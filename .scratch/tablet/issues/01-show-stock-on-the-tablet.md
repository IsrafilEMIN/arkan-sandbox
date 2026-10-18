# 01: Show stock on the tablet

**Role:** ready-for-agent
**Closed:** yes
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** the shop tablet should show what's in stock without anyone touching the terminal. `stock serve` starts a small web server on the shop network (port 8000 by default, `--port` to change it). Its home page is a plain table of every item: sku, name, quantity on hand and price, sorted by sku. `/items.json` gives the same data as JSON for the label printer script. Read-only: nothing on the tablet changes stock.

**Touches:** the stock package (a new web module and the command line).

- [x] `stock serve` serves the item table at `/` and the items as JSON at `/items.json`
- [x] item names show exactly as typed, even with `<` or `&` in them
- [x] any other path is a 404; any method but GET is refused
