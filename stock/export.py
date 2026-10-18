"""Write the inventory as a CSV file a spreadsheet can open."""

import csv
import datetime
from pathlib import Path

from stock.inventory import Inventory
from stock.money import plain_money

HEADER = ("sku", "name", "qty", "price", "value")


def exports_dir(inventory_file: Path) -> Path:
    """The folder the exports go in: `exports/` next to the inventory file."""
    return inventory_file.parent / "exports"


def export_path(inventory_file: Path, day: datetime.date) -> Path:
    return exports_dir(inventory_file) / f"stock-{day.isoformat()}.csv"


def write_csv(inventory: Inventory, path: Path) -> None:
    """Write one row per item, sorted by sku, replacing any file already at path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for item in inventory.items():
            writer.writerow(
                [
                    item.sku,
                    item.name,
                    item.qty,
                    plain_money(item.price_cents),
                    plain_money(item.value_cents),
                ]
            )
