# 01: Stock value does not add up

**Role:** ready-for-agent
**Closed:** no
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

- [ ] `stock value` prints `$3.05` for the two items above
- [ ] no other command shows a wrong amount of money
