# 01: List items that are running low

**Role:** ready-for-agent
**Closed:** no
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** before I phone the suppliers on Monday I want one command that shows what's running low. `stock low` lists every item with 5 or fewer on hand, and `stock low --at 10` changes the cutoff. Same columns as `stock list`, fewest on hand first, ties by sku. If nothing is low, say `nothing is running low` instead of printing nothing.

**Touches:** the inventory and the command line.

- [ ] `stock low` lists the items with 5 or fewer on hand, fewest first, ties by sku
- [ ] `--at N` sets the cutoff; N can be 0 but not negative
- [ ] it prints `nothing is running low` when no item is at or below the cutoff
