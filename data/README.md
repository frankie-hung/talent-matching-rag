# Seed data

Synthetic demo data only. Names, employers, and openings are fictional. Do not add real résumés, real employee records, or live API keys.

Ingest (when `app/` exists) reads:

- Jobs: `data/jobs/*.md`
- CVs: `data/cvs/*.md`

`python -m app.ingest` rebuilds the Chroma index from these files. Ranked matches must still show **grounding** (the CV passage and section that support the claim).

## Jobs

| job_id | Title | Location | Years |
|--------|--------|----------|-------|
| `job-ai-ml` | AI / ML Engineer | Hong Kong (hybrid, Quarry Bay) | 3 |
| `job-data-analyst` | Data Analyst | Hong Kong (hybrid, Kwun Tong) | 2 |
| `job-product-manager` | Product Manager | Hong Kong (hybrid, Sheung Wan) | 4 |
| `job-hrbp` | HR Business Partner | Hong Kong (on-site, Central) | 5 |
| `job-it-support` | IT Support / Systems Administrator | Hong Kong (on-site, Tsim Sha Tsui) | 2 |

Each file has YAML frontmatter (`job_id`, `title`, `location`, `years_required`, `must_have_skills`) and a full job description. Wording is paraphrased in the style of a public posting, not copied from a live listing.

## CVs

24 Markdown résumés. Frontmatter: `candidate_id`, `name`, `years_exp`, `location`. Body sections: Summary, Experience, Skills, Education.

The pool mixes strong fits, partial fits, and poor fits so retrieval can be wrong in interesting ways (for example an accountant who “reports”, a program manager who is not a product manager, a recruiter who is not an HR business partner).

| candidate_id | Name | Years | Location | Best-fit note |
|--------------|------|-------|----------|----------------|
| `cand-ml-01` | Mei-Ling Chan | 6 | Hong Kong | Strong AI / ML, including grounded retrieval |
| `cand-ml-02` | Arjun Mehta | 4 | Remote (APAC) | Strong NLP / ML |
| `cand-ml-03` | Sofia Alvarez | 2 | Hong Kong | Partial ML (under years); some analyst work |
| `cand-ml-04` | Kenji Watanabe | 8 | Singapore | Strong ML platform; less applied modelling |
| `cand-da-01` | Priya Nair | 5 | Hong Kong | Strong data analyst |
| `cand-da-02` | Oscar Lam | 3 | Hong Kong (hybrid) | Strong data analyst |
| `cand-da-03` | Hannah Brooks | 4 | Remote (APAC) | Partial analyst (marketing measurement) |
| `cand-da-04` | Wei Zhang | 7 | Hong Kong | Partial analyst (analytics engineering) |
| `cand-pm-01` | Jordan Hale | 7 | Hong Kong | Strong product manager |
| `cand-pm-02` | Aisha Rahman | 5 | Hong Kong | Strong product manager |
| `cand-pm-03` | Tom Ng | 3 | Hong Kong | Partial PM (under years) |
| `cand-pm-04` | Elena Petrova | 9 | Remote (APAC) | Poor PM fit (program manager) |
| `cand-hr-01` | Fiona Leung | 8 | Hong Kong | Strong HR business partner |
| `cand-hr-02` | Daniel Okonkwo | 6 | Hong Kong | Strong HR business partner |
| `cand-hr-03` | Chloe Tan | 4 | Singapore | Partial HR (recruiting only) |
| `cand-hr-04` | Grace Wong | 7 | Hong Kong | Partial HRBP (learning-heavy) |
| `cand-it-01` | Marcus Bell | 6 | Hong Kong | Strong IT support / systems admin |
| `cand-it-02` | Yuki Sato | 3 | Hong Kong | Strong IT support |
| `cand-it-03` | Liam O'Connor | 5 | Remote (APAC) | Partial IT (network engineer) |
| `cand-it-04` | Nora Ibrahim | 1 | Hong Kong | Poor IT fit (under years) |
| `cand-xx-01` | Benito Cruz | 12 | Hong Kong | Poor fit (hotel operations) |
| `cand-xx-02` | Camille Dubois | 6 | Remote (APAC) | Poor fit (brand design) |
| `cand-xx-03` | Samuel Adeyemi | 9 | Hong Kong | Poor fit (financial accountant) |
| `cand-xx-04` | Rita Cheung | 11 | Hong Kong | Poor fit (corporate counsel) |

## Golden set

`data/golden.json` has five queries, one per opening. `expected_candidate_ids` is the relevant set for a later `eval.py` hit@3 / hit@5: a hit means at least one of those ids appears in the top k. Order is best-first, but hit rate treats the list as a set. `partial_candidate_ids` are plausible near-misses and are not required for a hit.
