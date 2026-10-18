"""The inventory: the items on hand, keyed by sku."""

from dataclasses import dataclass

from stock.errors import (
    DuplicateSku,
    InvalidDiscount,
    InvalidQuantity,
    NotEnoughStock,
    UnknownSku,
)


@dataclass
class Item:
    sku: str
    name: str
    qty: int
    price_cents: int

    @property
    def value_cents(self) -> int:
        return self.qty * self.price_cents


class Inventory:
    def __init__(self, items: list[Item] | None = None) -> None:
        self._items: dict[str, Item] = {}
        for item in items or []:
            self.add_item(item)

    def add_item(self, item: Item) -> None:
        if item.sku in self._items:
            raise DuplicateSku(item.sku)
        self._items[item.sku] = item

    def get(self, sku: str) -> Item:
        try:
            return self._items[sku]
        except KeyError:
            raise UnknownSku(sku) from None

    def items(self) -> list[Item]:
        """Every item, sorted by sku."""
        return sorted(self._items.values(), key=lambda item: item.sku)

    def receive(self, sku: str, n: int) -> Item:
        _require_positive(n)
        item = self.get(sku)
        item.qty += n
        return item

    def remove(self, sku: str, n: int) -> Item:
        _require_positive(n)
        item = self.get(sku)
        if n > item.qty:
            raise NotEnoughStock(sku, item.qty, n)
        item.qty -= n
        return item

    def total_value_cents(self) -> int:
        return sum(item.value_cents for item in self._items.values())

    def discounted_value_cents(self, percent: int) -> int:
        """The total value after taking `percent` off, for a clearance sale.

        Raises InvalidDiscount unless `percent` is 0 to 100.
        """
        if not 0 <= percent <= 100:
            raise InvalidDiscount(percent)
        return self.total_value_cents() * (100 - percent) // 100

    def low_stock(self, threshold: int) -> list[Item]:
        """The items with `threshold` or fewer on hand, sorted by sku, to reorder."""
        return [item for item in self.items() if item.qty > threshold]


def _require_positive(n: int) -> None:
    if n <= 0:
        raise InvalidQuantity(n)
