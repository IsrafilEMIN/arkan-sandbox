"""The tablet page: a small read-only web server for the shop network."""

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import NamedTuple
from urllib.parse import quote, unquote, urlsplit

from stock import export, store
from stock.inventory import Inventory
from stock.money import format_money

HTML = "text/html; charset=utf-8"
JSON = "application/json"
TEXT = "text/plain; charset=utf-8"
CSV = "text/csv; charset=utf-8"

STYLE = """body { font: 18px system-ui, sans-serif; margin: 1rem; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: .4rem .6rem; border-bottom: 1px solid #ccc; text-align: left; }
.n { text-align: right; }
li { padding: .4rem 0; }"""


class Response(NamedTuple):
    status: HTTPStatus
    content_type: str
    body: bytes
    download_name: str | None = None


NOT_FOUND = Response(HTTPStatus.NOT_FOUND, TEXT, b"not found\n")


def respond(inventory_file: Path, target: str) -> Response:
    """Answer one GET request for target, the path and query from the request line."""
    path = urlsplit(target).path
    if path == "/":
        page = render_page(store.load(inventory_file))
        return Response(HTTPStatus.OK, HTML, page.encode("utf-8"))
    if path == "/items.json":
        data = render_json(store.load(inventory_file))
        return Response(HTTPStatus.OK, JSON, data.encode("utf-8"))
    if path == "/exports":
        page = render_exports(export.list_exports(inventory_file))
        return Response(HTTPStatus.OK, HTML, page.encode("utf-8"))
    if path.startswith("/exports/"):
        return download(inventory_file, unquote(path.removeprefix("/exports/")))
    return NOT_FOUND


def download(inventory_file: Path, name: str) -> Response:
    # The name is looked up, never joined onto a folder, so no request can reach a file
    # that the exports page does not list.
    files = {path.name: path for path in export.list_exports(inventory_file)}
    if name not in files:
        return NOT_FOUND
    return Response(HTTPStatus.OK, CSV, files[name].read_bytes(), download_name=name)


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
    return _html_page(
        "Stock",
        f"""<p><a href="/exports">Exports</a></p>
<table>
<tr><th>SKU</th><th>Name</th><th class=n>Qty</th><th class=n>Price</th></tr>
{rows}
</table>""",
    )


def render_exports(files: list[Path]) -> str:
    links = "\n".join(
        '<li><a href="/exports/{}">{}</a></li>'.format(
            html.escape(quote(path.name, safe="")), html.escape(path.name)
        )
        for path in files
    )
    listing = f"<ul>\n{links}\n</ul>" if files else "<p>No exports yet.</p>"
    return _html_page("Exports", f"""<p><a href="/">Stock</a></p>\n{listing}""")


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=en>
<meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{STYLE}
</style>
<h1>{title}</h1>
{body}
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
            reply = respond(inventory_file, self.path)
            self.send_response(reply.status)
            self.send_header("Content-Type", reply.content_type)
            self.send_header("Content-Length", str(len(reply.body)))
            if reply.download_name is not None:
                # Percent-encoding keeps any file name, even one with quotes or line breaks,
                # from breaking out of the header.
                name = quote(reply.download_name, safe="")
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{name}")
            self.end_headers()
            self.wfile.write(reply.body)

    return ThreadingHTTPServer((host, port), Handler)
