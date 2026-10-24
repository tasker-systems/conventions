#!/usr/bin/env python3
"""Fail unless every doctrine rule id has exactly one register row, and every row a doctrine rule.

Tenet 1 is only checkable if `doctrine/rules.md` is complete: a rule written in `doctrine/*.md`
with no row reads as having no status, and a row with no doctrine is a status for nothing.

NOT CHECKED: that a row's statuses are true. That is what consumers' `status.toml` and check D are
for (doctrine/consuming.md, CONS-5).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFINED = re.compile(r"\*\*([A-Z]+(?:-[A-Z]+)*-[0-9]+) —")
ROW = re.compile(r"^\|\s*([A-Z]+(?:-[A-Z]+)*-[0-9]+)\s*\|")


def main() -> int:
    defined: dict[str, str] = {}
    for path in sorted((ROOT / "doctrine").glob("*.md")):
        if path.name == "rules.md":
            continue
        for rule in DEFINED.findall(path.read_text(encoding="utf-8")):
            if rule in defined:
                print(f"{rule} is defined in both {defined[rule]} and {path.name}", file=sys.stderr)
                return 1
            defined[rule] = path.name
    rows: list[str] = []
    for line in (ROOT / "doctrine" / "rules.md").read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if match:
            rows.append(match.group(1))
    if not defined or not rows:
        print("no rules found; refusing to pass an empty scan (TW-3)", file=sys.stderr)
        return 1
    failed = False
    for rule in sorted(set(rows)):
        if rows.count(rule) > 1:
            print(f"{rule} has {rows.count(rule)} register rows", file=sys.stderr)
            failed = True
    for rule in sorted(defined.keys() - set(rows)):
        print(f"{rule} ({defined[rule]}) has no row in doctrine/rules.md", file=sys.stderr)
        failed = True
    for rule in sorted(set(rows) - defined.keys()):
        print(f"{rule} has a register row but no doctrine", file=sys.stderr)
        failed = True
    if not failed:
        print(f"register complete: {len(defined)} rules, one row each")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
