"""Bite tests for tools/register.py (TW-5): the register is generated from its consumers, and a
disagreement between the two is refused by name.

Each test copies this checkout's doctrine/ and tools/ into a scratch root and reads consumers from a
directory (`--from`) instead of GitHub, so it can break either side.

    python3 -I -m unittest discover -s tools/tests -v
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATUS = """reviewed_at = "0000000000000000000000000000000000000000"
[rules]
RUST-FMT-1 = "gated: .github/workflows/ci.yml#lint"
SC-ADV-1 = "partial: audit runs; `|| true` in the release job"
"""


class Register(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="conventions-register-")
        tmp = Path(self._tmp.name)
        self.root = tmp / "root"
        self.source = tmp / "consumers"
        for name in ("doctrine", "tools"):
            shutil.copytree(
                REPO / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__")
            )
        self.consumer("temper-contrib", STATUS)
        (self.source / "storyteller").mkdir(parents=True)
        (self.source / "storyteller" / "UNREADABLE").write_text("")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def consumer(self, name: str, status: str) -> None:
        path = self.source / name / ".conventions" / "status.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(status)

    def run_tool(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-I",
                str(self.root / "tools" / "register.py"),
                command,
                "--root",
                str(self.root),
                "--from",
                str(self.source),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def rules(self) -> str:
        return (self.root / "doctrine" / "rules.md").read_text()

    def row(self, rule: str) -> str:
        return next(x for x in self.rules().splitlines() if x.startswith(f"| {rule} |"))

    def test_generate_writes_the_consumer_column_and_check_then_passes(self) -> None:
        self.assertEqual(self.run_tool("generate").returncode, 0)
        self.assertIn("| gated: .github/workflows/ci.yml#lint |", self.row("RUST-FMT-1"))
        # A rule the consumer does not list is unexamined there, never blank.
        self.assertTrue(self.row("RUST-LINT-1").endswith("| unexamined |"))
        result = self.run_tool("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_pipe_in_a_status_stays_inside_its_cell(self) -> None:
        self.run_tool("generate")
        self.assertIn(r"`\|\| true` in the release job |", self.row("SC-ADV-1"))
        self.assertEqual(self.run_tool("check").returncode, 0)

    def test_a_status_changed_in_the_consumer_is_refused_by_name(self) -> None:
        self.run_tool("generate")
        self.consumer(
            "temper-contrib", STATUS.replace("gated: .github/workflows/ci.yml#lint", "uncovered")
        )
        result = self.run_tool("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "temper-contrib RUST-FMT-1: here 'gated: .github/workflows/ci.yml#lint'", result.stdout
        )

    def test_a_hand_edit_to_a_generated_cell_is_refused_by_name(self) -> None:
        self.run_tool("generate")
        rules = self.root / "doctrine" / "rules.md"
        rules.write_text(
            rules.read_text().replace(
                "| gated: .github/workflows/ci.yml#lint |", "| gated: hoped for |"
            )
        )
        result = self.run_tool("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("temper-contrib RUST-FMT-1: here 'gated: hoped for'", result.stdout)

    def test_a_consumer_that_adopts_gains_a_column(self) -> None:
        self.run_tool("generate")
        self.consumer(
            "tasker-contrib", '[rules]\nCI-2 = "gated: .github/workflows/ci.yml#ci-success"\n'
        )
        result = self.run_tool("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tasker-contrib CI-2: no cell here", result.stdout)

    def test_unread_and_unadopted_consumers_are_named_not_guessed(self) -> None:
        self.run_tool("generate")
        text = self.rules()
        self.assertIn(
            "| storyteller | unread | private; CONSUMERS_READ_TOKEN was not provided |", text
        )
        self.assertIn("| tasker-contrib | not adopted | every rule is unexamined there |", text)
        header = next(x for x in text.splitlines() if x.startswith("| Id | Rule |"))
        self.assertNotIn("storyteller", header)
        self.assertNotIn("tasker-contrib", header)

    def test_hand_taken_columns_are_kept_until_their_consumer_adopts(self) -> None:
        before = self.row("RUST-FMT-1").split(" | ")[2]
        self.run_tool("generate")
        self.assertEqual(self.row("RUST-FMT-1").split(" | ")[2], before)
        self.assertIn("| temper | hand-taken |", self.rules())

    def test_generate_is_stable(self) -> None:
        self.run_tool("generate")
        once = self.rules()
        self.run_tool("generate")
        self.assertEqual(self.rules(), once)


if __name__ == "__main__":
    unittest.main()
