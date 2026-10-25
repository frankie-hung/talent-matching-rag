# Talent Matching RAG

Demo portal for matching job openings to synthetic résumés with retrieval-augmented generation.

**Stack:** Python, Streamlit, and Chroma. **DeepSeek** is the default chat model when `DEEPSEEK_API_KEY` is set. Embeddings stay on the machine (`BAAI/bge-base-en-v1.5` via ONNX). DeepSeek does not serve that embedding model, and this demo does not call OpenAI.

Product requirements are in [`prd.md`](prd.md). A presenter script is in [`docs/DEMO.md`](docs/DEMO.md).

Ranked results must include **grounding**: each candidate shows the source CV passage, the section, and the file path. The quoted text is copied from the résumé, not written by the model.

Without an API key the app still runs. It retrieves by vectors and fills “Why this match?” with a heuristic that points at those passages. Mock mode does not invent skill gaps.

## Run

Python 3.11+. From the repo root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.ingest
streamlit run app/ui.py
```

On Windows, activate with `.venv\Scripts\activate`.

Then open the URL Streamlit prints (usually http://localhost:8501). Pick an opening, leave the paste box empty, and press **Find matches**. The detail pane has three blocks: **Why this match** (a DeepSeek badge when a key is set, otherwise **Mock explanation · No LLM**), **Sources / Grounding** (CV quotes from local retrieval), and, when the toggle is on, **All retrieved chunks** (also local). The footer shows the chat model, the embedding model, and embed / retrieve / LLM latency.

`python -m app.ingest` rebuilds Chroma from `data/jobs` and `data/cvs`. The first run downloads the BGE ONNX weights (about 210 MB) into the user cache. Later runs reuse them. The index lives in `.chroma/`, which is gitignored. Re-run ingest after changing the embedding model. An index built with another model will not match.

Leave `DEEPSEEK_API_KEY` blank to stay in mock mode. To use DeepSeek later, put the key only in `.env` and restart Streamlit. Optional settings: `DEEPSEEK_BASE_URL` (default `https://api.deepseek.com`) and `DEEPSEEK_MODEL` (default `deepseek-chat`, DeepSeek Pro). Never commit `.env`.

Set the embedding model explicitly on a machine that already has a `.env`:

```bash
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
```

That is the sentence-transformers model id. The app loads it locally. No embedding API key is required.

A terminal shortlist, still mocked, without starting the UI:

```bash
python -m app.match --job job-ai-ml --mock
```

Hit@3 / hit@5 against `data/golden.json`, plus a keyword-overlap baseline on the same job text:

```bash
python eval.py --mock
```

A hit means at least one labelled candidate id appears in the top k.

## Seed data

Synthetic only. Details and the fit matrix are in [`data/README.md`](data/README.md).

- Seven openings in `data/jobs/*.md`
- 100 résumés in `data/cvs/*.md` (Markdown, plus `.txt` and `.pdf` if you add them). After pulling new CVs, rebuild the index with `python -m app.ingest`.
- `data/golden.json` for the eval labels

## Keyword overlap and vector retrieval

The demo can rank people in two ways. **Keyword overlap** counts shared words between the job text and each résumé. **Vector retrieval** compares meaning, so similar wording can match even when the exact words differ.

`data/golden.json` labels seven openings with the people who should count as a real fit. **hit@5** scores each opening separately: it succeeds when at least one of those expected people appears in the top 5. A score of **1.0** means all seven openings succeeded (7/7). It does not mean every good fit was ranked first.

On this sample, both methods currently score 1.0. They still get there by different mistakes:

- Paste `HR Hong Kong` and search. The keyword method ignores any word of two letters or fewer, so it throws away “HR” and mostly matches “Hong Kong”. Analysts based in Hong Kong then rank above the HR business partners. Vector retrieval still starts with Fiona Leung (`cand-hr-01`). Her **Sources / Grounding** quotes are employee-relations work.
- Select **Data Analyst**. Keyword overlap on the full job text keeps the four analysts ahead of the accountant. Vector retrieval can still place Samuel Adeyemi (`cand-xx-03`) on the shortlist, because “reporting” and a management pack sit close to analyst language. Open **Sources / Grounding**: the quoted lines are ledger commentary. That is the point of grounding. A near-miss can look like a fit until you read the CV passage the rank came from.

## What the screen does

The sidebar is the job selector, an optional pasted description, years and location filters, top N, and the chunk toggle. Results are the shortlist. Candidate detail is the claim, the gaps, and the source passages. Filters report how many retrieved people were removed. Claims are only as good as the quote underneath them.
