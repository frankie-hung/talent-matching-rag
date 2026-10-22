# Talent Matching RAG

Demo portal for matching job openings to synthetic résumés with retrieval-augmented generation.

**Stack:** Python, Streamlit, and Chroma.

Product requirements are in [`prd.md`](prd.md).

Ranked results must include **grounding**: each candidate shows the source CV passages (chunk text and section) that support the match.

**DeepSeek** is the default LLM provider for this demo (OpenAI-compatible API). Implementation of the app is forthcoming.

## Seed data

Synthetic jobs and résumés live in [`data/`](data/README.md). Nothing in that folder is a real person or a real employer.

- Five openings: `data/jobs/*.md` (`job_id`, title, location, years, must-have skills, and a full description).
- 24 résumés: `data/cvs/*.md` (frontmatter `candidate_id`, `name`, `years_exp`, `location`, plus Summary, Experience, Skills, and Education). The pool mixes strong fits, partial fits, and poor fits.
- Optional eval labels: `data/golden.json` maps five queries to expected `candidate_id`s for a later hit@3 / hit@5 check.

When the app exists, `python -m app.ingest` loads `data/jobs` and `data/cvs` into Chroma. Do not put API keys in these files.

## Installation / Setup

### 1. Clone and install

Requires Python 3.11+.

```bash
git clone https://github.com/frankie-hung/talent-matching-rag.git
cd talent-matching-rag
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

`requirements.txt` is a minimal stub (`streamlit`, `chromadb`, the OpenAI-compatible client, and `httpx`) until the app is built.

### 2. Configure the API key

```bash
cp .env.example .env
```

Edit `.env` and set `DEEPSEEK_API_KEY`. `DEEPSEEK_BASE_URL` and the model name are optional; the example file has DeepSeek defaults.

Never commit `.env`. Only `.env.example` belongs in git.

### 3. Run (when the app exists)

These commands are placeholders until `app/` is implemented:

```bash
python -m app.ingest
streamlit run app/ui.py
```

Ingest rebuilds the Chroma index from seed jobs and CVs. The Streamlit UI then ranks matches. Every ranked candidate must show grounding (source CV passages).
