# 03: Apply a filled count sheet

**Role:** ready-for-agent
**Closed:** no
**Priority:** 1
**Blocked by:** 01

**What to build:** `stock count-apply <file>` reads a count sheet from ticket 01 after we've filled in the `counted` column, and sets each counted item's quantity to the counted number. A row with `counted` left empty means "not counted" and changes nothing. It prints one line per item that changed, like `PEN-01: 10 -> 7 (-3)`, then `3 items changed`. If any row is bad (a sku stock doesn't know, or a counted value that isn't a whole number of 0 or more) it changes nothing at all, and says which row is wrong.

**Touches:** the export module, the inventory and the command line.

- [ ] counted rows set the quantity, empty ones are left alone, and each change is printed with its difference
- [ ] one bad row means no change at all, and the message names the row
