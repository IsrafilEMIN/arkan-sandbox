# Coding standards

`scripts/check.sh` enforces the mechanical rules (tests pass, every file compiles, lines at most 100 characters, no tabs or trailing spaces). These are the rules it cannot check.

## Structure

- **Only the front ends talk to people.** The front ends are `stock/cli.py` (the terminal) and `stock/web.py` (the tablet). The core modules (`inventory`, `money`, `store`, `export`, `errors`) never call `print`, never write to `sys.stdout` or `sys.stderr`, and never use `warnings` or `logging`. They return values or raise a `StockError`, and the front end decides what to show.
- **Every error a user can cause is a `StockError`.** Add a subclass in `stock/errors.py` with a message a shop worker understands. Front ends catch `StockError` only; anything else is a bug and should crash loudly.
- **Money is integer cents** (ADR 0001). Read it with `parse_money`, show it with `format_money`. Never use `float` for money, and never format it by hand.

## Style

- Standard library only. Do not add a dependency.
- Type hints on every public function and method.
- Names use the words in `GLOSSARY.md`: `sku`, `qty`, `price_cents`, `value`. Do not invent synonyms.
- Comments say why, not what. A docstring says what a function returns or raises when the name does not.

## Tests

- `unittest`, one test file per module, in `tests/`.
- A test name says the behaviour: `test_remove_refuses_more_than_is_on_hand`, not `test_remove_2`.
- Test what a user sees (the returned value, the printed line, the saved file), not private helpers.
