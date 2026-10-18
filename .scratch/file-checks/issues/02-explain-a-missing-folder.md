# 02: Explain a missing folder

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What's wrong:** when the folder named in `--file` does not exist, `stock add` prints its `added ...` line and then crashes with a Python traceback, and nothing is saved:

```
stock --file no-such-folder/check.json add STK-01 "star stickers" 1 0.05
added STK-01: 1 x star stickers at $0.05
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'no-such-folder/check.json.tmp'
```

`store.save` lets the `FileNotFoundError` out, and `CODING_STANDARDS.md` says every error a user can cause is a `StockError`. Found while verifying `value-report` 01.

**Touches:** saving the inventory file and the command line.

- [ ] a `--file` in a missing folder prints a one-line `stock:` message and exits 1, with no traceback
- [ ] the command does not print `added ...` for an item it did not save
