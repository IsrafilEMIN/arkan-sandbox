import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

from stock import store, web
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
        status, content_type, body = web.respond(self.file, "/")
        self.assertEqual((status, content_type), (HTTPStatus.OK, web.HTML))
        self.assertIn(b"<tr><td>PEN-01</td><td>blue pen</td>", body)

    def test_names_are_escaped_on_the_page(self):
        body = web.respond(self.file, "/")[2]
        self.assertIn(b"tape &lt;wide&gt; &amp; clear", body)

    def test_items_json_lists_every_item(self):
        status, content_type, body = web.respond(self.file, "/items.json?fresh=1")
        self.assertEqual((status, content_type), (HTTPStatus.OK, web.JSON))
        skus = [item["sku"] for item in json.loads(body)["items"]]
        self.assertEqual(skus, ["PEN-01", "TAPE"])

    def test_any_other_path_is_not_found(self):
        self.assertEqual(web.respond(self.file, "/admin")[0], HTTPStatus.NOT_FOUND)

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


if __name__ == "__main__":
    unittest.main()
