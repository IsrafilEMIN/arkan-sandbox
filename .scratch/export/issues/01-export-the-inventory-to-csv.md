# 01: Export the inventory to CSV

**Role:** ready-for-agent
**Closed:** yes
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** `stock export` writes the whole inventory to a CSV file my accountant can open in a spreadsheet. One row per item: sku, name, quantity, unit price and value, with the money as plain numbers like `12.50` (no `$`, so the spreadsheet can add them up). The file goes in an `exports/` folder next to the inventory file, named after today's date (`stock-2026-10-18.csv`), and the command prints the path it wrote. Running it twice in a day replaces that day's file.

**Touches:** the stock package (a new export module and the command line).

- [x] `stock export` writes `exports/stock-<date>.csv` next to the inventory file and prints the path
- [x] the CSV has a header row and one row per item, sorted by sku
- [x] prices and values are plain decimal numbers with two places
