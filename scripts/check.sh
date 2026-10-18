#!/usr/bin/env bash
# usage: scripts/check.sh
# Runs the tests, compiles every Python file and runs the style check. Prints "ok" on success.
set -eu
cd "$(dirname "$0")/.."

mapfile -t files < <(find stock tests scripts -name '*.py' -not -path '*/__pycache__/*' | sort)

python3 -m unittest discover -s tests -t . -q
python3 -m py_compile "${files[@]}"
python3 scripts/style.py "${files[@]}"
echo ok
