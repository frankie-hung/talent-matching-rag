---
candidate_id: cand-se-01
name: Hannah Choi
years_exp: 7
location: Hong Kong
---

# Hannah Choi

## Summary

Backend engineer in Hong Kong with seven years on payment and ledger services. Writes Go, treats PostgreSQL transactions as part of the API contract, and has carried a production on-call rota for payouts. Prefers an idempotency key and a failing test over a hopeful retry.

## Experience


### Senior Backend Engineer, Typhoon Pay (fictional)
Hong Kong — 2021 to present

- Owned the merchant payout HTTP API in Go. Clients send an idempotency key, and a retried request returns the original result instead of moving money twice.
- Modelled payout, refund, and fee lines in PostgreSQL. A unique constraint on the external reference stopped a duplicate settlement that a queue retry had started.
- Sat on the weekly on-call rota. Wrote the runbook for a stuck payout after a holiday cut-off, including the exact row an operator should not update by hand.
- Added integration tests around partial refunds. The suite failed when a rounding change disagreed with the ledger by one cent.
### Software Engineer, Starferry Payments (fictional)
Hong Kong — 2018 to 2021

- Built internal HTTP services in Go for reconciliation callbacks. Documented error codes so the caller could tell a permanent reject from a retry.
- Tuned a month-end SQL report that had been scanning the full ledger. The query plan, not a bigger instance, was the fix.

## Skills

- Go, HTTP APIs, idempotency, OpenAPI notes
- PostgreSQL transactions, unique keys, query plans
- Production on-call, structured logs, runbooks
- Integration tests for money-movement rules
- English and Cantonese

## Education

BEng Computer Science, Hong Kong University of Science and Technology (2018)
