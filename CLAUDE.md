# CLAUDE.md

Guidance for agents working **in this repository**. Agents working in a *consuming* repository
receive this baseline through that repository's own guidance (and, later, a projected skill) — not
from this file.

## What this repository is

The shared engineering baseline for tasker-systems repos. See [README.md](README.md). It is not a
Rust product: nothing here compiles into a binary. Its outputs are doctrine (`doctrine/`) and
canonical configuration (`rust/`, `python/`, `typescript/`) that consuming repos adopt. It is
public; its consumers are listed in [README.md](README.md).

## Rules for changing it

- **Every rule has an id and an enforcement status.** Adding a rule to any `doctrine/*.md` file
  means adding its row to [`doctrine/rules.md`](doctrine/rules.md) in the same change, with each
  consumer's status stated: the gate that enforces it, `convention` (with why), or `uncovered`.
  Never leave a status blank — an unstated status reads as coverage.
- **Doctrine states the why beside the rule.** A rule without its reason gets followed to the
  letter and broken in spirit. Keep the reason short, but keep it.
- **Canonical config (`rust/`, `python/`, `typescript/`) must be valid as shipped.** A change to a
  config file is checked against a scratch workspace (or a consumer) before it lands; say how in
  the PR.
- **A consumer runs what it pinned.** `tools/conventions.py` is executed from consumers'
  projections, so a change to it changes their verdict only when they move their pin. Change its
  behaviour together with its bite tests in `tools/tests/`, and keep it standard-library only.
- **An external guide enters through a ledger.** A rule taken from a published style guide is
  restated in doctrine with our id and our reason, and [`sources/`](sources/) records the guide's
  verdict per section (adopted, adapted, covered, rejected, and why). Read the ledger before
  proposing a rule from a guide that has one; a rejection there is a decision, not an oversight.
- **Don't import a consumer's domain.** Generalise a pattern; leave its temper- or
  tasker-core-specific content where it lives.
- **No process artifacts here.** Specs, plans and reviews for this repo go to
  `tasker-systems/temper-artifacts` like temper's do; session records go to Temper's
  `+tasker-systems/conventions` context.

## Commits and PRs

Conventional commits (`docs:`, `feat:`, `fix:`, `chore:`). PR body: what, why, how it was
verified. No session narrative.
