# 01: Look up commands in one table

**Role:** needs-triage
**Closed:** no
**Priority:** 4
**Blocked by:** None (can start immediately)

**What to build:** `_run` in `stock/cli.py` picks the command with one `if args.command == ...` branch per command, and each new command adds a branch. Found in the code review of low-stock 01, as a judgement call (Repeated Switches), not a defect. A table from command name to handler would put each command in one place. It is worth doing only if more commands are coming; the stocktake spec adds some.

**Touches:** the command line.

- [ ] every command still prints and exits exactly as before (the `tests/test_cli.py` tests pass unchanged)
- [ ] adding a command needs one entry in one place, plus its parser
