"""Money is integer cents inside the program. These turn it into text and back."""

import re

from stock.errors import InvalidPrice

_PRICE = re.compile(r"\d+(\.\d{1,2})?")


def format_money(cents: int) -> str:
    """Format integer cents as dollars, e.g. 1250 -> "$12.50"."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 10}.{cents % 100}"


def plain_money(cents: int) -> str:
    """Format integer cents as a plain decimal for a spreadsheet, e.g. 1205 -> "12.05"."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def parse_money(text: str) -> int:
    """Parse "12.50", "$12.50", "12" or "0.5" into integer cents."""
    cleaned = text.strip().removeprefix("$")
    if not _PRICE.fullmatch(cleaned):
        raise InvalidPrice(text)
    dollars, _, frac = cleaned.partition(".")
    return int(dollars) * 100 + int(frac.ljust(2, "0"))
