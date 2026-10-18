# 01: Match SKUs however they are typed

**Role:** ready-for-agent
**Closed:** no
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** the staff type SKUs every which way: `pen-01`, `PEN01`, `Pen 01`. Today each of those gets "no item with sku ..." unless it is typed exactly the way it was added. A SKU should match whatever the case, and whatever dashes or spaces it has: `pen-01`, `PEN01` and ` Pen 01 ` all find the item added as `PEN-01`.

The rules, all of which matter to us:

- Every command that takes a sku finds the item by this rule.
- `stock add` refuses a new item whose sku matches an existing one by this rule, with the usual "already exists" message, naming the existing item's sku.
- A sku is shown and saved the way it was first added (`PEN-01`), everywhere: `stock list`, the export, the tablet and every message. Don't rewrite people's inventory files.
- Lists sort by the matching form, so `pen-01` comes before `PEN-02`, not after it.
- An old inventory file can already hold two items that now match each other (say `PEN-01` and `pen01`). Then every command refuses to load it, with a message that names both skus, so I can fix the file by hand. Don't merge them and don't drop either.
- `stock add` refuses a sku that is empty once the spaces and dashes are gone, like `--` or a single space.

**Touches:** the inventory, the inventory file and the errors.

- [ ] each rule above holds, with a test for each
