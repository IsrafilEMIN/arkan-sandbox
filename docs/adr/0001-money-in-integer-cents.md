# 0001: money is integer cents

## Status

Accepted.

## Context

Prices come in as text like `2.50` and go out as text like `$2.50`. Floats cannot hold most cent amounts exactly, so sums of floats drift (`0.1 + 0.2 != 0.3`), and a stock value that is off by a cent is wrong.

## Decision

Inside the program every amount of money is an `int` number of cents. Text becomes cents only in `money.parse_money`, and cents become text only in `money.format_money`. No other code converts money, and no code holds money in a `float`.

## Consequences

Sums are exact. A new place that shows or reads money calls the two helpers; it never formats or parses money by hand.
