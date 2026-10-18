# 01: Stock value does not add up

**Role:** ready-for-agent
**Closed:** yes
**Priority:** 1
**Blocked by:** None (can start immediately)

**What's wrong:** I checked `stock value` against a hand count before the accountant's visit and the numbers don't match. It happens with just two items in a fresh file:

```
stock --file /tmp/check.json add STK-01 "star stickers" 1 0.05
stock --file /tmp/check.json add PEN-01 "blue pen" 3 1.00
stock --file /tmp/check.json value
```

That prints `$3.5`. By hand it's 5 cents plus $3.00, so $3.05. The export of the same file has 0.05 and 3.00 in the value column, so I think the file is right and it's the number `stock value` shows. I'd like the value to be right, and anywhere else stock shows me money, if the same thing happens there.

**Touches:** the stock package.

- [x] `stock value` prints `$3.05` for the two items above
- [x] no other command shows a wrong amount of money

## Comments

Fixed on branch `value-report-01`. There were two causes. `stock` dropped the leading zero when it showed cents under ten, so 305 cents printed as `$3.5`. Separately, since the thousands-separator change, it read a price with one decimal place as cents: `0.5` became 5 cents, not 50.

The fix does not change prices that are already saved. Any item added with a one-decimal price (like `2.5`) between that change and this fix is stored ten times too low in that place: `2.5` is stored as $2.05. Check `stock list` for such items and fix them by hand.
