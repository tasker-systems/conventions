# CLAUDE.md

Guidance for agents working **in this repository**. Agents working in a *consuming* repository
receive this baseline through that repository's own guidance (and, later, a projected skill) — not
from this file.

## What this repository is

The shared engineering baseline for tasker-systems repos. See [README.md](README.md). It is not a
Rust product: nothing here compiles into a binary. Its outputs are doctrine (`doctrine/`) and
canonical configuration (`rust/`) that consuming repos adopt.

## Rules for changing it

- **Every rule has an id and an enforcement status.** Adding a rule to any `doctrine/*.md` file
  means adding its row to [`doctrine/rules.md`](doctrine/rules.md) in the same change, with each
  consumer's status stated: the gate that enforces it, `convention` (with why), or `uncovered`.
  Never leave a status blank — an unstated status reads as coverage.
- **Doctrine states the why beside the rule.** A rule without its reason gets followed to the
  letter and broken in spirit. Keep the reason short, but keep it.
- **Config in `rust/` must be valid as shipped.** A change to a config file is checked against a
  scratch workspace (or a consumer) before it lands; say how in the PR.
- **Don't import a consumer's domain.** Generalise a pattern; leave its temper- or
  tasker-core-specific content where it lives.
- **No process artifacts here.** Specs, plans and reviews for this repo go to
  `tasker-systems/temper-artifacts` like temper's do; session records go to Temper's
  `+tasker-systems/conventions` context.

## Commits and PRs

Conventional commits (`docs:`, `feat:`, `fix:`, `chore:`). PR body: what, why, how it was
verified. No session narrative.
