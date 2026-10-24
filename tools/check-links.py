#!/usr/bin/env python3
"""Fail if a relative Markdown link in this repository points at a file that does not exist (DOC-4).

NOT CHECKED: external URLs, and whether a `#heading` anchor exists in its target.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)#\s]+)(#[^)]*)?\)")


def main() -> int:
    checked = 0
    broken: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for target, _ in LINK.findall(path.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target):
                continue
            checked += 1
            if not (path.parent / target).exists():
                broken.append(f"{path.relative_to(ROOT)}: {target}")
    if checked == 0:
        print("no relative links found; refusing to pass an empty scan (TW-3)", file=sys.stderr)
        return 1
    for line in broken:
        print(f"broken link: {line}", file=sys.stderr)
    if not broken:
        print(f"links ok: {checked} relative links resolve")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
