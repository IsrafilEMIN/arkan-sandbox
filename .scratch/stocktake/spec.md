# Stocktake

**Closed:** no
**Priority:** 1

## Why

Twice a year we count everything on the shelves and fix the quantities in stock. Today that means printing `stock list`, writing on it, and typing every difference back by hand with `receive` and `remove`. It takes an evening and we still get some wrong.

## What

1. Print a count sheet: a CSV with every item and an empty column to write the counted number in.
2. Set an item's quantity straight to a number, when we know the real number.
3. Read a filled-in count sheet back and set every counted quantity in one go, showing what changed.
4. Flag big differences for a second count before they go in. This one waits until we decide what "big" means.

## Out of scope

Counting by shelf or room, barcode scanners, and keeping a history of past counts.

## Tickets

- `issues/01-print-a-count-sheet.md`
- `issues/02-set-an-items-quantity.md`
- `issues/03-apply-a-filled-count-sheet.md` (needs 01's sheet format)
- `issues/04-flag-big-differences-for-a-recount.md` (waits on our decision)
