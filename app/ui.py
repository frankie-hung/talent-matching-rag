"""Streamlit portal: pick a role, rank candidates, show grounded CV passages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.config import DEEPSEEK_MODEL, has_deepseek_key
from app.documents import Job, load_jobs
from app.embeddings import embedding_model_label
from app.match import MatchResult, RankedCandidate, match_candidates
from app.store import index_count

st.set_page_config(page_title="Talent matching", layout="wide")
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.25rem; max-width: 1180px; }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(28, 25, 23, 0.08); }
    </style>
    """,
    unsafe_allow_html=True,
)


def _jobs() -> list[Job]:
    return load_jobs()


def _section(title: str, badge: str) -> None:
    st.markdown(f"### {title} {badge}")


def _render_explanation(candidate: RankedCandidate, mode: str) -> None:
    if mode == "deepseek":
        badge = ":violet-badge[DeepSeek · External LLM]"
        note = (
            "DeepSeek wrote these strengths and gaps. "
            "It did not write the CV quotes in Sources / Grounding."
        )
    else:
        badge = ":gray-badge[Mock explanation · No LLM]"
        note = (
            "No API key, so DeepSeek did not run. "
            "This text is a local heuristic that points at retrieved passages."
        )
    with st.container(border=True):
        _section("Why this match", badge)
        st.caption(note)
        for strength in candidate.strengths:
            st.markdown(f"- {strength}")
        if candidate.gaps:
            st.markdown("#### Gaps")
            for gap in candidate.gaps:
                st.markdown(f"- {gap}")


def _render_evidence(chunks: list, title: str, badge: str, note: str) -> None:
    with st.container(border=True):
        _section(title, badge)
        st.caption(note)
        if not chunks:
            st.warning("No source passage was attached. This result is incomplete.")
            return
        for index, evidence in enumerate(chunks):
            st.caption(
                f"{evidence.section} · `{evidence.source_path}` · "
                f"local cosine similarity {evidence.similarity:.2f}"
            )
            st.markdown(evidence.text)
            if index < len(chunks) - 1:
                st.divider()


def _footer(result: MatchResult | None) -> None:
    st.divider()
    if result is None:
        embed_ms = retrieve_ms = llm_ms = "—"
        chat = DEEPSEEK_MODEL if has_deepseek_key() else f"{DEEPSEEK_MODEL} (mock — no API key)"
    else:
        embed_ms = f"{result.latency_embed_ms:.0f} ms"
        retrieve_ms = f"{result.latency_retrieve_ms:.0f} ms"
        llm_ms = f"{result.latency_llm_ms:.0f} ms"
        chat = result.chat_model
    left, middle, right = st.columns(3)
    left.metric("Embed", embed_ms)
    middle.metric("Retrieve", retrieve_ms)
    right.metric("LLM", llm_ms)
    st.caption(f"Chat model: {chat} · Embedding model: {embedding_model_label()}")


