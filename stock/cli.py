"""The `stock` command line: it reads the arguments and prints the results."""

import argparse
import datetime
import os
import sys
from pathlib import Path

from stock import export, store, web
from stock.errors import StockError
from stock.inventory import Inventory, Item
from stock.money import format_money, parse_money

DEFAULT_FILE = "inventory.json"

EXAMPLES = """examples:
  stock add PEN-01 "blue pen" 10 1.20   add 10 blue pens at $1.20 each
  stock receive PEN-01 24               24 more arrived
  stock remove PEN-01 3                 3 sold
  stock list                            every item, sorted by sku
  stock value                           what the stock on hand is worth
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stock",
        description="Keep track of the stock on hand.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    sub.add_parser("export", help="write the inventory to exports/stock-<date>.csv")

    serve = sub.add_parser("serve", help="show the stock on the shop tablet")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--host", default="0.0.0.0", help="address to listen on (default: all)")
    return parser


def main(argv: list[str] | None = None, today: datetime.date | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        return _serve(args)
    args.today = today or datetime.date.today()
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
    if args.command == "export":
        path = export.export_path(args.file, args.today)
        export.write_csv(inventory, path)
        print(path)
        return False
    raise AssertionError(f"unhandled command {args.command}")


def _serve(args: argparse.Namespace) -> int:
    server = web.make_server(args.file, args.host, args.port)
    host, port = server.server_address[:2]
    print(f"serving {args.file} on http://{host}:{port}/ (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


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
