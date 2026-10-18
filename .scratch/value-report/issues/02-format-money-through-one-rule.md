# 02: Format money through one rule

**Role:** needs-triage
**Closed:** no
**Priority:** 2
**Blocked by:** None (can start immediately)

**What's wrong:** `format_money` and `plain_money` in `stock/money.py` each split cents into dollars and cents by hand, and differ only in the `$`. Ticket 01 happened because the two copies drifted: only `plain_money` padded the cents. If `format_money` built on `plain_money`, one rule would cover both.

Found in the code review of value-report 01. The behaviour is right today; this is about keeping the two copies from drifting again.

**Touches:** `stock/money.py`.

- [ ] one function holds the dollars-and-cents rule, and the other builds on it
- [ ] `format_money` and `plain_money` return the same strings as before
