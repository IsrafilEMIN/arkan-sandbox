import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

from stock import export, store, web
from stock.inventory import Inventory, Item


class WebTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = Path(self.dir.name) / "inventory.json"
        items = [Item("PEN-01", "blue pen", 10, 120), Item("TAPE", "tape <wide> & clear", 2, 250)]
        store.save(Inventory(items), self.file)

    def tearDown(self):
        self.dir.cleanup()

    def test_the_home_page_is_a_table_of_items(self):
        reply = web.respond(self.file, "/")
        self.assertEqual((reply.status, reply.content_type), (HTTPStatus.OK, web.HTML))
        self.assertIn(b"<tr><td>PEN-01</td><td>blue pen</td>", reply.body)

    def test_the_home_page_links_to_the_exports(self):
        self.assertIn(b'<a href="/exports">', web.respond(self.file, "/").body)

    def test_names_are_escaped_on_the_page(self):
        self.assertIn(b"tape &lt;wide&gt; &amp; clear", web.respond(self.file, "/").body)

    def test_items_json_lists_every_item(self):
        reply = web.respond(self.file, "/items.json?fresh=1")
        self.assertEqual((reply.status, reply.content_type), (HTTPStatus.OK, web.JSON))
        skus = [item["sku"] for item in json.loads(reply.body)["items"]]
        self.assertEqual(skus, ["PEN-01", "TAPE"])

    def test_any_other_path_is_not_found(self):
        self.assertEqual(web.respond(self.file, "/admin").status, HTTPStatus.NOT_FOUND)

    def write_export(self, name, text, mtime):
        folder = export.exports_dir(self.file)
        folder.mkdir(exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")
        os.utime(folder / name, (mtime, mtime))

    def test_the_exports_page_lists_the_newest_file_first(self):
        self.write_export("stock-2026-10-11.csv", "sku\n", 1000)
        self.write_export("stock-2026-10-18.csv", "sku\n", 2000)
        reply = web.respond(self.file, "/exports")
        self.assertEqual((reply.status, reply.content_type), (HTTPStatus.OK, web.HTML))
        self.assertLess(
            reply.body.index(b'<a href="/exports/stock-2026-10-18.csv">stock-2026-10-18.csv</a>'),
            reply.body.index(b'<a href="/exports/stock-2026-10-11.csv">stock-2026-10-11.csv</a>'),
        )

    def test_the_exports_page_says_when_there_are_none(self):
        reply = web.respond(self.file, "/exports")
        self.assertEqual(reply.status, HTTPStatus.OK)
        self.assertIn(b"No exports yet", reply.body)

    def test_odd_file_names_are_escaped_on_the_exports_page(self):
        self.write_export("a <b> & c.csv", "sku\n", 1000)
        self.assertIn(
            b'<a href="/exports/a%20%3Cb%3E%20%26%20c.csv">a &lt;b&gt; &amp; c.csv</a>',
            web.respond(self.file, "/exports").body,
        )

    def test_an_export_downloads_as_csv_under_its_own_name(self):
        self.write_export("stock-2026-10-18.csv", "sku,name\nPEN-01,blue pen\n", 1000)
        reply = web.respond(self.file, "/exports/stock-2026-10-18.csv")
        self.assertEqual((reply.status, reply.content_type), (HTTPStatus.OK, web.CSV))
        self.assertEqual(reply.body, b"sku,name\nPEN-01,blue pen\n")
        self.assertEqual(reply.download_name, "stock-2026-10-18.csv")

    def test_a_link_from_the_exports_page_downloads_its_file(self):
        self.write_export("a <b> & c.csv", "sku\n", 1000)
        reply = web.respond(self.file, "/exports/a%20%3Cb%3E%20%26%20c.csv")
        self.assertEqual((reply.status, reply.download_name), (HTTPStatus.OK, "a <b> & c.csv"))

    def test_only_files_in_the_exports_folder_download(self):
        self.write_export("stock-2026-10-18.csv", "sku\n", 1000)
        (export.exports_dir(self.file) / "old").mkdir()
        (export.exports_dir(self.file) / "old" / "a.csv").write_text("sku\n")
        (export.exports_dir(self.file) / "inv.csv").symlink_to(self.file)
        for target in [
            "/exports/",
            "/exports/missing.csv",
            "/exports/../inventory.json",
            "/exports/..%2Finventory.json",
            "/exports/%2E%2E/inventory.json",
            "/exports/old",
            "/exports/old/a.csv",
            "/exports/old%2Fa.csv",
            "/exports/inv.csv",
            f"/exports/{self.file}",
            "/exports//etc/passwd",
        ]:
            with self.subTest(target=target):
                self.assertEqual(web.respond(self.file, target).status, HTTPStatus.NOT_FOUND)

    def test_the_server_refuses_a_post(self):
        server = web.make_server(self.file, "127.0.0.1", 0)
        server.RequestHandlerClass.log_message = lambda *args: None
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/"
            with urllib.request.urlopen(url) as reply:
                self.assertEqual(reply.status, 200)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(urllib.request.Request(url, data=b"x", method="POST"))
            self.assertEqual(caught.exception.code, HTTPStatus.NOT_IMPLEMENTED)
            caught.exception.close()
        finally:
            server.shutdown()
            server.server_close()

    def test_the_server_sends_a_download_as_an_attachment(self):
        self.write_export("a <b> & c.csv", "sku\n", 1000)
        server = web.make_server(self.file, "127.0.0.1", 0)
        server.RequestHandlerClass.log_message = lambda *args: None
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/exports/a%20%3Cb%3E%20%26%20c.csv"
            with urllib.request.urlopen(url) as reply:
                self.assertEqual(reply.headers["Content-Type"], web.CSV)
                self.assertEqual(
                    reply.headers["Content-Disposition"],
                    "attachment; filename*=UTF-8''a%20%3Cb%3E%20%26%20c.csv",
                )
                self.assertEqual(reply.read(), b"sku\n")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
