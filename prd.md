# PRD: Talent Matching RAG Demo

**Document language:** English  
**Product UI language:** English  
**Stack:** Python, Streamlit, Chroma, DeepSeek API (OpenAI-compatible; default LLM)

---

## 1. Goal

Build a **demo RAG portal** for talent matching: given job openings and a pool of résumés, help hiring teams find which candidates best fit a role using semantic retrieval and LLM ranking—with **grounded evidence** (source passages from each CV).

**Success criteria**

- Clear pipeline: ingest jobs + CVs → embed → retrieve → LLM-ranked shortlist with reasons **and grounding**
- Local run with one command (or Docker) in ~5 minutes
- Ranked results always show source snippets (which CV section/chunk)
- Synthetic / anonymized demo data only (no real PII)

---

## 2. Problem statement

Hiring teams receive many CVs per opening. Keyword search misses synonyms and transferable skills; manual screening is slow and inconsistent. A talent-matching RAG layer retrieves and ranks candidates against a job description, with transparent **grounded** evidence the user can verify.

---

## 3. Users (demo)

| Role | Need |
|------|------|
| Hiring screener | Pick a job → ranked candidates + fit reasons + source passages |
| Technical reviewer | See architecture, stack, latency, grounding, guardrails |
| Presenter | Narrate chunking, embeddings, ranking, evaluation |

---

## 4. Scope

### In scope (MVP)

1. **Seed data:** several job openings and a synthetic résumé pool (the repo currently has 7 openings and 100 CVs, including a large IT cohort)  
2. **Ingestion:** Markdown (and optional PDF) → chunk → Chroma with metadata (`candidate_id`, fake name, `years_exp`, `location`, section)  
3. **Streamlit UI:** select/paste JD → optional filters → Find matches → top-N with scores, rationale, **grounding**  
4. **RAG:** embed query → retrieve k chunks → group by candidate → LLM rerank/explain  
5. **Grounding (required):** every ranked candidate shows cited CV passages (chunk text + section/source file); UI labels them as sources  
6. **Docs:** README + short demo script; optional `eval.py` hit@k

### Out of scope

Real ATS integration, live email ingest, bias dashboard, fine-tuned models, SSO, auto-reject emails

---

## 5. Functional requirements

### Data

- FR1: Load jobs from `data/jobs/*.md`  
- FR2: Load CVs from `data/cvs/*.{md,txt,pdf}`  
- FR3: `python -m app.ingest` rebuilds Chroma  
- FR4: First-run ingest or ship rebuildable index

### Matching

- FR5: Match by `job_id` or pasted JD; default top 5  
- FR6: Vector retrieval (optional hybrid later)  
- FR7: LLM structured output: `fit_score`, `strengths`, `gaps`, `evidence[]`  
- FR8: **Grounding:** each result lists source chunks (text, `source_path` / `section`, optional similarity); no claim without a citation  
- FR9: Hard filters (years, location) with filtered-out count

### UI (Streamlit)

- FR10: Job selector | results | candidate detail  
- FR11: “Why this match?” + **Sources / Grounding** panel per candidate  
- FR12: Toggle “Show retrieved chunks”  
- FR13: Footer: chat model, embedding model, latency (embed / retrieve / LLM)

---

## 6. Non-functional

- Python 3.11+, Chroma persistent dir, API key via `.env`  
- Synthetic data only; keys never committed  
- Mock ranking mode if no API key (for offline rehearsal)  
- MVP in 1–2 focused sessions

---

## 7. Architecture

```
[Jobs + CVs] → parse/chunk → embeddings → Chroma
                                              ↓
[Streamlit] JD → embed → retrieve k chunks → group by candidate
                                              ↓
                         LLM rerank + explain + grounded citations → UI
```

Thin custom RAG preferred (clarity for demos) over heavy frameworks.

---

## 8. Evaluation

- Golden set (5 queries → expected candidate IDs)  
- `eval.py`: hit@3 / hit@5  
- README: keyword vs RAG on 2 examples

---

## 9. Demo narrative (suggested)

1. Problem & pipeline  
2. Why RAG (not fine-tune) for matching  
3. Live: pick opening → shortlist → open **grounding**  
4. Limits: bias, hallucination, PII, human-in-the-loop  
5. Production path: ATS sync, eval harness, access control

---

## 10. Decisions (locked)

| Item | Choice |
|------|--------|
| UI | **Streamlit** |
| Language | **Python** |
| Vector DB | **Chroma** |
| Grounding | **Required** on ranked results |
| Default LLM | **DeepSeek** via `.env` (`DEEPSEEK_API_KEY`; OpenAI-compatible client). Optional `DEEPSEEK_BASE_URL` and model name. |

Resolved in the MVP: CV files may be Markdown, text, or PDF (text extraction). Offline mock ranking runs when `DEEPSEEK_API_KEY` is unset. Embeddings are local MiniLM, not a DeepSeek or OpenAI embedding API.

---

## 11. Acceptance checklist

- [ ] PRD agreed  
- [x] Seed jobs + synthetic CVs  
- [x] Ingest + Chroma works  
- [x] Portal returns ranked matches with **grounding**  
- [x] README + demo script  
- [x] Optional eval hit@k  
- [x] No real PII; API key via `.env`

---

## 12. Deliverables

| Artifact | Path |
|----------|------|
| PRD | `prd.md` |
| App | `app/` |
| Seed data | `data/jobs/`, `data/cvs/` |
| Demo script | `docs/DEMO.md` |
| README | `README.md` |
