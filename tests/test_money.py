import unittest

from stock.errors import InvalidPrice
from stock.money import format_money, parse_money, plain_money


class FormatMoneyTest(unittest.TestCase):
    def test_formats_dollars_and_cents(self):
        self.assertEqual(format_money(1250), "$12.50")
        self.assertEqual(format_money(199), "$1.99")

    def test_formats_a_negative_amount_with_the_sign_first(self):
        self.assertEqual(format_money(-250), "-$2.50")


class PlainMoneyTest(unittest.TestCase):
    def test_formats_a_plain_decimal_with_two_places(self):
        self.assertEqual(plain_money(1205), "12.05")
        self.assertEqual(plain_money(1200), "12.00")
        self.assertEqual(plain_money(-5), "-0.05")


class ParseMoneyTest(unittest.TestCase):
    def test_parses_dollars_and_cents(self):
        self.assertEqual(parse_money("12.50"), 1250)

    def test_accepts_a_dollar_sign(self):
        self.assertEqual(parse_money("$3.99"), 399)

    def test_parses_whole_dollars(self):
        self.assertEqual(parse_money("12"), 1200)

    def test_parses_one_decimal_place_as_tens_of_cents(self):
        self.assertEqual(parse_money("0.5"), 50)
        self.assertEqual(parse_money("2.5"), 250)

    def test_accepts_thousands_separators(self):
        self.assertEqual(parse_money("1,250.00"), 125000)
        self.assertEqual(parse_money("$12,000"), 1200000)

    def test_rejects_text_that_is_not_a_price(self):
        for text in ["", "abc", "1.234", "-1", "1.2.3", "1,25", ",100"]:
            with self.subTest(text=text):
                with self.assertRaises(InvalidPrice):
                    parse_money(text)


if __name__ == "__main__":
    unittest.main()
