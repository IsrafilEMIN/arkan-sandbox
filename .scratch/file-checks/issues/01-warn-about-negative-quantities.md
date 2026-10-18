# 01: Warn about negative quantities

**Role:** ready-for-agent
**Closed:** yes
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** last week I fixed a count by hand in `inventory.json` and typed `-3` instead of `3`. Nothing complained: `stock list` showed -3 and the stock value went down. I don't want stock to refuse the file, because I still need to sell things while I sort it out. But every command should warn me which skus have a negative quantity, on stderr, one line each, like:

```
stock: warning: PEN-01 has a negative quantity (-3), check inventory.json
```

and then run as normal.

**Touches:** loading the inventory file and the command line.

- [x] every command run on a file with a negative quantity prints one warning line per such sku to stderr, naming the file
- [x] the command still runs and exits as it would without the warning
- [x] a file with no negative quantities prints no warning
