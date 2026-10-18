"""Errors a user can cause. The CLI turns each one into a message."""


class StockError(Exception):
    """Base class for every error a user can cause."""


class UnknownSku(StockError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"no item with sku {sku}")
        self.sku = sku


class DuplicateSku(StockError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"sku {sku} already exists")
        self.sku = sku


class NotEnoughStock(StockError):
    def __init__(self, sku: str, have: int, want: int) -> None:
        super().__init__(f"only {have} of {sku} in stock, cannot remove {want}")
        self.sku = sku
        self.have = have
        self.want = want


class InvalidQuantity(StockError):
    def __init__(self, n: int) -> None:
        super().__init__(f"quantity must be a whole number above zero, got {n}")
        self.n = n


class InvalidPrice(StockError):
    def __init__(self, text: str) -> None:
        super().__init__(f"cannot read price {text!r}, use a form like 2.50")
        self.text = text


class InvalidDiscount(StockError):
    def __init__(self, percent: int) -> None:
        super().__init__(f"a discount must be 0 to 100 percent, got {percent}")
        self.percent = percent
