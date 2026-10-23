---
candidate_id: cand-se-03
name: Ingrid Lau
years_exp: 5
location: Hong Kong (hybrid)
---

# Ingrid Lau

## Summary

Backend engineer, five years, hybrid in Hong Kong. Ships Go services that sit behind HTTP and a small Kafka consumer. Cares about idempotent handlers and tests that describe the business rule in the name of the test. Has been on-call for a checkout API, not for laptops or the office network.

## Experience


### Backend Engineer, Quarry API (fictional)
Hong Kong, hybrid — 2022 to present

- Designed the checkout HTTP API in Go. Status codes distinguish a validation reject from a downstream timeout the caller may retry.
- Consumed order events from Kafka. The handler stores the event id and ignores a duplicate delivery instead of creating a second charge.
- Wrote table-driven tests for discount stacking. A product argument about ‘which discount wins’ became a fixture, not a Slack thread.
- Took on-call one week in four. Added a log field the pager runbook now tells you to search first.
### Junior Developer, Northwind Retail APAC (fictional)
Hong Kong — 2020 to 2022

- Maintained an internal inventory API in Go and PostgreSQL. Fixed a race where two stores decremented the same row.
- Shadowed on-call before holding the rota alone.

## Skills

- Go, HTTP APIs, Kafka consumers
- PostgreSQL, idempotent handlers
- Table-driven tests, on-call notes
- English and Cantonese

## Education

BSc Computer Science, University of Hong Kong (2020)
