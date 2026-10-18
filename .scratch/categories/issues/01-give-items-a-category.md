# 01: Give items a category

**Role:** ready-for-agent
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** I want to sort the stock into categories (stationery, cleaning, kitchen and so on). `stock add` takes an optional `--category`, `stock set-category <sku> <category>` changes it (an empty category clears it), and the category is saved in the inventory file. Files from before this keep loading, with no category on any item. `stock list --by-category` prints one heading per category in alphabetical order, the items under each heading sorted by sku, and the items with no category last, under "Uncategorised". The grouping belongs to the inventory, not to the command line.

**Touches:** the inventory, the inventory file and the command line.

- [ ] `stock add --category` and `stock set-category` set the category, and it survives a save and load
- [ ] an inventory file with no categories still loads
- [ ] `stock list --by-category` groups as above, with "Uncategorised" last
