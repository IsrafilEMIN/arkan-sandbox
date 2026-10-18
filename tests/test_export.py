import csv
import datetime
import os
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

    def test_list_exports_is_empty_before_the_first_export(self):
        self.assertEqual(export.list_exports(self.inventory_file), [])

    def test_list_exports_puts_the_newest_file_first(self):
        folder = export.exports_dir(self.inventory_file)
        folder.mkdir()
        for name, mtime in [("old.csv", 1000), ("new.csv", 3000), ("mid.csv", 2000)]:
            (folder / name).write_text("sku\n")
            os.utime(folder / name, (mtime, mtime))
        names = [path.name for path in export.list_exports(self.inventory_file)]
        self.assertEqual(names, ["new.csv", "mid.csv", "old.csv"])

    def test_list_exports_skips_folders_and_links(self):
        folder = export.exports_dir(self.inventory_file)
        folder.mkdir()
        (folder / "stock-2026-10-18.csv").write_text("sku\n")
        (folder / "old").mkdir()
        (folder / "secret.csv").symlink_to(self.inventory_file)
        names = [path.name for path in export.list_exports(self.inventory_file)]
        self.assertEqual(names, ["stock-2026-10-18.csv"])


if __name__ == "__main__":
    unittest.main()
