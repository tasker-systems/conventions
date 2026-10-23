# Google Shell style guide — ledger

Source: [google/styleguide `shellguide.md`](https://github.com/google/styleguide/blob/gh-pages/shellguide.md),
read 2026-10-23. CC-BY 3.0, © Google; restated, not copied. Ledger format:
[`../README.md`](../README.md).

Google's guide is about readable utility scripts. Ours carry CI gates and tripwires, so the rules we
take are the ones that keep a script from passing when it should fail. On strict mode, portability
and testing shell, the guide is silent and our doctrine goes further.

| Guide section | Verdict | Our rule | Note |
|---|---|---|---|
| Which shell: bash only | adopt | SH-1 | `sh` only where a platform forces it; no zsh |
| Shebang `#!/bin/bash` | adapt | SH-1 | `#!/usr/bin/env bash` — macOS `/bin/bash` is 3.2 |
| Set options with `set`, not in the shebang | covered | SH-2 | |
| (silent) `set -euo pipefail` | — | SH-2 | Ours; Google does not mandate it |
| When to use shell; rewrite beyond ~100 lines | adapt | SH-7 | Intent kept (logic moves out); the line count rejected |
| ShellCheck | adopt | SH-3 | Gated in CI, ratcheting from `-S warning` to `-S info` |
| `$(command)`, not backticks | adopt | SH-4 | SC2006 enabled explicitly; it is style severity |
| Quoting | adopt | SH-3 | SC2086/SC2048/SC2068 via the ratchet |
| Arrays for lists of arguments; avoid `eval` | adopt | SH-5 | `eval "$(tool --print-env)"` is the one allowed form |
| `[[ … ]]` over `[ … ]` | reject | — | Preferred, not ruled; quoting rules catch the bug class |
| Arithmetic with `(( ))` | reject | — | Low value; note `(( i++ ))` exits under `set -e` when `i` is 0 |
| Pipes into `while` (subshell variables) | adopt | SH-3 | SC2030/SC2031 |
| Errors to STDERR | covered | — | Practiced (80 files in temper) |
| File and function header comments | adapt | TW-1 | Our tripwire header (why, and what is NOT CHECKED) does more |
| `main` function | reject | — | Taste |
| Naming, `readonly`, `local` | reject | — | Low value |
| Libraries `.sh`, not executable | adopt | SH-1 | Also defines who is exempt from SH-2 |
| 2-space indent, 80 columns (shfmt) | reject | — | Would reformat everything, fix nothing; deferred |
| `TODO(user)` format | reject | — | Google-internal |
| (silent) GNU vs BSD portability | — | SH-6 | Ours, from temper's `sed -i` breakage |
