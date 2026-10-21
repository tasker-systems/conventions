# Rust

Applies to every tasker-systems Rust workspace. Canonical config is in [`../rust/`](../rust/). Each
rule's enforcement status per repo is in [`rules.md`](rules.md).

## Lints

**RUST-LINT-1 — one workspace lint table.** The workspace `Cargo.toml` carries the table in
[`rust/workspace-lints.toml`](../rust/workspace-lints.toml), and every member crate sets
`[lints] workspace = true`. *Why:* lints configured per crate, or only on a command line, differ
between crates and between the developer's machine and CI. One table is one stance.

**RUST-LINT-2 — warnings fail the build.** Clippy and rustdoc run with `-D warnings` on every pull
request, not only before a release. *Why:* a warning that never fails is noise everyone learns to
scroll past; the lint table means nothing if its findings can merge.

**RUST-LINT-3 — `#[expect]` with a reason, never `#[allow]`.** A lint is silenced with
`#[expect(lint, reason = "...")]`. `clippy::allow_attributes` and
`clippy::allow_attributes_without_reason` enforce it. *Why:* an `#[expect]` reports when it stops
being needed, so dead suppressions surface; `#[allow]` hides a problem forever. The reason is for
the next reader, who otherwise cannot tell a considered exception from a silenced bug. (Microsoft
Pragmatic Rust Guidelines, M-LINT-OVERRIDE-EXPECT.)

**RUST-LINT-4 — adopting the table is audit-before-enforce.** When a repo first adopts the table, or
the table gains a lint, existing findings are fixed or given a reasoned `#[expect]` before the lint
gates. A blanket crate-level `#![allow]` to get green is not adoption.

## Unsafe

**RUST-UNSAFE-1 — unsafe is forbidden by default (hard rule).** Every crate root declares
`#![forbid(unsafe_code)]`. *Why:* almost all of both workspaces needs no unsafe, and `forbid`
cannot be undone by an inner attribute, so a crate that has none keeps none.

**RUST-UNSAFE-2 — an unsafe site is a registered exception.** A crate that genuinely needs unsafe
omits the `forbid`, and is listed in the repo's unsafe-exception register. The workspace table sets
`unsafe_code = "deny"`, so every site must carry `#[expect(unsafe_code, reason = "...")]`, and
`clippy::undocumented_unsafe_blocks` requires a `// SAFETY:` comment on each block. A tripwire pins
both sets — crates without `forbid`, and `expect(unsafe_code)` sites — so a new one fails CI until
it is reviewed into the register. *Why:* this is how "forbid by default" stays a hard rule while the
few legitimate sites (CPU feature probes, binding glue) stay reviewable.

**RUST-UNSAFE-3 — FFI goes through binding frameworks.** Ruby, Python and JavaScript bindings use
magnus, PyO3 and napi-rs rather than hand-written `extern` glue. *Why:* the frameworks carry the
unsafe and its review; tasker-core's three FFI crates hold no hand-written unsafe as a result.

## Errors

**RUST-ERR-1 — typed errors in libraries, `anyhow` at the edges.** Library crates define errors
with `thiserror` and a `Result<T>` alias; `anyhow` is for binaries, scripts, tests and the outermost
glue. *Why:* a caller can only handle what it can name.

**RUST-ERR-2 — no silent defaults for required values.** `unwrap_or_default()` and friends are for
values that are genuinely optional. A required field that is missing is an error
(`ok_or_else(...)`). *Why:* a default that stands in for a missing value turns a loud failure into
quietly wrong data (tasker-core's Fail Loudly tenet).

**RUST-ERR-3 — panics are for bugs.** Libraries do not panic on bad input. An `expect("...")` is
acceptable where its message states the invariant that makes it unreachable.

## Types

**RUST-TYPE-1 — public types implement `Debug`.** Enforced by `missing_debug_implementations`.
Types that carry a credential implement it by hand, redacting the secret (see
[`security.md`](security.md)).

## Toolchain

**RUST-TC-1 — float on stable, declare a minimum.** Workspaces build on the current stable
toolchain (no `rust-toolchain.toml` pin) and declare `rust-version` in `[workspace.package]`, which
every crate inherits. *Why:* floating keeps both repos on the same compiler without a bump ritual;
the declared minimum tells a consumer what the published crates need, and gives
`clippy::incompatible_msrv` something to check against.

**RUST-TC-2 — edition is a workspace setting.** `edition` lives in `[workspace.package]`. Moving
to a new edition is one deliberate change per repo, not a per-crate drift.

## SQL (sqlx)

**RUST-SQL-1 — queries are compile-checked.** Use the `query!` / `query_as!` macros and commit the
`.sqlx` cache. A runtime-checked `sqlx::query(...)` is an exception with a reason (dynamic `ORDER BY`,
a dynamic table, a vector cast), and the set of exceptions is pinned by a tripwire. *Why:* a
runtime query is the one place a schema change can break production without breaking the build.

## Not specified in v0

- The `too-many-arguments` threshold: temper treats more than five domain parameters as a smell to
  fix with a parameter struct; tasker-core sets the threshold at ten. Clippy's default (seven) is
  left in place until that is ruled.
- Clippy's `pedantic`, `style`, `complexity` and `perf` groups: off, as in tasker-core today. Turning
  any on is a separate ruling, adopted per [RUST-LINT-4](#lints).
