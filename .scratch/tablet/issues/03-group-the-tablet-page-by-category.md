# 03: Group the tablet page by category

**Role:** ready-for-agent
**Closed:** no
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** the stock table on the tablet is getting long and people scroll past what they want. Group it the same way as `stock list --by-category`: one heading per category in alphabetical order, the items under each heading sorted by sku, and the items with no category last, under "Uncategorised". `/items.json` should give each item's category too, so the label printer script can print it on the shelf labels.

**Touches:** the web module.

- [ ] the home page shows one table per category, in the same order as `stock list --by-category`
- [ ] items with no category are last, under "Uncategorised"
- [ ] each item in `/items.json` has a `category` field, `null` when it has none
