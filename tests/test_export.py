import csv
import datetime
import tempfile
import unittest
from pathlib import Path

from stock import export
from stock.inventory import Inventory, Item


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.inventory_file = Path(self.dir.name) / "inventory.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_the_export_goes_in_exports_next_to_the_inventory_file(self):
        path = export.export_path(self.inventory_file, datetime.date(2026, 10, 18))
        self.assertEqual(path, Path(self.dir.name) / "exports" / "stock-2026-10-18.csv")

    def test_writes_a_header_and_one_row_per_item_sorted_by_sku(self):
        inventory = Inventory([Item("PEN-01", "blue pen", 10, 120), Item("BOOK-A5", "a5", 3, 405)])
        path = export.export_path(self.inventory_file, datetime.date(2026, 10, 18))
        export.write_csv(inventory, path)
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        self.assertEqual(
            rows,
            [
                ["sku", "name", "qty", "price", "value"],
                ["BOOK-A5", "a5", "3", "4.05", "12.15"],
                ["PEN-01", "blue pen", "10", "1.20", "12.00"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
