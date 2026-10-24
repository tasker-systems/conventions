#!/usr/bin/env python3
"""Generate the register's per-consumer columns from each consumer's `.conventions/status.toml`.

Doctrine: doctrine/consuming.md (CONS-5). A consumer records its status for each rule beside its
own gates; this tool reads those files at each consumer's default branch (tools/consumers.toml)
and writes them into doctrine/rules.md, so the register states what the consumers' gates do rather
than what someone last copied:

    python3 -I tools/register.py generate      # rewrite doctrine/rules.md
    python3 -I tools/register.py check         # fail, naming each cell, if rules.md disagrees

Where the register and a consumer disagree, the consumer wins: it is where the gate lives. `check`
runs in the scheduled register job (.github/workflows/register.yml), so a disagreement is detected
without anyone looking; the fix is `generate` and a reviewed PR.

A consumer's column is:
  - generated, when its status.toml can be read (an unlisted rule reads `unexamined`);
  - hand-taken, kept as written, when it has not adopted but rules.md already holds a column for it
    (temper and tasker-core, until they adopt);
  - absent, when it has not adopted and has no column, or cannot be read: a private consumer
    without CONSUMERS_READ_TOKEN. The consumers block above the tables names which and why.

NOT CHECKED:
  - that a consumer's status is true of its gates: that is the consumer's own check D and its
    witnesses;
  - hand-taken columns, which no file backs until their consumer adopts.

A fetch that fails for any reason other than "not found" fails the run: an unreadable consumer is
never reported as one that has not adopted. Standard library only.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_ROW = re.compile(r"^\|\s*([A-Z]+(?:-[A-Z]+)*-[0-9]+)\s*\|")
HEADER = re.compile(r"^\|\s*Id\s*\|\s*Rule\s*\|")
SEPARATOR = re.compile(r"^\|(?:-+\|)+\s*$")
BLOCK_BEGIN = "<!-- consumers:begin -->"
BLOCK_END = "<!-- consumers:end -->"
TOKEN_ENV = "CONSUMERS_READ_TOKEN"
UNREAD = object()


@dataclass
class Registered:
    name: str
    repo: str
    branch: str
    private: bool


@dataclass
class Column:
    name: str
    source: str  # "generated", "hand-taken", "not adopted", "unread"
    detail: str
    cells: dict[str, str]
    pin: str | None = None


def load_registered(root: Path) -> list[Registered]:
    with (root / "tools" / "consumers.toml").open("rb") as handle:
        data = tomllib.load(handle)
    out = [
        Registered(c["name"], c["repo"], c.get("branch", "main"), bool(c.get("private", False)))
        for c in data.get("consumer", [])
    ]
    if not out:
        raise SystemExit("tools/consumers.toml lists no consumer; refusing an empty register")
    return out


# --------------------------------------------------------------------------------------------
# Reading consumers
# --------------------------------------------------------------------------------------------


def fetch_remote(consumer: Registered, path: str) -> bytes | object | None:
    """A file at the consumer's default branch; None when absent; UNREAD when it cannot be read
    because the consumer is private and no token was given."""
    token = os.environ.get(TOKEN_ENV, "")
    if consumer.private and not token:
        return UNREAD
    if token:
        url = f"https://api.github.com/repos/{consumer.repo}/contents/{path}?ref={consumer.branch}"
        headers = {"Accept": "application/vnd.github.raw", "Authorization": f"Bearer {token}"}
    else:
        url = f"https://raw.githubusercontent.com/{consumer.repo}/{consumer.branch}/{path}"
        headers = {}
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def fetch_local(source: Path, consumer: Registered, path: str) -> bytes | object | None:
    """The same reads from a directory, for tests: <source>/<name>/<path>; a file named UNREADABLE
    in <source>/<name> stands in for a private consumer without a token."""
    base = source / consumer.name
    if (base / "UNREADABLE").is_file():
        return UNREAD
    target = base / path
    return target.read_bytes() if target.is_file() else None


def read_columns(
    registered: list[Registered], hand: dict[str, dict[str, str]], fetch
) -> list[Column]:
    columns: list[Column] = []
    for consumer in registered:
        status = fetch(consumer, ".conventions/status.toml")
        if status is UNREAD:
            columns.append(
                Column(consumer.name, "unread", f"private; {TOKEN_ENV} was not provided", {})
            )
            continue
        if status is None:
            if consumer.name in hand:
                columns.append(
                    Column(
                        consumer.name,
                        "hand-taken",
                        "not adopted; the column is kept as written until it adopts",
                        hand[consumer.name],
                    )
                )
            else:
                columns.append(
                    Column(consumer.name, "not adopted", "every rule is unexamined there", {})
                )
            continue
        data = tomllib.loads(status.decode("utf-8"))
        rules = {str(k): str(v) for k, v in data.get("rules", {}).items()}
        pin = None
        config = fetch(consumer, ".conventions/consumer.toml")
        if isinstance(config, bytes):
            pin = tomllib.loads(config.decode("utf-8")).get("revision")
        columns.append(
            Column(
                consumer.name,
                "generated",
                f"`{consumer.repo}` `{consumer.branch}`: `.conventions/status.toml`",
                rules,
                pin if isinstance(pin, str) else None,
            )
        )
    return columns


# --------------------------------------------------------------------------------------------
# Reading and writing rules.md
# --------------------------------------------------------------------------------------------


def split_cells(line: str) -> list[str]:
    """The cells of a table row; a `\\|` inside a cell is not a separator."""
    inner = line.strip()
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") and not inner.endswith("\\|") else inner
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", inner)]


def escape(cell: str) -> str:
    return re.sub(r"(?<!\\)\|", r"\\|", cell)


def hand_columns(text: str) -> dict[str, dict[str, str]]:
    """The per-consumer cells rules.md holds today, by consumer and rule."""
    out: dict[str, dict[str, str]] = {}
    names: list[str] = []
    for line in text.splitlines():
        if HEADER.match(line):
            names = split_cells(line)[2:]
        elif RULE_ROW.match(line):
            cells = split_cells(line)
            for name, cell in zip(names, cells[2:], strict=False):
                out.setdefault(name, {})[cells[0]] = cell
    return out


def render(text: str, columns: list[Column]) -> str:
    shown = [c for c in columns if c.source in ("generated", "hand-taken")]
    out: list[str] = []
    for line in text.splitlines():
        if HEADER.match(line):
            out.append("| " + " | ".join(["Id", "Rule", *(c.name for c in shown)]) + " |")
        elif SEPARATOR.match(line) and out and HEADER.match(out[-1]):
            out.append("|" + "---|" * (2 + len(shown)))
        elif RULE_ROW.match(line):
            rule, statement = split_cells(line)[:2]
            cells = [
                escape(c.cells.get(rule, "unexamined" if c.source == "generated" else ""))
                for c in shown
            ]
            out.append("| " + " | ".join([rule, statement, *cells]) + " |")
        else:
            out.append(line)
    rendered = "\n".join(out) + "\n"
    if BLOCK_BEGIN not in rendered or BLOCK_END not in rendered:
        raise SystemExit(f"doctrine/rules.md has no {BLOCK_BEGIN} … {BLOCK_END} block")
    head, _, rest = rendered.partition(BLOCK_BEGIN)
    _, _, tail = rest.partition(BLOCK_END)
    return head + BLOCK_BEGIN + "\n" + consumers_block(columns) + BLOCK_END + tail


def consumers_block(columns: list[Column]) -> str:
    rows = "\n".join(f"| {c.name} | {c.source} | {c.detail} |" for c in columns)
    return (
        "\n**Registered consumers.** This block and the consumer columns of every table below are\n"
        "generated by [`tools/register.py`](../tools/register.py) from each consumer's\n"
        "`.conventions/status.toml`; do not edit them by hand. Where a consumer and this file\n"
        "disagree, the consumer wins: it is where the gate lives. A rule a generated column does\n"
        "not list is **unexamined** there. For tasker-contrib the baseline covers its own surfaces\n"
        "only; its templates and example apps are user-owned.\n\n"
        "| Consumer | Column | Source |\n|---|---|---|\n" + rows + "\n\n"
    )


# --------------------------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------------------------


def disagreements(current: str, expected: str, columns: list[Column]) -> list[str]:
    now = hand_columns(current)
    found: list[str] = []
    for column in columns:
        if column.source != "generated":
            continue
        rules = sorted(set(now.get(column.name, {})) | set(hand_columns(expected)[column.name]))
        for rule in rules:
            have = now.get(column.name, {}).get(rule)
            want = escape(column.cells.get(rule, "unexamined"))
            if have is None:
                found.append(f"{column.name} {rule}: no cell here; {column.name} says {want!r}")
            elif have != want:
                found.append(f"{column.name} {rule}: here {have!r}; {column.name} says {want!r}")
    if not found and current != expected:
        found.append("the consumers block or a table header differs from what generate writes")
    return found


def lag(pin: str | None) -> str:
    if not pin:
        return "pin unknown"
    result = subprocess.run(
        ["git", "rev-list", "--count", f"{pin}..HEAD"], cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"pinned at {pin[:12]}, which is not in this checkout's history"
    behind = int(result.stdout.strip())
    return f"pinned at {pin[:12]}, " + ("current" if behind == 0 else f"{behind} commit(s) behind")


def summarise(columns: list[Column], problems: list[str]) -> None:
    lines = [f"- {c.name}: {c.source} ({c.detail})" for c in columns]
    lines += [f"- {c.name}: {lag(c.pin)}" for c in columns if c.source == "generated"]
    lines += [f"- **disagrees** {p}" for p in problems]
    for line in lines:
        print(line)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("## Register against the consumers\n\n" + "\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="register.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("generate", "check"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--from", dest="source", type=Path, help="read consumers from a directory")
    args = parser.parse_args(argv)

    rules_md = args.root / "doctrine" / "rules.md"
    current = rules_md.read_text(encoding="utf-8")
    registered = load_registered(args.root)
    if args.source:
        source = args.source

        def fetch(consumer: Registered, path: str) -> bytes | object | None:
            return fetch_local(source, consumer, path)
    else:
        fetch = fetch_remote
    columns = read_columns(registered, hand_columns(current), fetch)
    expected = render(current, columns)

    if args.command == "generate":
        rules_md.write_text(expected, encoding="utf-8")
        summarise(columns, [])
        print(
            "doctrine/rules.md regenerated" if expected != current else "doctrine/rules.md current"
        )
        return 0
    problems = disagreements(current, expected, columns)
    summarise(columns, problems)
    if problems:
        print(
            f"FAIL  doctrine/rules.md disagrees with its consumers in {len(problems)} place(s); "
            "run `python3 -I tools/register.py generate` and open a PR",
            file=sys.stderr,
        )
        return 1
    print("register: every generated column agrees with its consumer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
