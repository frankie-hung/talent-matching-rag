"""Retrieve CV chunks, group by candidate, and rerank with DeepSeek or a mock."""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    deepseek_api_key,
    has_deepseek_key,
)
from app.embeddings import embed_query, embedding_model_label
from app.store import get_collection, index_count

_LOCATION_ALIASES = {
    "hk": "hong kong",
    "hong kong sar": "hong kong",
    "sg": "singapore",
}


@dataclass
class Evidence:
    chunk_id: str
    text: str
    section: str
    source_path: str
    similarity: float


@dataclass
class RankedCandidate:
    candidate_id: str
    name: str
    years_exp: int
    location: str
    fit_score: int
    strengths: list[str]
    gaps: list[str]
    evidence: list[Evidence]
    retrieved_chunks: list[Evidence]
    retrieval_similarity: float


@dataclass
class MatchResult:
    rankings: list[RankedCandidate]
    retrieved_candidates: int
    filtered_out: int
    mode: str
    chat_model: str
    embedding_model: str
    latency_embed_ms: float
    latency_retrieve_ms: float
    latency_llm_ms: float
    warnings: list[str] = field(default_factory=list)
    query_label: str = ""


@dataclass
class _Hit:
    evidence: Evidence
    candidate_id: str
    name: str
    years_exp: int
    location: str


@dataclass
class _PoolCandidate:
    candidate_id: str
    name: str
    years_exp: int
    location: str
    chunks: list[Evidence]

    @property
    def max_similarity(self) -> float:
        return max(chunk.similarity for chunk in self.chunks)


def _similarity(distance: float) -> float:
    # Chroma cosine space returns distance = 1 - cosine similarity.
    return 1.0 - float(distance)


def _location_matches(candidate_location: str, query: str) -> bool:
    needle = query.strip().casefold()
    if not needle:
        return True
    haystack = candidate_location.casefold()
    needle = _LOCATION_ALIASES.get(needle, needle)
    haystack = _LOCATION_ALIASES.get(haystack, haystack)
    return needle in haystack or haystack in needle


def _retrieve(query_embedding: list[float], k: int) -> list[_Hit]:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        raise RuntimeError("Chroma index is empty. Run python -m app.ingest")
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, count),
        include=["documents", "metadatas", "distances"],
    )
    hits: list[_Hit] = []
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    for text, meta, distance in zip(documents, metadatas, distances):
        meta = meta or {}
        candidate_id = str(meta.get("candidate_id") or "")
        hits.append(
            _Hit(
                evidence=Evidence(
                    chunk_id=str(meta.get("chunk_id") or ""),
                    text=text or "",
                    section=str(meta.get("section") or "Section"),
                    source_path=str(meta.get("source_path") or ""),
                    similarity=_similarity(distance),
                ),
                candidate_id=candidate_id,
                name=str(meta.get("name") or candidate_id),
                years_exp=int(meta.get("years_exp") or 0),
                location=str(meta.get("location") or ""),
            )
        )
    return hits


def _group(hits: list[_Hit]) -> list[_PoolCandidate]:
    grouped: dict[str, _PoolCandidate] = {}
    for hit in hits:
        if not hit.candidate_id:
            continue
        pool = grouped.get(hit.candidate_id)
        if pool is None:
            pool = _PoolCandidate(
                candidate_id=hit.candidate_id,
                name=hit.name,
                years_exp=hit.years_exp,
                location=hit.location,
                chunks=[],
            )
            grouped[hit.candidate_id] = pool
        pool.chunks.append(hit.evidence)
    pools = list(grouped.values())
    for pool in pools:
        pool.chunks.sort(key=lambda item: item.similarity, reverse=True)
    pools.sort(key=lambda item: item.max_similarity, reverse=True)
    return pools


def _heuristic(
    pool: _PoolCandidate, years_required: int | None
) -> tuple[int, list[str], list[str], list[Evidence]]:
    top = pool.chunks[0]
    score = int(round(max(0.0, min(1.0, top.similarity)) * 100))
    strengths = [
        (
            f"Closest CV passage is the {top.section} section "
            f"(similarity {top.similarity:.2f}). The source text is quoted in Sources."
        )
    ]
    gaps = []
    if years_required is not None and pool.years_exp < years_required:
        gaps.append(
            f"Résumé lists {pool.years_exp} years; this opening asks for {years_required}."
        )
    gaps.append(
        "Mock mode did not call DeepSeek, so skill gaps are not inferred beyond years and the passages shown."
    )
    return score, strengths, gaps, pool.chunks[:3]


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("Model JSON was not an object")
    return parsed


