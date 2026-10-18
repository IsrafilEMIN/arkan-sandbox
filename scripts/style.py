"""Basic style check for the Python files given on the command line.

Rules: lines at most 100 characters, no tabs, no trailing spaces, a newline at the end.
"""

import sys

MAX_LINE = 100


def check(path: str) -> list[str]:
    problems = []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for n, line in enumerate(text.splitlines(), start=1):
        if len(line) > MAX_LINE:
            problems.append(f"{path}:{n}: line is {len(line)} characters, the limit is {MAX_LINE}")
        if "\t" in line:
            problems.append(f"{path}:{n}: tab character")
        if line != line.rstrip():
            problems.append(f"{path}:{n}: trailing whitespace")
    if text and not text.endswith("\n"):
        problems.append(f"{path}: no newline at the end of the file")
    return problems


def main(paths: list[str]) -> int:
    problems = [p for path in paths for p in check(path)]
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
