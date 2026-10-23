# Google Python style guide — ledger

Source: [google/styleguide `pyguide.md`](https://github.com/google/styleguide/blob/gh-pages/pyguide.md),
read 2026-10-23. CC-BY 3.0, © Google; restated, not copied. Ledger format:
[`../README.md`](../README.md).

Much of the guide is configuration for Google's own tools (pylint with `g-*` checks, yapf/pyink,
pytype, absl, BUILD files). Our equivalents are ruff, `ruff format` and mypy. Wherever a ruff rule
code holds the same line, it is named.

| Guide section | Verdict | Our rule | Note |
|---|---|---|---|
| 2.1 Lint (pylint; suppress with a symbolic name) | adapt | PY-LINT-1, -2, -3 | ruff, not pylint; the "name and reason" part kept via PGH003/PGH004/RUF100. The `del unused_arg` idiom rejected: ruff's `ARG` plus a `_` prefix is the native form |
| 2.2 Imports: import modules, not names | reject | — | A monorepo-refactoring convenience; importing names is idiomatic for typed/pydantic code |
| 2.2 / 3.13 Absolute, sorted imports | adopt | PY-LINT-2 | `I`, `TID252` (`ban-relative-imports = "parents"`) |
| 2.4 Exceptions (no bare except, no catch-all, chaining, no assert for validation) | adopt | PY-ERR-1, PY-ERR-2 | `E722`, `BLE001`, `B904`, `S101` |
| 2.4 Exception names end in `Error` | reject | — | `N818` off: SDK class names match across languages |
| 2.5 Mutable global state | adopt | PY-DEF-1 | `PLW0603`, `RUF012` |
| 2.7 Comprehensions; 2.8 default iterators; 2.10 lambdas | adopt | PY-LINT-2 | `C4`, `SIM118`, `E731` |
| 2.12 Default argument values | adopt | PY-DEF-1 | `B006`, `B008` |
| 2.13 Properties; 3.15 getters and setters | reject | — | Review judgment |
| 2.14 True/False evaluations | adopt | PY-LINT-2 | `E711`, `E712` |
| 2.16 Lexical scoping (late-binding closures) | adopt | PY-DEF-1 | `B023` |
| 2.17 Decorators (avoid `staticmethod`) | reject | — | Taste, not a defect class |
| 2.18 Threading | adapt | — | Belongs with CONC-BOUND-*; Python queue bounds not yet inventoried (stated silence) |
| 2.19 Power features (metaclasses, `getattr` tricks) | reject | — | tasker-py's FFI loader and handler registry use `importlib`/`getattr` legitimately; review judges it |
| 2.20 `from __future__` imports | reject | — | Neither required nor banned; PEP 649/749 changes the picture |
| 2.21 / 3.19 Type annotations; pytype | adapt | PY-TYPE-1, PY-TYPE-2 | `mypy --strict` in place of pytype, for published packages; stub verification added, which Google does not need |
| 3.1 Semicolons; 3.14 statements | adopt | PY-LINT-2 | `E701`–`E703` |
| 3.2 Line length 80 | reject | — | 100, owned by `ruff format` |
| 3.3–3.6 Parentheses, indentation, blank lines, whitespace | covered | PY-LINT-1 | `ruff format --check` |
| 3.8 Docstrings (Google `Args:`/`Returns:`/`Raises:` format) | adapt | — | The house format where docstrings are written; gating the public API with `D` is a stated silence, pending a ruling |
| 3.10 Strings (f-strings, no `%`) | adopt | PY-LINT-2 | `UP031`, `UP032` |
| 3.10.1 Logging (constant templates) | adopt | PY-LOG-1 | `G004`, `LOG`; plus a tripwire for tasker-py's FFI log helpers, which ruff cannot see |
| 3.10.2 Error messages | reject | — | `TRY003`/`EM` too noisy for what they buy |
| 3.11 Files and resources (context managers) | adopt | PY-LINT-2 | `SIM115` |
| 3.12 TODO format (`TODO(crbug…)`) | reject | — | Google-internal |
| 3.16 Naming | adopt | PY-LINT-2 | `N` (less `N818`), `E741` |
| 3.17 Main guard | reject | — | Practiced; not worth a rule |
| 3.18 Function length | reject | — | Review judgment |
| 3.19.7 pytype disables | reject | — | No pytype |
| (silent) Generated code | — | PY-GEN-1 | Google's guide does not address it; we have two generated trees |