def _llm_rerank(
    jd_text: str,
    pools: list[_PoolCandidate],
    years_required: int | None,
) -> tuple[list[dict], str]:
    from openai import OpenAI

    catalogue = []
    for pool in pools:
        catalogue.append(
            {
                "candidate_id": pool.candidate_id,
                "name": pool.name,
                "years_exp": pool.years_exp,
                "location": pool.location,
                "passages": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "section": chunk.section,
                        "source_path": chunk.source_path,
                        "similarity": round(chunk.similarity, 3),
                        "text": chunk.text[:700],
                    }
                    for chunk in pool.chunks[:3]
                ],
            }
        )
    years_note = (
        f"The opening prefers at least {years_required} years."
        if years_required is not None
        else "No minimum years was supplied."
    )
    system = (
        "You rank synthetic résumés for a hiring demo. Use only the CV passages provided. "
        "Do not invent employers, skills, years, or quotations. "
        "Every candidate needs at least one evidence_chunk_id copied from that candidate's passages. "
        "Return JSON only."
    )
    user = (
        f"{years_note}\n\n"
        "Job description:\n"
        f"{jd_text[:6000]}\n\n"
        "Candidates:\n"
        f"{json.dumps(catalogue, ensure_ascii=False)}\n\n"
        "Return an object with key candidates: a list of every candidate_id above. "
        "Each item has candidate_id, fit_score (integer 0-100), strengths (short strings), "
        "gaps (short strings), evidence_chunk_ids (chunk ids from that candidate only). "
        "Order the list best fit first."
    )
    client = OpenAI(api_key=deepseek_api_key(), base_url=DEEPSEEK_BASE_URL, timeout=60.0)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.2,
        )
    content = response.choices[0].message.content or ""
    return _extract_json(content).get("candidates") or [], content


def _from_llm(
    pools: list[_PoolCandidate], payload: list[dict], years_required: int | None
) -> list[RankedCandidate]:
    by_id = {pool.candidate_id: pool for pool in pools}
    ranked: list[RankedCandidate] = []
    seen: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            continue
        candidate_id = str(item.get("candidate_id") or "")
        pool = by_id.get(candidate_id)
        if pool is None or candidate_id in seen:
            continue
        seen.add(candidate_id)
        chunk_by_id = {chunk.chunk_id: chunk for chunk in pool.chunks}
        cited: list[Evidence] = []
        for chunk_id in item.get("evidence_chunk_ids") or []:
            evidence = chunk_by_id.get(str(chunk_id))
            if evidence is not None and evidence not in cited:
                cited.append(evidence)
        if not cited:
            cited = pool.chunks[:3]
        strengths = [str(value) for value in (item.get("strengths") or []) if str(value).strip()]
        gaps = [str(value) for value in (item.get("gaps") or []) if str(value).strip()]
        if not strengths:
            _score, strengths, extra_gaps, _evidence = _heuristic(pool, years_required)
            gaps = gaps or extra_gaps
        try:
            score = int(round(float(item.get("fit_score"))))
        except (TypeError, ValueError):
            score = int(round(max(0.0, min(1.0, pool.max_similarity)) * 100))
        score = max(0, min(100, score))
        ranked.append(
            RankedCandidate(
                candidate_id=pool.candidate_id,
                name=pool.name,
                years_exp=pool.years_exp,
                location=pool.location,
                fit_score=score,
                strengths=strengths[:5],
                gaps=gaps[:5],
                evidence=cited[:4],
                retrieved_chunks=list(pool.chunks),
                retrieval_similarity=pool.max_similarity,
            )
        )
    for pool in pools:
        if pool.candidate_id in seen:
            continue
        score, strengths, gaps, evidence = _heuristic(pool, years_required)
        gaps = ["The model omitted this candidate; the score falls back to retrieval similarity."] + gaps
        ranked.append(
            RankedCandidate(
                candidate_id=pool.candidate_id,
                name=pool.name,
                years_exp=pool.years_exp,
                location=pool.location,
                fit_score=score,
                strengths=strengths,
                gaps=gaps[:5],
                evidence=evidence,
                retrieved_chunks=list(pool.chunks),
                retrieval_similarity=pool.max_similarity,
            )
        )
    ranked.sort(key=lambda item: (item.fit_score, item.retrieval_similarity), reverse=True)
    return ranked


def _ensure_grounding(rankings: list[RankedCandidate]) -> None:
    for candidate in rankings:
        if not candidate.evidence:
            candidate.evidence = candidate.retrieved_chunks[:3]
        for evidence in candidate.evidence:
            if not evidence.text.strip() or not evidence.source_path or not evidence.section:
                raise RuntimeError(
                    f"Missing grounding for {candidate.candidate_id}: {evidence.chunk_id}"
                )


