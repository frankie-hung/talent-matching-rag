---
candidate_id: cand-se-17
name: Samir Iqbal
years_exp: 6
location: Hong Kong
---

# Samir Iqbal

## Summary

Backend engineer in Hong Kong, six years, in Go and PostgreSQL on a logistics billing service that is adjacent to payments. Has owned HTTP APIs, idempotent invoice creation, automated tests, and on-call. A close match for a payouts team, with the domain scar being freight invoices rather than card acquiring.

## Experience


### Backend Engineer, Warehouse and Wire (fictional)
Hong Kong — 2021 to present

- Built the freight-invoice API in Go. Creating an invoice twice with the same shipper reference returns the first invoice.
- Posted invoice lines in a PostgreSQL transaction that also writes the audit row. A failure rolls both back.
- Tested currency rounding against a fixture finance signed. The argument moved out of email.
- On-call for invoice generation. One page was a downstream tax service; the note says we retry, we do not edit totals.
### Developer, Peakform Logistics (fictional)
Hong Kong — 2019 to 2021

- Maintained a rate-quote service. Added the timeout budget the carrier API had been ignoring.

## Skills

- Go, HTTP APIs, idempotent creates
- PostgreSQL transactions and audit rows
- Rounding tests, production on-call
- English

## Education

BSc Software Engineering, a Lahore university (2019)
