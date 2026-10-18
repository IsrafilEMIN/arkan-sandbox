"""Load and save the inventory as a JSON file."""

import json
import os
from pathlib import Path

from stock.inventory import Inventory, Item

FIELDS = ("sku", "name", "qty", "price_cents")


def load(path: Path) -> Inventory:
    """Read the inventory at path. A missing file is an empty inventory."""
    if not path.exists():
        return Inventory()
    data = json.loads(path.read_text(encoding="utf-8"))
    items = []
    for raw in data["items"]:
        items.append(
            Item(
                sku=raw["sku"],
                name=raw["name"],
                qty=raw["qty"],
                price_cents=raw["price_cents"],
            )
        )
    return Inventory(items)


def save(inventory: Inventory, path: Path) -> None:
    """Write the inventory to path, replacing the old file in one step."""
    data = {"items": [_to_dict(item) for item in inventory.items()]}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _to_dict(item: Item) -> dict:
    return {field: getattr(item, field) for field in FIELDS}
