---
candidate_id: cand-se-13
name: Denis Kwan
years_exp: 7
location: Hong Kong
---

# Denis Kwan

## Summary

Backend engineer in Hong Kong, seven years, focused on high-volume read APIs rather than ledgers. Go, Redis, and PostgreSQL. Good at latency budgets and load tests. Has done on-call. Money-movement experience is limited to reading a payments service someone else owned.

## Experience


### Senior Backend Engineer, Sampan Networks (fictional)
Hong Kong — 2020 to present

- Rebuilt a public read API in Go. p99 dropped after the hot path stopped joining five tables and started reading a maintained projection.
- Put a Redis cache in front of catalogue reads with an explicit stampede lock. Documented what is allowed to be stale.
- Ran load tests before campaign weekends. The test, not production, found the connection-pool leak.
- On-call for the read path. Writes a short note when a cache flush was the wrong lever.
### Software Engineer, Island Cache (fictional)
Hong Kong — 2018 to 2020

- Maintained PostgreSQL indexes for a content site. Learned to read EXPLAIN before adding hardware.

## Skills

- Go, Redis, PostgreSQL
- Latency budgets, load tests
- HTTP read APIs, on-call
- Cantonese and English

## Education

BSc Computer Science, City University of Hong Kong (2018)
