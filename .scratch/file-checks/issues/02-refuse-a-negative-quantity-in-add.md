# 02: Refuse a negative quantity in add

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** `stock add X1 widget -1 1.00` adds an item with a quantity of -1, and the stock value goes down. `receive` and `remove` already refuse a quantity of 0 or less, but `add` takes any whole number. Found while verifying low-stock 01 (PR #11); it happens on `run/feature` before that change too.

**Touches:** the inventory and the command line.

- [ ] `stock add` with a negative quantity prints a `stock:` error, exits 1 and does not change the inventory file
- [ ] `stock add` with a quantity of 0 still works, for an item that is out of stock
