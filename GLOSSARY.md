# stock

stock keeps the inventory of one shop. this glossary names the things it tracks.

## Language

**Item**:
one kind of thing the shop sells or uses, with its sku, name, quantity on hand and unit price.
_Avoid_: product, article

**SKU**:
the short code that names an item, such as `PEN-01`. each item has exactly one.
_Avoid_: id, code, part number

**Quantity**:
how many of an item are on hand, a whole number. `qty` in code.
_Avoid_: count, amount, stock level

**Price**:
what one unit of an item is worth, in integer cents inside the program (see ADR 0001).
_Avoid_: cost, rate

**Value**:
quantity times price, for one item or summed over the inventory.
_Avoid_: total cost, worth

**Inventory**:
every item the shop has, kept in one inventory file.
_Avoid_: catalogue, database

**Inventory file**:
the JSON file that holds the inventory, `inventory.json` unless `--file` or `STOCK_FILE` names another.
_Avoid_: db, store

**Running low**:
an item whose quantity is at or below the cutoff: 5, unless `--at` sets another.
_Avoid_: low stock level, reorder point

**Receive**:
add stock that arrived to an item's quantity.
_Avoid_: restock, add stock

**Remove**:
take stock out of an item's quantity: sold, used or broken.
_Avoid_: sell, consume

## Relationships

- An **inventory** holds many **items**, each named by one **SKU**.
- An item's **value** is its **quantity** times its **price**.
