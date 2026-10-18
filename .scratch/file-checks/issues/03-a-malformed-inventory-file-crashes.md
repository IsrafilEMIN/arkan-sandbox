# 03: A malformed inventory file crashes with a traceback

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** `store.load` (`stock/store.py`) reads `inventory.json` with `json.loads` and `raw["..."]`. A hand edit that breaks the JSON, or that drops a field such as `qty`, raises `JSONDecodeError` or `KeyError`. Every command then crashes with a Python traceback, not a `stock:` message. `CODING_STANDARDS.md` says every error a user can cause is a `StockError`, and a hand edit of the inventory file is an error a user can cause.

Found in the code review of file-checks 01.

**Touches:** loading the inventory file, `stock/errors.py` and the tablet page (`stock/web.py`, which catches no `StockError` today).

- [ ] a file that is not valid JSON makes each command print one `stock:` line that names the file, and exit 1
- [ ] an item with a missing field makes each command print one `stock:` line that names the file and the field, and exit 1
- [ ] a `qty` or `price_cents` that is not a whole number (for example `"3"`) makes each command print one `stock:` line that names the file and the sku, and exit 1. Since file-checks 01, the negative quantity check raises `TypeError` on such a file for every command
- [ ] the tablet page shows the same message for a malformed file, not a traceback
