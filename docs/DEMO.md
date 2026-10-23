# Demo script

Five minutes. Synthetic data only. Do not paste a real résumé or a live API key into the UI.

## Before you start

```bash
source .venv/bin/activate
python -m app.ingest
streamlit run app/ui.py
```

If `.env` has no `DEEPSEEK_API_KEY`, say so: retrieval is real, the written “why” is the mock heuristic, and every card still quotes a CV passage. With a key, DeepSeek reranks and the footer shows the chat model and the LLM latency.

## 1. Problem and pipeline

Hiring teams drown in CVs. Keyword search misses paraphrases (“retrieval assistant” versus “RAG”) and over-ranks lookalikes (an accountant who “reports”, a recruiter filed under HR).

Point at the pipeline: jobs and CVs in `data/` are chunked by section, embedded locally with MiniLM, stored in Chroma, then grouped back to a person. The model may explain. The passage on screen is copied from the file.

## 2. Why retrieval instead of a fine-tune

The corpus is a few dozen synthetic résumés and it changes whenever someone drops in a Markdown file. Re-ingest is `python -m app.ingest`. Nothing here is worth a training run, and a fine-tune would not show the sentence that justified the rank.

## 3. Live shortlist and grounding

1. Select **AI / ML Engineer**. Leave the paste box empty. Top N stays at 5. Press **Find matches**.
2. Read the results column, then the detail pane. **Why this match?** is the claim. **Sources / Grounding** is the CV text, the section name, and the path under `data/cvs/`.
3. Turn on **Show retrieved chunks** and show that the panel can list every passage retrieved for that person, not only the ones cited.
4. Optional filter: type `Hong Kong` into **Location contains** and search again. People whose location line does not mention Hong Kong drop out, and the caption reports how many were filtered out. Clear the box before the next search.
5. Paste a one-paragraph description of a payments product manager over the Product Manager opening and search again, so the audience sees match-by-text as well as match-by-opening.
6. If you want the larger IT pool, switch to **Backend Software Engineer** or **DevOps / Site Reliability Engineer**. The shortlist should cite Go or Java services, or Kubernetes and Terraform, from `data/cvs/`.

## 4. Limits

- The ranker can still sound confident. The quote is the check. If the quote does not support the sentence, the sentence is wrong.
- Years and location filters are blunt. They are not a fairness review.
- Names and employers in this repo are fictional. A production system needs an access boundary and a rule about real CVs.
- Mock mode will not invent skill gaps. That is deliberate.

## 5. What production would add

An ATS feed, a held-out eval that is not this toy `golden.json`, and a person who can reject the shortlist. `python eval.py` prints hit@3 and hit@5 for the five labelled openings, next to a keyword overlap baseline.

Close on the footer: chat model, local embedding model, and embed / retrieve / LLM milliseconds.