def main() -> None:
    st.title("Talent matching")
    st.caption(
        "Synthetic résumés only. Every ranked candidate includes grounding: "
        "the CV passage, section, and source file the match came from."
    )

    count = index_count()
    if count == 0:
        st.error("No Chroma index yet. From the repo root run `python -m app.ingest`, then reload.")
        _footer(None)
        return

    jobs = _jobs()
    by_id = {job.job_id: job for job in jobs}

    with st.sidebar:
        st.header("Role")
        job_id = st.selectbox(
            "Opening",
            options=[job.job_id for job in jobs],
            format_func=lambda value: f"{by_id[value].title}",
        )
        job = by_id[job_id]
        st.caption(
            f"{job.location} · {job.years_required}+ years · `{job.source_path}`"
        )
        with st.expander("Job description"):
            st.markdown(job.body)
        pasted = st.text_area(
            "Or paste a job description",
            height=160,
            placeholder="Leave empty to use the selected opening.",
        )
        st.header("Filters")
        min_years = st.number_input(
            "Minimum years of experience",
            min_value=0,
            max_value=40,
            value=0,
            help="0 keeps everyone the retriever returned. Candidates below the bar are counted as filtered out.",
        )
        location = st.text_input(
            "Location contains",
            placeholder="Hong Kong, Remote, Singapore",
        )
        top_n = st.slider("Top N", min_value=1, max_value=10, value=5)
        show_chunks = st.toggle("Show retrieved chunks", value=False)
        find = st.button("Find matches", type="primary", use_container_width=True)

    if not has_deepseek_key():
        st.info(
            "Mock ranking is on. Vectors still retrieve CV passages. "
            "Set DEEPSEEK_API_KEY in `.env` for DeepSeek rerank and written strengths."
        )

    if find:
        jd_text = pasted.strip() or job.query_text()
        label = "Pasted job description" if pasted.strip() else job.title
        years_required = None if pasted.strip() else job.years_required
        with st.spinner("Embedding the role and reading matching passages…"):
            try:
                st.session_state["result"] = match_candidates(
                    jd_text,
                    top_n=int(top_n),
                    min_years=int(min_years),
                    location_contains=location,
                    years_required=years_required,
                    query_label=label,
                    query_lead=None if pasted.strip() else job.embedding_lead(),
                )
            except Exception as exc:
                st.session_state["result"] = None
                st.error(str(exc))

    result: MatchResult | None = st.session_state.get("result")
    if result is None:
        st.markdown("Choose an opening and press **Find matches**.")
        _footer(None)
        return

    for warning in result.warnings:
        st.warning(warning)

    st.markdown(f"**{result.query_label}**")
    st.caption(
        f"Retrieved {result.retrieved_candidates} candidates · "
        f"filtered out {result.filtered_out} · "
        f"showing {len(result.rankings)} · mode `{result.mode}`"
    )

    if not result.rankings:
        st.warning("No candidates left after filters. Relax years or location and search again.")
        _footer(result)
        return

    list_col, detail_col = st.columns([1, 1.35], gap="large")
    labels = [
        f"{item.name}  ·  {item.fit_score}  ·  {item.location}"
        for item in result.rankings
    ]
    with list_col:
        st.subheader("Results")
        if result.mode == "deepseek":
            st.caption(
                "Shortlist order uses DeepSeek fit scores. "
                "Retrieval similarity on each card is local (embeddings / Chroma)."
            )
        else:
            st.caption(
                "Local retrieval only. Order and fit scores come from embedding similarity, not an LLM."
            )
        st.caption(
            "Fit on each line is overall fit, about 0–100 (higher is better), separate from similarity. "
            "Years and location are inferred signals from the résumé."
        )
        selected = st.radio(
            "Shortlist",
            options=list(range(len(result.rankings))),
            format_func=lambda index: labels[index],
            label_visibility="collapsed",
        )
        for index, candidate in enumerate(result.rankings, start=1):
            st.markdown(
                f"**{index}. {candidate.name}**  \n"
                f"Fit {candidate.fit_score} · {candidate.years_exp} years · {candidate.location}"
            )
    candidate = result.rankings[int(selected)]
    with detail_col:
        st.subheader("Candidate detail")
        st.markdown(f"### {candidate.name}")
        st.caption(
            f"`{candidate.candidate_id}` · {candidate.years_exp} years · {candidate.location}. "
            "Years and location are inferred signals from the résumé."
        )
        sim_col, fit_col = st.columns(2)
        sim_col.metric(
            "Retrieval similarity",
            f"{candidate.retrieval_similarity:.2f}",
            border=True,
            help=(
                "Cosine similarity, not cosine distance. About 0–1. "
                "Higher is a closer match. About 0.75+ is a strong match."
            ),
        )
        sim_col.caption(
            "Cosine similarity, not distance. About 0–1; higher is closer. ~0.75+ is strong."
        )
        fit_col.metric(
            "Fit",
            candidate.fit_score,
            border=True,
            help="Overall fit, about 0–100. Higher is a better fit. Separate from similarity.",
        )
        fit_col.caption("Overall fit, about 0–100. Higher is better. Separate from similarity.")
        st.markdown(":green-badge[Local retrieval]")
        if result.mode == "deepseek":
            st.caption("Similarity is the local embedding match. Fit is DeepSeek’s overall score.")
        else:
            st.caption("Similarity is the local embedding match. No LLM ran.")
        _render_explanation(candidate, result.mode)
        _render_evidence(
            candidate.evidence,
            "Sources / Grounding",
            ":green-badge[Local · CV text]",
            "Quoted text is copied from the résumé. The model does not write these passages.",
        )
        if show_chunks:
            _render_evidence(
                candidate.retrieved_chunks,
                "All retrieved chunks",
                ":green-badge[Local retrieval]",
                "Every passage Chroma returned for this person, before the explanation was written.",
            )

    _footer(result)


if __name__ == "__main__":
    main()
