---
job_id: job-backend
title: Backend Software Engineer
location: Hong Kong (hybrid, Kwun Tong)
years_required: 4
must_have_skills:
  - Go or Java
  - Relational databases (PostgreSQL or MySQL)
  - Designing and operating HTTP APIs
  - Production on-call for a service you shipped
  - Automated tests around business rules
---

# Backend Software Engineer

**Team:** Payments Platform, Typhoon Pay (fictional)  
**Type:** Permanent, hybrid — Kwun Tong three days a week  
**Reports to:** Engineering Manager, Ledger Services

## About the role

Typhoon Pay moves merchant payouts and refunds for shops in Hong Kong and a few nearby markets. The ledger service is the system of record for those movements. We need a backend engineer who can change it without breaking a settlement that already left the building.

This is an individual contributor seat. You will design the API, write the tests, sit in the on-call rotation, and explain a failure in writing the next morning.

## What you will do

- Design HTTP APIs for payouts, refunds, and reconciliation callbacks. Idempotency and explicit error codes are part of the contract, not a follow-up.
- Model money movement in PostgreSQL or MySQL. You should be comfortable with transactions, unique keys, and a query plan that is not a surprise under month-end load.
- Write the service in Go or Java. The team has both. New code matches the service you join, and you do not introduce a third language for one endpoint.
- Own production behaviour: structured logs, a dashboard you actually open, and a runbook entry when you ship something operators will be paged for.
- Review colleagues’ changes for correctness around partial failure, retries, and daylight-saving or holiday cut-offs.
- Pair with finance when a number in the product disagrees with the ledger. You bring the row, not a screenshot of a total.

## What you bring

- At least four years building backend services that other systems call, not only scripts and one-off jobs.
- Daily fluency in Go or Java, and in SQL against a relational database you have operated.
- A shipped API with versioning or compatibility notes, plus tests that failed when a business rule changed.
- Experience in an on-call rotation. You can say what you changed during an incident and what you left for the next shift.
- Clear written English. Specs and incident notes are short and specific.

## Nice to have

- Payments, billing, or other double-entry style domains.
- A message bus (Kafka or similar) used for a real consumer, including a poison-message story.
- Familiarity with Hong Kong holiday calendars and multi-currency rounding.
- Cantonese for local merchant-ops conversations. English remains the language of the codebase and the runbooks.

## How we work

Kwun Tong hybrid. Core hours overlap the settlement window. We write decisions next to the code. On-call is a weekly rota and most weeks are quiet.
