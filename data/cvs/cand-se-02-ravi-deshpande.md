---
candidate_id: cand-se-02
name: Ravi Deshpande
years_exp: 6
location: Hong Kong
---

# Ravi Deshpande

## Summary

Java backend engineer, six years in Hong Kong, mostly on ledger and billing services. Comfortable with Spring, MySQL transactions, and an on-call week that includes writing the incident note. Less interested in front-end work. Has shipped versioned HTTP APIs used by an internal finance tool.

## Experience


### Backend Engineer, Harbourline Digital Bank (fictional)
Hong Kong — 2022 to present

- Maintained the fee-ledger service in Java. Each posting is a transaction with a unique business key so a replay cannot double-charge a merchant.
- Published a versioned HTTP API for finance adjustments. Compatibility notes lived next to the endpoint, and old clients kept working through one deprecation window.
- Joined the on-call rotation for the ledger. During a deadlock incident, captured the blocking query and left a follow-up to shorten the transaction.
- Covered the business rules with automated tests: tax rounding, reversal of a reversal, and a rejected adjustment that must not leave a half-posted row.
### Software Engineer, Metrobyte Systems (fictional)
Hong Kong — 2019 to 2022

- Built subscription billing jobs in Java against MySQL. Learned to separate a read model from the table that takes the money.
- Added request logs with a correlation id so support could find one invoice without a database screenshot.

## Skills

- Java, Spring, HTTP APIs
- MySQL transactions and indexes
- On-call, incident notes, correlation ids
- JUnit tests around billing rules
- English

## Education

BTech Computer Engineering, a Pune university (2019)
