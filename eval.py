"""Hit@k against data/golden.json, plus a keyword baseline on the same labels.

A hit at k means at least one expected candidate id appears in the top k.
Run from the repo root after `python -m app.ingest`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict

from app.config import GOLDEN_PATH
from app.documents import all_chunks, load_jobs
from app.match import match_candidates
from app.store import index_count

_STOP = {
    "the",
    "and",
    "for",
    "with",
    "who",
    "has",
    "this",
    "that",
    "from",
    "into",
    "are",
    "was",
    "not",
    "but",
    "per",
    "via",
    "you",
    "your",
    "have",
    "been",
    "their",
    "than",
    "then",
    "only",
    "each",
    "about",
}


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9+#]+", text.casefold())
        if len(token) > 2 and token not in _STOP
    ]


def keyword_rank(query: str, top_n: int = 5) -> list[str]:
    """Rank candidate ids by overlap with query terms across CV chunks."""
    terms = _tokens(query)
    scores: dict[str, int] = defaultdict(int)
    seen_terms: dict[str, set[str]] = defaultdict(set)
    for chunk in all_chunks():
        haystack = set(_tokens(f"{chunk.section}\n{chunk.text}"))
        for term in terms:
            if term in haystack and term not in seen_terms[chunk.candidate_id]:
                seen_terms[chunk.candidate_id].add(term)
                scores[chunk.candidate_id] += 1
    ordered = sorted(scores, key=lambda candidate_id: scores[candidate_id], reverse=True)
    return ordered[:top_n]


def hit_at(ranked_ids: list[str], expected: list[str], k: int) -> int:
    return int(any(candidate_id in expected for candidate_id in ranked_ids[:k]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval against data/golden.json")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force heuristic ranking even if DEEPSEEK_API_KEY is set",
    )
    args = parser.parse_args()
    if index_count() == 0:
        raise SystemExit("No Chroma index. Run: python -m app.ingest")

    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    jobs = {job.job_id: job for job in load_jobs()}
    hit3 = []
    hit5 = []
    keyword_hit3 = []
    keyword_hit5 = []
    print("query\thit@3\thit@5\tkeyword_hit@3\tkeyword_hit@5\ttop_ids")
    for item in golden["queries"]:
        job = jobs[item["job_id"]]
        result = match_candidates(
            job.query_text(),
            top_n=max(args.top_n, 5),
            years_required=job.years_required,
            query_label=job.title,
            query_lead=job.embedding_lead(),
            force_mock=args.mock,
        )
        ranked = [candidate.candidate_id for candidate in result.rankings]
        expected = item["expected_candidate_ids"]
        keyword_ids = keyword_rank(job.query_text(), top_n=5)
        row_hit3 = hit_at(ranked, expected, 3)
        row_hit5 = hit_at(ranked, expected, 5)
        key3 = hit_at(keyword_ids, expected, 3)
        key5 = hit_at(keyword_ids, expected, 5)
        hit3.append(row_hit3)
        hit5.append(row_hit5)
        keyword_hit3.append(key3)
        keyword_hit5.append(key5)
        print(
            f"{item['query_id']}\t{row_hit3}\t{row_hit5}\t{key3}\t{key5}\t{','.join(ranked[:5])}"
        )
        print(f"  keyword {item['query_id']}: {','.join(keyword_ids)}")
        for candidate in result.rankings:
            if not candidate.evidence or not candidate.evidence[0].text.strip():
                raise SystemExit(f"Missing grounding for {candidate.candidate_id}")

    n = len(hit3)
    print(
        f"mean hit@3={sum(hit3) / n:.2f} hit@5={sum(hit5) / n:.2f} "
        f"keyword hit@3={sum(keyword_hit3) / n:.2f} keyword hit@5={sum(keyword_hit5) / n:.2f} "
        f"mode={'mock' if args.mock else 'auto'}"
    )


if __name__ == "__main__":
    main()
