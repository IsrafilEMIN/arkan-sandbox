import unittest

from stock.errors import DuplicateSku, InvalidQuantity, NotEnoughStock, UnknownSku
from stock.inventory import Inventory, Item


def sample() -> Inventory:
    return Inventory(
        [
            Item("PEN-01", "blue pen", 10, 120),
            Item("BOOK-A5", "a5 notebook", 4, 350),
        ]
    )


class InventoryTest(unittest.TestCase):
    def test_lists_items_sorted_by_sku(self):
        self.assertEqual([item.sku for item in sample().items()], ["BOOK-A5", "PEN-01"])

    def test_rejects_a_duplicate_sku(self):
        inventory = sample()
        with self.assertRaises(DuplicateSku):
            inventory.add_item(Item("PEN-01", "red pen", 1, 120))

    def test_receive_adds_to_the_quantity(self):
        self.assertEqual(sample().receive("PEN-01", 5).qty, 15)

    def test_remove_takes_from_the_quantity(self):
        self.assertEqual(sample().remove("PEN-01", 3).qty, 7)

    def test_remove_refuses_more_than_is_on_hand(self):
        inventory = sample()
        with self.assertRaises(NotEnoughStock):
            inventory.remove("BOOK-A5", 5)
        self.assertEqual(inventory.get("BOOK-A5").qty, 4)

    def test_quantities_must_be_above_zero(self):
        inventory = sample()
        for n in [0, -2]:
            with self.subTest(n=n):
                with self.assertRaises(InvalidQuantity):
                    inventory.receive("PEN-01", n)

    def test_unknown_sku_is_an_error(self):
        with self.assertRaises(UnknownSku):
            sample().get("NOPE")

    def test_total_value_is_quantity_times_price(self):
        self.assertEqual(sample().total_value_cents(), 10 * 120 + 4 * 350)

    def test_negative_items_lists_only_items_below_zero_sorted_by_sku(self):
        inventory = sample()
        inventory.add_item(Item("TAPE-1", "tape", -1, 90))
        inventory.add_item(Item("CLIP-9", "paper clip", -3, 5))
        self.assertEqual([item.sku for item in inventory.negative_items()], ["CLIP-9", "TAPE-1"])

    def test_negative_items_is_empty_when_every_quantity_is_zero_or_more(self):
        inventory = sample()
        inventory.add_item(Item("TAPE-1", "tape", 0, 90))
        self.assertEqual(inventory.negative_items(), [])


if __name__ == "__main__":
    unittest.main()
