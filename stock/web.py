"""The tablet page: a small read-only web server for the shop network."""

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from stock import store
from stock.inventory import Inventory
from stock.money import format_money

Response = tuple[HTTPStatus, str, bytes]

HTML = "text/html; charset=utf-8"
JSON = "application/json"
TEXT = "text/plain; charset=utf-8"


def respond(inventory_file: Path, target: str) -> Response:
    """Answer one GET request for target, the path and query from the request line."""
    path = urlsplit(target).path
    if path == "/":
        return HTTPStatus.OK, HTML, render_page(store.load(inventory_file)).encode("utf-8")
    if path == "/items.json":
        return HTTPStatus.OK, JSON, render_json(store.load(inventory_file)).encode("utf-8")
    return HTTPStatus.NOT_FOUND, TEXT, b"not found\n"


def render_page(inventory: Inventory) -> str:
    rows = "\n".join(
        "<tr><td>{}</td><td>{}</td><td class=n>{}</td><td class=n>{}</td></tr>".format(
            html.escape(item.sku),
            html.escape(item.name),
            item.qty,
            html.escape(format_money(item.price_cents)),
        )
        for item in inventory.items()
    )
    return f"""<!doctype html>
<html lang=en>
<meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Stock</title>
<style>
body {{ font: 18px system-ui, sans-serif; margin: 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: .4rem .6rem; border-bottom: 1px solid #ccc; text-align: left; }}
.n {{ text-align: right; }}
</style>
<h1>Stock</h1>
<table>
<tr><th>SKU</th><th>Name</th><th class=n>Qty</th><th class=n>Price</th></tr>
{rows}
</table>
"""


def render_json(inventory: Inventory) -> str:
    items = [
        {"sku": item.sku, "name": item.name, "qty": item.qty, "price_cents": item.price_cents}
        for item in inventory.items()
    ]
    return json.dumps({"items": items}, indent=2) + "\n"


def make_server(inventory_file: Path, host: str, port: int) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status, content_type, body = respond(inventory_file, self.path)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer((host, port), Handler)
