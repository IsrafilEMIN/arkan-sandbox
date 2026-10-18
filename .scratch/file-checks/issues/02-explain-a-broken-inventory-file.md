# 02: Explain a broken inventory file

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What's wrong:** when `inventory.json` is not valid JSON (for example `{broken`), every command crashes with a Python `JSONDecodeError` traceback. `CODING_STANDARDS.md` says every error a user can cause is a `StockError` with a message a shop worker understands. A hand edit that breaks the file is an error a user can cause. Found in the code review of low-stock 01; `stock/store.py` `load` was not part of that change.

**Touches:** loading the inventory file.

- [ ] a command run on a file that is not valid JSON prints one `stock: ...` line that names the file, and exits 1
- [ ] no traceback is shown
