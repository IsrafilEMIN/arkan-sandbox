"""The `stock` command line: it reads the arguments and prints the results."""

import argparse
import os
import sys
from pathlib import Path

from stock import store
from stock.errors import StockError
from stock.inventory import Inventory, Item
from stock.money import format_money, parse_money

DEFAULT_FILE = "inventory.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stock", description="Keep track of the stock on hand.")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(os.environ.get("STOCK_FILE", DEFAULT_FILE)),
        help="the inventory file (default: $STOCK_FILE or ./inventory.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a new item")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("qty", type=_whole_number)
    add.add_argument("price", help="unit price, e.g. 2.50")

    receive = sub.add_parser("receive", help="add stock that arrived")
    receive.add_argument("sku")
    receive.add_argument("n", type=_whole_number)

    remove = sub.add_parser("remove", help="take stock out (sold, used, broken)")
    remove.add_argument("sku")
    remove.add_argument("n", type=_whole_number)

    sub.add_parser("list", help="show every item")
    sub.add_parser("value", help="show the total value of the stock on hand")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inventory = store.load(args.file)
        changed = _run(args, inventory)
        if changed:
            store.save(inventory, args.file)
    except StockError as err:
        print(f"stock: {err}", file=sys.stderr)
        return 1
    return 0


def _run(args: argparse.Namespace, inventory: Inventory) -> bool:
    """Run one command. Returns True when the inventory changed and must be saved."""
    if args.command == "add":
        item = Item(args.sku, args.name, args.qty, parse_money(args.price))
        inventory.add_item(item)
        print(f"added {item.sku}: {item.qty} x {item.name} at {format_money(item.price_cents)}")
        return True
    if args.command == "receive":
        item = inventory.receive(args.sku, args.n)
        print(f"{item.sku}: {item.qty} on hand")
        return True
    if args.command == "remove":
        item = inventory.remove(args.sku, args.n)
        print(f"{item.sku}: {item.qty} on hand")
        return True
    if args.command == "list":
        _print_list(inventory)
        return False
    if args.command == "value":
        print(format_money(inventory.total_value_cents()))
        return False
    raise AssertionError(f"unhandled command {args.command}")


def _print_list(inventory: Inventory) -> None:
    items = inventory.items()
    if not items:
        print("no items")
        return
    width = max(len(item.sku) for item in items)
    for item in items:
        price = format_money(item.price_cents)
        print(f"{item.sku:<{width}}  {item.qty:>5}  {price:>10}  {item.name}")


def _whole_number(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a whole number: {text}") from None
