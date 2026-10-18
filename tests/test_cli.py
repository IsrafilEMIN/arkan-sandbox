import contextlib
import datetime
import io
import tempfile
import unittest
from pathlib import Path

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

    def test_help_shows_examples(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn('stock add PEN-01 "blue pen" 10 1.20', out.getvalue())

    def test_list_with_no_items(self):
        self.assertEqual(self.run_stock("list")[1], "no items\n")

    def test_low_lists_items_with_5_or_fewer_fewest_first(self):
        self.run_stock("add", "PEN-01", "blue pen", "5", "1.20")
        self.run_stock("add", "TAPE-1", "tape", "2", "1.99")
        self.run_stock("add", "CLIP-9", "paper clips", "6", "0.50")
        code, out, _ = self.run_stock("low")
        self.assertEqual(code, 0)
        self.assertEqual(
            out, "TAPE-1      2       $1.99  tape\nPEN-01      5       $1.20  blue pen\n"
        )

    def test_low_at_sets_the_cutoff(self):
        self.run_stock("add", "PEN-01", "blue pen", "5", "1.20")
        self.run_stock("add", "CLIP-9", "paper clips", "10", "0.50")
        self.run_stock("add", "TAPE-1", "tape", "11", "1.99")
        out = self.run_stock("low", "--at", "10")[1]
        self.assertEqual(
            out, "PEN-01      5       $1.20  blue pen\nCLIP-9     10       $0.50  paper clips\n"
        )

    def test_low_says_so_when_nothing_is_running_low(self):
        self.run_stock("add", "PEN-01", "blue pen", "1", "1.20")
        self.assertEqual(self.run_stock("low", "--at", "0")[1], "nothing is running low\n")

    def test_low_refuses_a_negative_cutoff(self):
        code, out, err = self.run_stock("low", "--at", "-1")
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, "stock: the low stock cutoff must be 0 or more, got -1\n")


if __name__ == "__main__":
    unittest.main()
