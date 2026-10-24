"""Bite tests for tools/conventions.py (TW-5): every check is shown red on its violation.

Each test builds a throwaway baseline (a git repository holding this checkout's projected files)
and a consumer adopted from it with `bump --init`, then breaks one thing and runs `check`.

    python3 -I -m unittest discover -s tools/tests -v
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "conventions.py"
PROJECTED = (
    "README.md",
    "LICENSE",
    "doctrine",
    "rust",
    "python",
    "typescript",
    "skill",
    "tools/conventions.py",
    "tools/slots.toml",
)
GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}
SKILL = ".claude/skills/tasker-systems-conventions"


def git(cwd: Path, *args: str) -> str:
    env = {**os.environ, **GIT_ENV}
    result = subprocess.run(
        ["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


class Fixture:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="conventions-test-")
        tmp = Path(self._tmp.name)
        self.baseline = tmp / "baseline"
        self.consumer = tmp / "consumer"
        self.baseline.mkdir()
        self.consumer.mkdir()
        for name in PROJECTED:
            source = REPO / name
            target = self.baseline / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        git(self.baseline, "init", "-q", "-b", "main")
        git(self.baseline, "add", "-A")
        git(self.baseline, "commit", "-q", "-m", "baseline")
        self.sha = git(self.baseline, "rev-parse", "HEAD")
        (self.consumer / "AGENTS.md").write_text(f"Conventions: see `{SKILL}`.\n")
        result = self.run("bump", "--init", "demo", "--revision", "main")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "first projection" in result.stdout, result.stdout

    def run(self, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
        return subprocess.run(
            [
                sys.executable,
                "-I",
                str(TOOL),
                command,
                "--root",
                str(self.consumer),
                "--baseline-repo",
                str(self.baseline),
                *args,
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def check(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self.run("check", *args)

    def write(self, rel: str, text: str) -> None:
        path = self.consumer / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def append(self, rel: str, text: str) -> None:
        path = self.consumer / rel
        path.write_text(path.read_text() + text)

    def adopt(self, canonical: str, path: str, mode: str, **extra: str) -> None:
        lines = [f'canonical = "{canonical}"', f'path = "{path}"', f'mode = "{mode}"']
        lines += [f'{k} = "{v}"' for k, v in extra.items()]
        config = self.consumer / ".conventions" / "consumer.toml"
        text = config.read_text()
        head, sep, tail = text.partition("[guidance]")
        config.write_text(head + "[[adopted]]\n" + "\n".join(lines) + "\n\n" + sep + tail)

    def canonical(self, rel: str) -> str:
        return (REPO / rel).read_text()

    def close(self) -> None:
        self._tmp.cleanup()


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.f = Fixture()

    def tearDown(self) -> None:
        self.f.close()

    def assert_passes(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_fails(self, result: subprocess.CompletedProcess[str], needle: str) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(needle, result.stderr)


class CleanConsumer(Base):
    def test_fresh_adoption_passes_and_reports_no_lag(self) -> None:
        result = self.f.check()
        self.assert_passes(result)
        self.assertIn("current main", result.stdout)

    def test_offline_says_b_and_c_did_not_run(self) -> None:
        result = self.f.check("--offline")
        self.assert_passes(result)
        self.assertIn("B: not run (--offline)", result.stdout)
        self.assertIn("C: not run (--offline)", result.stdout)


class CheckB(Base):
    def test_hand_edited_projection_fails(self) -> None:
        self.f.append(".conventions/baseline/doctrine/tenets.md", "\nedited\n")
        self.assert_fails(self.f.check(), "doctrine/tenets.md differs from the pinned commit")

    def test_extra_file_in_projection_fails(self) -> None:
        self.f.write(".conventions/baseline/doctrine/extra.md", "x\n")
        self.assert_fails(self.f.check(), "extra.md is not in the baseline at the pin")

    def test_missing_file_in_projection_fails(self) -> None:
        (self.f.consumer / ".conventions/baseline/doctrine/tenets.md").unlink()
        self.assert_fails(self.f.check(), "tenets.md is missing from the projection")

    def test_unreachable_baseline_fails_closed(self) -> None:
        result = self.f.run("check", "--baseline-repo", str(self.f.baseline / "nope"))
        # The later --baseline-repo wins in argparse; the fetch fails and B must go red.
        self.assert_fails(result, "could not fetch the baseline")

    def test_pin_that_is_a_branch_name_fails(self) -> None:
        config = self.f.consumer / ".conventions/consumer.toml"
        config.write_text(config.read_text().replace(self.f.sha, "main"))
        self.assert_fails(self.f.check(), "full 40-character commit SHA")

    def test_pin_not_on_main_fails(self) -> None:
        git(self.f.baseline, "checkout", "-q", "-b", "side")
        (self.f.baseline / "doctrine/side.md").write_text("side\n")
        git(self.f.baseline, "add", "-A")
        git(self.f.baseline, "commit", "-q", "-m", "side")
        side = git(self.f.baseline, "rev-parse", "HEAD")
        git(self.f.baseline, "checkout", "-q", "main")
        config = self.f.consumer / ".conventions/consumer.toml"
        config.write_text(config.read_text().replace(self.f.sha, side))
        self.assert_fails(self.f.check(), "is not a commit on the baseline's main")


class CheckC(Base):
    def test_lag_is_reported_and_does_not_fail(self) -> None:
        (self.f.baseline / "doctrine/new.md").write_text("new\n")
        git(self.f.baseline, "add", "-A")
        git(self.f.baseline, "commit", "-q", "-m", "next")
        result = self.f.check()
        self.assert_passes(result)
        self.assertIn("1 commit(s)", result.stdout)


class CheckA(Base):
    def test_exact_copy_passes_and_change_fails(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "exact")
        self.f.write("ruff.toml", "# our comment\n" + self.f.canonical("python/ruff.toml"))
        self.assert_passes(self.f.check("--offline"))
        self.f.write("ruff.toml", self.f.canonical("python/ruff.toml").replace("py311", "py39"))
        self.assert_fails(self.f.check("--offline"), "ruff.toml: target-version")

    def test_list_order_does_not_matter(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "exact")
        canonical = self.f.canonical("python/ruff.toml")
        self.f.write("ruff.toml", canonical.replace('"E", "W",', '"W", "E",'))
        self.assert_passes(self.f.check("--offline"))
        self.f.write("ruff.toml", canonical.replace('"E", "W",', '"W",'))
        self.assert_fails(self.f.check("--offline"), "lint.select")

    def test_exception_covers_a_difference_and_must_have_a_reason(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "exact")
        self.f.write("ruff.toml", self.f.canonical("python/ruff.toml").replace("py311", "py39"))
        self.f.write(
            ".conventions/exceptions.toml",
            '[[exception]]\npath = "ruff.toml"\nkey = "target-version"\nreason = "py39 floor"\n',
        )
        self.assert_passes(self.f.check("--offline"))
        self.f.write(
            ".conventions/exceptions.toml",
            '[[exception]]\npath = "ruff.toml"\nkey = "target-version"\nreason = ""\n',
        )
        self.assert_fails(self.f.check("--offline"), "has no reason")

    def test_dead_exception_fails(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "exact")
        self.f.write("ruff.toml", self.f.canonical("python/ruff.toml"))
        self.f.write(
            ".conventions/exceptions.toml",
            '[[exception]]\npath = "ruff.toml"\nkey = "target-version"\nreason = "stale"\n',
        )
        self.assert_fails(self.f.check("--offline"), "matches no difference")

    def test_extends_toml_allows_additions_and_refuses_overrides(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "extends")
        self.f.write(
            "ruff.toml",
            'extend = ".conventions/baseline/python/ruff.toml"\n[lint]\nextend-select = ["D"]\n',
        )
        self.assert_passes(self.f.check("--offline"))
        self.f.append("ruff.toml", "")
        self.f.write(
            "ruff.toml",
            'extend = ".conventions/baseline/python/ruff.toml"\nline-length = 120\n',
        )
        self.assert_fails(self.f.check("--offline"), "line-length")

    def test_extends_must_reference_the_projection(self) -> None:
        self.f.adopt("python/ruff.toml", "ruff.toml", "extends")
        self.f.write("ruff.toml", 'extend = "somewhere/else.toml"\n')
        self.assert_fails(self.f.check("--offline"), "does not reference")

    def test_extends_jsonc_with_comments_and_a_list(self) -> None:
        self.f.adopt("typescript/tsconfig.base.json", "app/tsconfig.json", "extends")
        self.f.write(
            "app/tsconfig.json",
            '{\n  // the framework base first\n  "extends": ["./.svelte-kit/tsconfig.json",\n'
            '    "../.conventions/baseline/typescript/tsconfig.base.json"],\n'
            '  /* our own */ "compilerOptions": { "allowJs": true, },\n}\n',
        )
        self.assert_passes(self.f.check("--offline"))
        self.f.write(
            "app/tsconfig.json",
            '{ "extends": "../.conventions/baseline/typescript/tsconfig.base.json",\n'
            '  "compilerOptions": { "strict": false } }\n',
        )
        self.assert_fails(self.f.check("--offline"), "compilerOptions.strict")

    def test_table_mode_on_a_single_package(self) -> None:
        self.f.adopt(
            "rust/workspace-lints.toml",
            "Cargo.toml",
            "table",
            table="lints",
            canonical_table="workspace.lints",
        )
        lints = self.f.canonical("rust/workspace-lints.toml").replace(
            "[workspace.lints.", "[lints."
        )
        self.f.write("Cargo.toml", '[package]\nname = "demo"\nversion = "0.1.0"\n\n' + lints)
        self.assert_passes(self.f.check("--offline"))
        self.f.write(
            "Cargo.toml",
            self.f.consumer.joinpath("Cargo.toml")
            .read_text()
            .replace('dbg_macro = "warn"', 'dbg_macro = "allow"'),
        )
        self.assert_fails(self.f.check("--offline"), "lints.clippy.dbg_macro")

    def test_superset_allows_slots_only(self) -> None:
        self.f.adopt("rust/deny.toml", "deny.toml", "superset")
        canonical = self.f.canonical("rust/deny.toml")
        self.f.write("deny.toml", canonical + '\n[[bans.skip]]\nname = "syn"\nversion = "1"\n')
        # [[bans.skip]] after [bans] is a TOML array of tables under bans: a declared slot.
        self.assert_passes(self.f.check("--offline"))
        self.f.write("deny.toml", canonical.replace('"Zlib",', ""))
        self.assert_fails(self.f.check("--offline"), "licenses.allow")
        self.f.write("deny.toml", canonical.replace("[bans]", '[bans]\nhighlight = "all"'))
        self.assert_fails(self.f.check("--offline"), "not a declared local slot")


class CheckD(Base):
    def test_gated_status_must_name_an_existing_gate(self) -> None:
        self.f.write(
            ".github/workflows/ci.yml", "name: CI\non: push\njobs:\n  lint:\n    runs-on: x\n"
        )
        status = '[rules]\n"RUST-FMT-1" = "gated: .github/workflows/ci.yml#lint"\n'
        self.f.write(".conventions/status.toml", status)
        self._rebump()
        self.assert_passes(self.f.check("--offline"))
        self.f.write(".conventions/status.toml", status.replace("#lint", "#nope"))
        self._rebump()
        self.assert_fails(self.f.check("--offline"), "names gate")

    def test_unknown_rule_and_unknown_word_fail(self) -> None:
        self.f.write(".conventions/status.toml", '[rules]\n"NOPE-1" = "practiced"\n')
        self._rebump()
        self.assert_fails(self.f.check("--offline"), "NOPE-1 is not a rule")
        self.f.write(".conventions/status.toml", '[rules]\n"RUST-FMT-1" = "mostly"\n')
        self._rebump()
        self.assert_fails(self.f.check("--offline"), "unknown status word")

    def _rebump(self) -> None:
        result = self.f.run("bump", "--revision", self.f.sha)
        self.assertEqual(result.returncode, 0, result.stderr)


class CheckE(Base):
    def test_entry_must_link_the_skill(self) -> None:
        self.f.write("AGENTS.md", "No link here.\n")
        self.assert_fails(self.f.check("--offline"), "does not link the projected skill")

    def test_hand_edited_skill_fails(self) -> None:
        self.f.append(f"{SKILL}/SKILL.md", "\nedited\n")
        self.assert_fails(self.f.check("--offline"), "is not the skill rendered")

    def test_status_change_without_rebump_makes_the_skill_stale(self) -> None:
        self.f.write(".conventions/status.toml", '[rules]\n"RUST-FMT-1" = "practiced"\n')
        self.assert_fails(self.f.check("--offline"), "is not the skill rendered")
        self.assert_passes(self.f.run("bump", "--revision", self.f.sha))
        self.assert_passes(self.f.check("--offline"))
        skill = (self.f.consumer / SKILL / "SKILL.md").read_text()
        self.assertIn("| RUST-FMT-1 | practiced |", skill)


class Bump(Base):
    def test_bump_reports_rule_changes(self) -> None:
        rules = self.f.baseline / "doctrine/rules.md"
        rules.write_text(rules.read_text() + "| NEW-1 | A new rule | uncovered | uncovered |\n")
        git(self.f.baseline, "commit", "-q", "-am", "add a rule")
        result = self.f.run("bump", "--revision", "main")
        self.assert_passes(result)
        self.assertIn("rule added: NEW-1", result.stdout)

    def test_bump_refuses_a_revision_not_on_main(self) -> None:
        result = self.f.run("bump", "--revision", "0" * 40)
        self.assertNotEqual(result.returncode, 0)


class CheckF(Base):
    """A pin move that changes a rule is one act: the statuses are reviewed in the same commit."""

    def move_main(self, rules_edit: str) -> str:
        rules = self.f.baseline / "doctrine/rules.md"
        text = rules.read_text()
        if rules_edit == "add-rule":
            text += "| NEW-1 | A new rule | uncovered | uncovered |\n"
        elif rules_edit == "status-cell":
            # A consumer column moves (it is generated); the rule itself does not.
            text = text.replace(
                "| RUST-FMT-1 | rustfmt defaults, checked in CI | gated:",
                "| RUST-FMT-1 | rustfmt defaults, checked in CI | partial: moved; was gated:",
            )
        rules.write_text(text)
        git(self.f.baseline, "commit", "-q", "-am", rules_edit)
        return git(self.f.baseline, "rev-parse", "HEAD")

    def test_adoption_is_reviewed_at_its_pin(self) -> None:
        self.assert_passes(self.f.check())

    def test_rule_change_fails_until_the_statuses_are_reviewed(self) -> None:
        sha = self.move_main("add-rule")
        self.assert_passes(self.f.run("bump", "--revision", "main"))
        self.assert_fails(self.f.check(), f"but the pin is {sha}")
        status = self.f.consumer / ".conventions/status.toml"
        status.write_text(status.read_text().replace(self.f.sha, sha))
        self.assert_passes(self.f.check())

    def test_a_moved_status_column_is_not_a_rule_change(self) -> None:
        self.move_main("status-cell")
        result = self.f.run("bump", "--revision", "main")
        self.assertIn("no rule was added, removed or changed", result.stdout)
        self.assert_passes(self.f.check())

    def test_missing_reviewed_at_fails(self) -> None:
        status = self.f.consumer / ".conventions/status.toml"
        status.write_text(
            "".join(x for x in status.read_text().splitlines(True) if "reviewed_at =" not in x)
        )
        self.assert_fails(self.f.check("--offline"), "status.toml has no `reviewed_at`")


class Witness(Base):
    """`witness` holds on a well-formed consumer, and goes red when a check it witnesses is off."""

    WORKFLOW = (
        "name: CI\non: pull_request\njobs:\n  conventions:\n    runs-on: x\n    steps:\n"
        "      - run: python3 -I .conventions/baseline/tools/conventions.py check\n"
    )

    def setUp(self) -> None:
        super().setUp()
        # The pin needs a parent on main, for the lag case.
        (self.f.baseline / "doctrine/next.md").write_text("next\n")
        git(self.f.baseline, "add", "-A")
        git(self.f.baseline, "commit", "-q", "-m", "next")
        self.f.adopt("python/ruff.toml", "ruff.toml", "extends")
        self.f.write("ruff.toml", 'extend = ".conventions/baseline/python/ruff.toml"\n')
        self.f.adopt("rust/clippy.toml", "clippy.toml", "exact")
        self.f.write("clippy.toml", self.f.canonical("rust/clippy.toml"))
        self.f.adopt("rust/deny.toml", "deny.toml", "superset")
        self.f.write("deny.toml", self.f.canonical("rust/deny.toml"))
        self.f.adopt("rust/workspace-lints.toml", "Cargo.toml", "table", table="workspace.lints",
                     canonical_table="workspace.lints")  # fmt: skip
        self.f.write(
            "Cargo.toml",
            "[workspace]\nmembers = []\n\n" + self.f.canonical("rust/workspace-lints.toml"),
        )
        self.f.adopt("rust/audit.toml", ".cargo/audit.toml", "superset")
        self.f.write(".cargo/audit.toml", '[advisories]\nignore = ["RUSTSEC-2023-0071"]\n')
        self.f.adopt("typescript/tsconfig.base.json", "app/tsconfig.json", "extends")
        self.f.write(
            "app/tsconfig.json",
            '{ "extends": "../.conventions/baseline/typescript/tsconfig.base.json" }\n',
        )
        self.f.write(".github/workflows/ci.yml", self.WORKFLOW)
        self.f.write(".conventions/status.toml", '[rules]\n"RUST-FMT-1" = "uncovered"\n')
        self.assert_passes(self.f.run("bump", "--revision", "main"))
        self.assert_passes(self.f.check())

    def witness(self, tool: Path = TOOL) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(tool), "witness", "--root", str(self.f.consumer),
             "--baseline-repo", str(self.f.baseline)],
            capture_output=True, text=True, check=False,
        )  # fmt: skip

    def mutated(self, old: str, new: str) -> Path:
        text = TOOL.read_text()
        self.assertEqual(text.count(old), 1, old)
        path = self.f.baseline.parent / "mutated" / "conventions.py"
        path.parent.mkdir()
        path.write_text(text.replace(old, new))
        return path

    def test_witness_holds_on_a_well_formed_consumer(self) -> None:
        result = self.witness()
        self.assert_passes(result)
        self.assertIn("cases held", result.stdout)
        for case in (
            "ruff.toml overrides canonical",
            "clippy.toml adds a key the baseline does not hold",
            "Cargo.toml overrides canonical workspace.lints.rust.unsafe_code",
            "deny.toml overrides canonical graph.all-features",
            ".cargo/audit.toml adds a key the baseline does not hold",
            "app/tsconfig.json stops referencing the projection",
            "a reasoned exception covers the divergence it records stays green",
            "AGENTS.md stops linking the skill",
            "a pin behind the baseline's main is named as lag",
        ):
            self.assertIn(case, result.stdout)

    def test_witness_fails_when_check_f_is_disabled(self) -> None:
        tool = self.mutated(
            "    reviewed = load_reviewed_at(consumer.root)\n",
            "    return\n    reviewed = load_reviewed_at(consumer.root)\n",
        )
        result = self.witness(tool)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reviewed against another revision than the pin was accepted", result.stderr)
        self.assertIn("name no revision they were reviewed against was accepted", result.stderr)

    def test_witness_fails_when_the_exception_reason_rule_is_disabled(self) -> None:
        tool = self.mutated(
            '            report.fail("A", f"exceptions.toml exception[{index}] has no reason")\n',
            "            pass\n",
        )
        result = self.witness(tool)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("an exception carries no reason was accepted", result.stderr)

    def test_witness_refuses_a_secret_in_the_conventions_job(self) -> None:
        self.f.write(
            ".github/workflows/ci.yml",
            self.WORKFLOW + "        env:\n          T: ${{ secrets.READ }}\n",
        )
        result = self.witness()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            ".github/workflows/ci.yml#conventions runs the check and references no", result.stderr
        )

    def test_witness_refuses_a_consumer_whose_ci_never_runs_the_check(self) -> None:
        self.f.write(".github/workflows/ci.yml", self.WORKFLOW.replace(" check", " --help"))
        result = self.witness()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no workflow job runs `conventions.py check`", result.stderr)


class TomlDump(unittest.TestCase):
    def test_round_trips_what_tomllib_reads(self) -> None:
        sys.path.insert(0, str(TOOL.parent))
        try:
            import conventions
        finally:
            sys.path.pop(0)

        for rel in ("rust/deny.toml", "rust/clippy.toml", "rust/workspace-lints.toml",
                    "python/ruff.toml", "tools/slots.toml"):  # fmt: skip
            data = tomllib.loads((REPO / rel).read_text())
            self.assertEqual(tomllib.loads(conventions.toml_dumps(data)), data, rel)
        odd = {"a": {"b.c": 'q"uote\u00e9\x7f', "e": [], "f": {}, "g": [{"h": 1.5}]}}
        self.assertEqual(tomllib.loads(conventions.toml_dumps(odd)), odd)


if __name__ == "__main__":
    unittest.main()


class RepoChecks(unittest.TestCase):
    """check-register.py and check-links.py, run against a scratch copy so they can be broken."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="conventions-repo-")
        self.root = Path(self._tmp.name)
        shutil.copytree(
            REPO,
            self.root,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_script(self, name: str) -> subprocess.CompletedProcess[str]:
        script = self.root / "tools" / name
        return subprocess.run(
            [sys.executable, "-I", str(script)], capture_output=True, text=True, check=False
        )

    def test_register_complete_passes(self) -> None:
        result = self.run_script("check-register.py")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rule_without_a_row_fails(self) -> None:
        rules = self.root / "doctrine" / "rules.md"
        text = rules.read_text()
        rules.write_text(
            "\n".join(row for row in text.splitlines() if not row.startswith("| CONS-8 "))
        )
        result = self.run_script("check-register.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONS-8 (consuming.md) has no row", result.stderr)

    def test_row_without_a_rule_fails(self) -> None:
        rules = self.root / "doctrine" / "rules.md"
        rules.write_text(rules.read_text() + "| GHOST-1 | nothing | uncovered | uncovered |\n")
        result = self.run_script("check-register.py")
        self.assertIn("GHOST-1 has a register row but no doctrine", result.stderr)

    def test_broken_link_fails(self) -> None:
        self.assertEqual(self.run_script("check-links.py").returncode, 0)
        (self.root / "doctrine" / "tenets.md").unlink()
        result = self.run_script("check-links.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tenets.md", result.stderr)
