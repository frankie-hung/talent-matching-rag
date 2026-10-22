---
candidate_id: cand-ml-01
name: Mei-Ling Chan
years_exp: 6
location: Hong Kong
---

# Mei-Ling Chan

## Summary

Machine learning engineer in Hong Kong with six years taking models from a labelled sample to a service other teams call. Most recent work is a policy-search assistant that retrieves internal passages and refuses to answer when retrieval is empty. Comfortable in PyTorch, SQL, and a plain Python service. Prefers a written evaluation set over a single accuracy number.

## Experience

### Machine Learning Engineer, Harbourline Digital Bank (fictional)
Hong Kong — 2022 to present

- Trained a bilingual text classifier for card-dispute reasons in PyTorch. Replaced a keyword ruleset that missed paraphrases such as “merchant never delivered” versus “item not received”.
- Built a retrieval pipeline over policy manuals: chunked documents, embedded passages, and returned the source section with every draft answer so reviewers could check the citation.
- Added a batch monitor that compares weekly score distributions with the training slice and pages the on-call channel when a product code drifts.
- Wrote SQL to build the training frame from the warehouse, including a deduplicated customer key that analytics had been double-counting.
- Documented model limits for model risk: slices with too little Cantonese text, and cases where the assistant must hand off to a human.

### Data Scientist, Peakform Logistics (fictional)
Hong Kong — 2019 to 2022

- Shipped an ETA regression for cross-border trucking. The model ran as a nightly batch, and planners saw a confidence band rather than a point they could not question.
- Maintained feature jobs in Python and SQL. Chased a leakage bug where the label timestamp was earlier than a “current location” feature.
- Partnered with operations research on a smaller ranking model for which warehouse should fulfil an order. Took it as far as an offline evaluation and a shadow run.

## Skills

- Python, PyTorch, scikit-learn, sentence embeddings, vector search
- SQL, experiment tracking, FastAPI-style model services
- Evaluation design, error slices, grounded citations for retrieved text
- Spoken Cantonese, written English

## Education

BSc Computer Science, City University of Hong Kong (fictional degree path, 2019)
