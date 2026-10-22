# Talent Matching RAG

Demo portal for matching job openings to synthetic résumés with retrieval-augmented generation.

**Stack:** Python, Streamlit, and Chroma.

Product requirements are in [`prd.md`](prd.md).

Ranked results must include **grounding**: each candidate shows the source CV passages (chunk text and section) that support the match.

**DeepSeek** is the default LLM provider for this demo (OpenAI-compatible API). Implementation of the app is forthcoming.

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
