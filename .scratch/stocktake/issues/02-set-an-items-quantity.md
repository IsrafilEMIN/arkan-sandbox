# 02: Set an item's quantity

**Role:** ready-for-agent
**Closed:** no
**Priority:** 1
**Blocked by:** None (can start immediately)

**What to build:** `stock set <sku> <qty>` sets an item's quantity to that number, for when we know the real count and don't want to work out the difference. 0 is fine, a negative number is refused. It prints the new and the old quantity: `PEN-01: 7 on hand (was 10)`.

**Touches:** the inventory and the command line.

- [ ] `stock set` sets the quantity and prints `<sku>: <new> on hand (was <old>)`
- [ ] 0 is accepted and a negative quantity is refused with a message
