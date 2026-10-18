# stock

A small command-line inventory for one shop: what is on the shelves, how many, and what it is worth.

Python 3.11 or later, standard library only. There is nothing to install.

## use

```
python3 -m stock add PEN-01 "blue pen" 10 1.20
python3 -m stock receive PEN-01 24
python3 -m stock remove PEN-01 3
python3 -m stock list
python3 -m stock value
```

The inventory lives in `inventory.json` in the current folder. Use `--file <path>`, or set
`STOCK_FILE`, to keep it somewhere else.

## develop

```
scripts/check.sh
```

runs the tests, compiles every file and runs the style check. It prints `ok` when all pass.