def match_candidates(
    jd_text: str,
    *,
    top_n: int = 5,
    min_years: int = 0,
    location_contains: str = "",
    years_required: int | None = None,
    retrieve_k: int = 48,
    pool_size: int = 8,
    query_label: str = "",
    query_lead: str | None = None,
    force_mock: bool = False,
) -> MatchResult:
    if not jd_text.strip():
        raise ValueError("Job description is empty")
    top_n = max(1, min(10, int(top_n)))
    warnings: list[str] = []

    started = time.perf_counter()
    query_embedding = embed_query(jd_text, lead=query_lead)
    embed_ms = (time.perf_counter() - started) * 1000

    started = time.perf_counter()
    evidences = _retrieve(query_embedding, retrieve_k)
    pools = _group(evidences)
    retrieve_ms = (time.perf_counter() - started) * 1000

    retrieved_candidates = len(pools)
    kept: list[_PoolCandidate] = []
    filtered_out = 0
    for pool in pools:
        if min_years and pool.years_exp < min_years:
            filtered_out += 1
            continue
        if not _location_matches(pool.location, location_contains):
            filtered_out += 1
            continue
        kept.append(pool)

    shortlist = kept[: max(top_n, pool_size)]
    mode = "mock"
    chat_model = f"{DEEPSEEK_MODEL} (mock — no API key)"
    llm_ms = 0.0
    rankings: list[RankedCandidate] = []

    use_llm = has_deepseek_key() and not force_mock and bool(shortlist)
    if use_llm:
        started = time.perf_counter()
        try:
            payload, _raw = _llm_rerank(jd_text, shortlist, years_required)
            rankings = _from_llm(shortlist, payload, years_required)
            mode = "deepseek"
            chat_model = DEEPSEEK_MODEL
        except Exception as exc:
            warnings.append(f"DeepSeek call failed ({exc.__class__.__name__}). Showing mock ranking.")
            rankings = []
        llm_ms = (time.perf_counter() - started) * 1000

    if not rankings:
        built: list[RankedCandidate] = []
        for pool in shortlist:
            score, strengths, gaps, evidence = _heuristic(pool, years_required)
            built.append(
                RankedCandidate(
                    candidate_id=pool.candidate_id,
                    name=pool.name,
                    years_exp=pool.years_exp,
                    location=pool.location,
                    fit_score=score,
                    strengths=strengths,
                    gaps=gaps,
                    evidence=evidence,
                    retrieved_chunks=list(pool.chunks),
                    retrieval_similarity=pool.max_similarity,
                )
            )
        rankings = built
        if not use_llm:
            llm_ms = 0.0

    rankings = rankings[:top_n]
    _ensure_grounding(rankings)
    return MatchResult(
        rankings=rankings,
        retrieved_candidates=retrieved_candidates,
        filtered_out=filtered_out,
        mode=mode,
        chat_model=chat_model,
        embedding_model=embedding_model_label(),
        latency_embed_ms=embed_ms,
        latency_retrieve_ms=retrieve_ms,
        latency_llm_ms=llm_ms,
        warnings=warnings,
        query_label=query_label,
    )


def main() -> None:
    import argparse

    from app.documents import load_jobs

    parser = argparse.ArgumentParser(description="Rank candidates for one opening")
    parser.add_argument("--job", required=True, help="job_id from data/jobs")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--min-years", type=int, default=0)
    parser.add_argument("--location", default="")
    parser.add_argument("--mock", action="store_true", help="Skip DeepSeek even if a key is set")
    args = parser.parse_args()
    if index_count() == 0:
        raise SystemExit("No index. Run python -m app.ingest")
    jobs = {job.job_id: job for job in load_jobs()}
    if args.job not in jobs:
        raise SystemExit(f"Unknown job_id {args.job}. Known: {', '.join(jobs)}")
    job = jobs[args.job]
    result = match_candidates(
        job.query_text(),
        top_n=args.top_n,
        min_years=args.min_years,
        location_contains=args.location,
        years_required=job.years_required,
        query_label=job.title,
        query_lead=job.embedding_lead(),
        force_mock=args.mock,
    )
    print(f"mode={result.mode} chat={result.chat_model}")
    print(
        f"retrieved={result.retrieved_candidates} filtered_out={result.filtered_out} "
        f"embed_ms={result.latency_embed_ms:.0f} retrieve_ms={result.latency_retrieve_ms:.0f} "
        f"llm_ms={result.latency_llm_ms:.0f}"
    )
    for warning in result.warnings:
        print(f"warning: {warning}")
    for index, candidate in enumerate(result.rankings, start=1):
        print(
            f"{index}. {candidate.candidate_id} {candidate.name} "
            f"score={candidate.fit_score} years={candidate.years_exp} loc={candidate.location}"
        )
        for evidence in candidate.evidence:
            preview = evidence.text.replace("\n", " ")[:140]
            print(
                f"   - [{evidence.section}] {evidence.source_path} "
                f"sim={evidence.similarity:.2f} {preview}"
            )


if __name__ == "__main__":
    main()
