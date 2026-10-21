# conventions

The shared engineering baseline for tasker-systems repositories. Today that means two Rust
workspaces — [`temper`](https://github.com/tasker-systems/temper) and
[`tasker-core`](https://github.com/tasker-systems/tasker-core) — and, later, the polyglot surfaces
around them.

The two projects grew up separately and are each strong where the other is thin. tasker-core
carries the code-level doctrine (written tenets, a phased lint table, bounded concurrency, the
distributed-systems primitives); temper carries the enforcement machinery (bite-tested tripwires,
blocking supply-chain gates, drift checks on everything generated). This repository is where the
two halves meet, so that a rule written once is enforced everywhere it claims to be.

## The one idea

**A rule that is written down is either enforced by a named gate, or says why it is not.** Every
rule here has an id, and [`doctrine/rules.md`](doctrine/rules.md) records, per consuming repo,
which gate enforces it — or that it is convention-only and why. A rule whose status is unknown is a
hole, not a default.

## Layout

```
doctrine/        the stance, in prose — why each rule exists
  tenets.md        the short list everything else follows from
  rules.md         the rule register: id, statement, enforcement per repo
  rust.md          lints, unsafe, errors, toolchain
  supply-chain.md  dependencies, advisories, licenses, Actions, toolchain inputs
  security.md      credentials, redaction, SQL, auth posture
  concurrency.md   bounded resources, contained failure, coordination in the database
  tripwires.md     how a repo-specific guard is written, tested and wired
  agent-guidance.md how a consuming repo's agent guidance is shaped
rust/            canonical config a consuming repo adopts
  workspace-lints.toml   the [workspace.lints] table
  clippy.toml            disallowed methods and thresholds
  deny.toml              cargo-deny: sources, licenses, bans
  audit.toml             the shape of a reviewed advisory-ignore list
```

Still to come, each its own change: the tripwire harness and the portable tripwires, reusable
GitHub workflows for the stage-1 gate, the drift check a consuming repo runs against its pinned
baseline, and the agent skill projected into each repo.

## Adopting

Not yet mechanised. Until the drift check exists, a consuming repo adopts by copying the files in
`rust/` and recording the baseline commit it copied from. Once it exists, divergence from the
pinned baseline fails that repo's CI — which is the point: "the same in both repos" should be a
checked invariant, not a habit.

## Scope of v0

Rust workspaces only. Ruby, Python and TypeScript conventions are deliberately out of scope until
the Rust baseline holds in both consumers. Domain-specific guards (temper's authorization sinks,
tasker-core's state-machine rules) stay in their own repositories; this repository owns the *shape*
of a guard, not every guard.

The goal this repository serves, its clauses and their coverage, live in the `+tasker-systems/conventions`
context in Temper.
