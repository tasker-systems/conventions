#!/usr/bin/env python3
"""Prove each canonical config is valid as shipped, and still bites (CLAUDE.md; tenet 2).

For each tool, a clean probe must pass under the canonical config, and a probe that violates a rule
the config claims to enforce must fail. A config that no longer parses fails the clean probe; a
config whose rule was silently dropped fails the violating probe.

| Config                                   | Tool        | Violation probe                        |
|------------------------------------------|-------------|----------------------------------------|
| rust/workspace-lints.toml + clippy.toml  | cargo clippy| `&String` parameter (ptr_arg, RUST-API-4) and `std::sync::mpsc::channel` (CONC-BOUND-1) |
| python/ruff.toml                         | ruff        | bare `except:` (E722, PY-ERR-1)        |
| typescript/biome.json                    | biome       | `any` (noExplicitAny, TS-TYPE-1)        |
| typescript/tsconfig.base.json            | tsc         | unchecked index access (TS-CFG-1)       |

Tools are taken from PATH or the commands below; CI installs exact versions.

NOT CHECKED: rust/deny.toml and rust/audit.toml beyond parsing as TOML. Running cargo-deny and
cargo-audit needs their binaries and a dependency graph; that is a consumer's own gate.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUFF = os.environ.get("RUFF", "ruff").split()
BIOME = os.environ.get("BIOME", "biome").split()
TSC = os.environ.get("TSC", "tsc").split()

failures: list[str] = []


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def expect(
    label: str, result: subprocess.CompletedProcess[str], ok: bool, needle: str = ""
) -> None:
    output = result.stdout + result.stderr
    passed = (result.returncode == 0) == ok and (not needle or needle in output)
    print(f"{'ok  ' if passed else 'FAIL'} {label}")
    if not passed:
        failures.append(label)
        print(output[-2000:], file=sys.stderr)


def rust(tmp: Path) -> None:
    ws = tmp / "rust"
    (ws / "probe" / "src").mkdir(parents=True)
    lints = (ROOT / "rust" / "workspace-lints.toml").read_text()
    (ws / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["probe"]\nresolver = "3"\n\n'
        '[workspace.package]\nedition = "2024"\nrust-version = "1.85"\n\n' + lints
    )
    shutil.copy(ROOT / "rust" / "clippy.toml", ws / "clippy.toml")
    (ws / "probe" / "Cargo.toml").write_text(
        '[package]\nname = "probe"\nversion = "0.1.0"\nedition.workspace = true\n'
        'rust-version.workspace = true\ndescription = "probe"\nlicense = "MIT"\n'
        'repository = "https://example.invalid"\nreadme = false\nkeywords = []\ncategories = []\n'
        "publish = false\n\n[lints]\nworkspace = true\n"
    )
    lib = ws / "probe" / "src" / "lib.rs"
    lib.write_text(
        "#![forbid(unsafe_code)]\n//! Probe.\n\n/// Length.\npub fn len(s: &str) -> usize {\n    s.len()\n}\n"
    )
    expect(
        "rust: clean probe passes clippy -D warnings",
        run(["cargo", "clippy", "-q", "--", "-D", "warnings"], ws),
        ok=True,
    )
    lib.write_text(
        "#![forbid(unsafe_code)]\n//! Probe.\n\n/// Length.\npub fn len(s: &String) -> usize {\n    s.len()\n}\n"
    )
    expect(
        "rust: &String is refused (ptr_arg)",
        run(["cargo", "clippy", "-q", "--", "-D", "warnings"], ws),
        ok=False,
        needle="ptr_arg",
    )
    lib.write_text(
        "#![forbid(unsafe_code)]\n//! Probe.\n\n/// Channel.\npub fn make() {\n"
        "    let (_tx, _rx) = std::sync::mpsc::channel::<u8>();\n}\n"
    )
    expect(
        "rust: unbounded channel is refused (CONC-BOUND-1)",
        run(["cargo", "clippy", "-q", "--", "-D", "warnings"], ws),
        ok=False,
        needle="CONC-BOUND-1",
    )


def python(tmp: Path) -> None:
    probe = tmp / "py"
    probe.mkdir()
    (probe / "clean.py").write_text('"""Probe."""\n\n\ndef f(x: int) -> int:\n    return x + 1\n')
    cfg = str(ROOT / "python" / "ruff.toml")
    expect(
        "python: clean probe passes",
        run([*RUFF, "check", "--no-cache", "--config", cfg, "clean.py"], probe),
        ok=True,
    )
    (probe / "bad.py").write_text(
        '"""Probe."""\n\n\ndef f() -> None:\n    try:\n        pass\n    except:\n        pass\n'
    )
    expect(
        "python: bare except is refused (E722)",
        run([*RUFF, "check", "--no-cache", "--config", cfg, "bad.py"], probe),
        ok=False,
        needle="E722",
    )
    # The tools need Python 3.11 (tomllib); the canonical floor is py310 (PY-VER-1), so they are
    # linted at their own floor rather than raising the canonical one.
    tools = [str(p) for p in sorted((ROOT / "tools").rglob("*.py"))]
    lint_tools = [*RUFF, "check", "--no-cache", "--config", cfg, "--target-version", "py311"]
    expect("python: the baseline's own tools pass", run([*lint_tools, *tools], ROOT), ok=True)
    fmt_tools = [*RUFF, "format", "--check", "--config", cfg, *tools]
    expect("python: the baseline's own tools are formatted", run(fmt_tools, ROOT), ok=True)


def biome(tmp: Path) -> None:
    probe = tmp / "biome"
    probe.mkdir()
    shutil.copy(ROOT / "typescript" / "biome.json", probe / "biome.json")
    (probe / "clean.ts").write_text("export const f = (x: number): number => x + 1;\n")
    expect(
        "biome: clean probe passes",
        run([*BIOME, "lint", "--error-on-warnings", "clean.ts"], probe),
        ok=True,
    )
    (probe / "bad.ts").write_text("export const f = (x: any): number => x + 1;\n")
    expect(
        "biome: any is refused (noExplicitAny)",
        run([*BIOME, "lint", "--error-on-warnings", "bad.ts"], probe),
        ok=False,
        needle="noExplicitAny",
    )


def tsc(tmp: Path) -> None:
    probe = tmp / "tsc"
    probe.mkdir()
    shutil.copy(ROOT / "typescript" / "tsconfig.base.json", probe / "tsconfig.base.json")
    (probe / "tsconfig.json").write_text(
        '{"extends": "./tsconfig.base.json", "compilerOptions": {"module": "esnext", '
        '"target": "es2022", "moduleResolution": "bundler", "noEmit": true}, "files": ["a.ts"]}\n'
    )
    (probe / "a.ts").write_text("export const first = (a: number[]): number | undefined => a[0];\n")
    expect("tsc: clean probe compiles", run([*TSC, "-p", "."], probe), ok=True)
    (probe / "a.ts").write_text("export const first = (a: number[]): number => a[0];\n")
    expect(
        "tsc: unchecked index access is refused (TS-CFG-1)",
        run([*TSC, "-p", "."], probe),
        ok=False,
        needle="TS2322",
    )


def toml_only() -> None:
    for name in ("deny.toml", "audit.toml"):
        try:
            with (ROOT / "rust" / name).open("rb") as handle:
                tomllib.load(handle)
            print(f"ok   rust/{name} parses (not executed; see NOT CHECKED)")
        except tomllib.TOMLDecodeError as error:
            failures.append(f"rust/{name} parses")
            print(f"FAIL rust/{name}: {error}", file=sys.stderr)


def main() -> int:
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix="conventions-valid-") as name:
        tmp = Path(name)
        for label, step in (("rust", rust), ("python", python), ("biome", biome), ("tsc", tsc)):
            if not only or label in only:
                step(tmp)
    if not only:
        toml_only()
    if failures:
        print(f"{len(failures)} check(s) failed", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
