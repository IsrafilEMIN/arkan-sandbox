# 01: Print a count sheet

**Role:** ready-for-agent
**Closed:** no
**Priority:** 1
**Blocked by:** None (can start immediately)

**What to build:** `stock count-sheet` writes a CSV we can print or fill in on the tablet: columns `sku`, `name`, `expected` (the quantity stock has now) and `counted` (left empty), one row per item, sorted by sku. It goes in the exports folder next to the inventory file as `count-<date>.csv`, and the command prints the path it wrote.

**Touches:** the export module and the command line.

- [ ] `stock count-sheet` writes `exports/count-<date>.csv` and prints the path
- [ ] the sheet has the four columns above, `counted` empty, one row per item sorted by sku
