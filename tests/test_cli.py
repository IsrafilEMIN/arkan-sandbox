import contextlib
import datetime
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from stock.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = str(Path(self.dir.name) / "inventory.json")

    def tearDown(self):
        self.dir.cleanup()

    def run_stock(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--file", self.file, *args], today=datetime.date(2026, 10, 18))
        return code, out.getvalue(), err.getvalue()

    def write_items(self, *items: tuple[str, int]) -> None:
        rows = [{"sku": sku, "name": sku, "qty": qty, "price_cents": 120} for sku, qty in items]
        Path(self.file).write_text(json.dumps({"items": rows}), encoding="utf-8")

    def test_add_then_list(self):
        self.run_stock("add", "PEN-01", "blue pen", "10", "1.20")
        code, out, _ = self.run_stock("list")
        self.assertEqual(code, 0)
        self.assertEqual(out, "PEN-01     10       $1.20  blue pen\n")

    def test_receive_and_remove_print_the_new_quantity(self):
        self.run_stock("add", "PEN-01", "blue pen", "10", "1.20")
        self.assertEqual(self.run_stock("receive", "PEN-01", "5")[1], "PEN-01: 15 on hand\n")
        self.assertEqual(self.run_stock("remove", "PEN-01", "2")[1], "PEN-01: 13 on hand\n")

    def test_value_is_the_total_of_all_items(self):
        self.run_stock("add", "PEN-01", "blue pen", "3", "1.20")
        self.run_stock("add", "BOOK-A5", "a5 notebook", "2", "3.55")
        self.assertEqual(self.run_stock("value")[1], "$10.70\n")

    def test_an_error_prints_a_message_and_exits_1(self):
        code, out, err = self.run_stock("remove", "NOPE", "1")
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, "stock: no item with sku NOPE\n")

    def test_export_prints_the_path_it_wrote(self):
        self.run_stock("add", "PEN-01", "blue pen", "10", "1.20")
        code, out, _ = self.run_stock("export")
        expected = Path(self.dir.name) / "exports" / "stock-2026-10-18.csv"
        self.assertEqual((code, out), (0, f"{expected}\n"))
        self.assertTrue(expected.is_file())

    def test_list_with_no_items(self):
        self.assertEqual(self.run_stock("list")[1], "no items\n")

    def test_every_command_warns_about_each_negative_quantity_then_runs(self):
        self.write_items(("PEN-01", -3), ("BOOK-A5", 2), ("CLIP-9", -1))
        warnings = (
            f"stock: warning: CLIP-9 has a negative quantity (-1), check {self.file}\n"
            f"stock: warning: PEN-01 has a negative quantity (-3), check {self.file}\n"
        )
        export = Path(self.dir.name) / "exports" / "stock-2026-10-18.csv"
        cases = [
            (("list",), "BOOK-A5      2       $1.20  BOOK-A5\n"),
            (("value",), "-$2.40\n"),
            (("receive", "BOOK-A5", "1"), "BOOK-A5: 3 on hand\n"),
            (("remove", "BOOK-A5", "1"), "BOOK-A5: 2 on hand\n"),
            (("export",), f"{export}\n"),
            (("add", "TAPE-1", "tape", "1", "0.90"), "added TAPE-1: 1 x tape at $0.90\n"),
        ]
        for args, want_out in cases:
            with self.subTest(args=args):
                code, out, err = self.run_stock(*args)
                self.assertEqual((code, err), (0, warnings))
                self.assertTrue(out.startswith(want_out), out)

    def test_serve_warns_once_when_it_starts(self):
        self.write_items(("PEN-01", -3))
        server = mock.Mock(server_address=("127.0.0.1", 8000))
        server.serve_forever.side_effect = KeyboardInterrupt
        with mock.patch("stock.web.make_server", return_value=server):
            code, _, err = self.run_stock("serve")
        self.assertEqual(code, 0)
        self.assertEqual(
            err, f"stock: warning: PEN-01 has a negative quantity (-3), check {self.file}\n"
        )

    def test_a_failing_command_still_warns_and_exits_1(self):
        self.write_items(("PEN-01", -3))
        code, _, err = self.run_stock("remove", "NOPE", "1")
        self.assertEqual(code, 1)
        self.assertEqual(
            err,
            f"stock: warning: PEN-01 has a negative quantity (-3), check {self.file}\n"
            "stock: no item with sku NOPE\n",
        )

    def test_no_warning_when_no_quantity_is_negative(self):
        self.write_items(("PEN-01", 0), ("BOOK-A5", 2))
        self.assertEqual(self.run_stock("list")[2], "")


if __name__ == "__main__":
    unittest.main()
