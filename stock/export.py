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


def list_exports(inventory_file: Path) -> list[Path]:
    """The files in the exports folder, newest first. Folders and links are left out."""
    folder = exports_dir(inventory_file)
    if not folder.is_dir():
        return []
    # A link could point anywhere on the computer, and the tablet serves what this lists.
    files = [path for path in folder.iterdir() if path.is_file() and not path.is_symlink()]
    return sorted(files, key=lambda path: (path.stat().st_mtime, path.name), reverse=True)


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
