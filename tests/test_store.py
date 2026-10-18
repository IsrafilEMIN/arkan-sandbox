import tempfile
import unittest
from pathlib import Path

from stock import store
from stock.inventory import Inventory, Item


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "inventory.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_a_missing_file_is_an_empty_inventory(self):
        self.assertEqual(store.load(self.path).items(), [])

    def test_save_then_load_keeps_every_field(self):
        inventory = Inventory([Item("PEN-01", "blue pen", 10, 120)])
        store.save(inventory, self.path)
        self.assertEqual(store.load(self.path).items(), [Item("PEN-01", "blue pen", 10, 120)])

    def test_save_leaves_no_temporary_file(self):
        store.save(Inventory(), self.path)
        self.assertEqual([p.name for p in Path(self.dir.name).iterdir()], ["inventory.json"])


if __name__ == "__main__":
    unittest.main()
