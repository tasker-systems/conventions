# Rule register

Every rule in `doctrine/` has a row here, with its enforcement status in each consuming repo. This
file is what makes [tenet 1](tenets.md) checkable: a rule is either enforced by a named gate, or
says why it is not.

**Status vocabulary**

| Status | Meaning |
|---|---|
| **gated: `<gate>`** | A named CI check fails on a violation |
| **partial: …** | Enforced for part of the scope; what's missing is stated |
| **practiced** | The code follows it today, but nothing would catch a violation |
| **convention: …** | Deliberately not gated, with the reason |
| **uncovered** | Not followed, or not checked. A known hole |

Statuses were taken on 2026-10-21 against `temper@f460428` and `tasker-core@48ac836`, and
amended on 2026-10-23 for tasker-core#376 and temper#1217, from a
read-only inventory of each repo; counts come from grep. Gated and uncovered cells were checked by
hand. A `practiced` cell is a reading of the code, not a proof — the first grounding pass on each
section re-verifies them. A change that alters a status updates its row in the same change.

## Rust

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| RUST-LINT-1 | One workspace lint table, inherited by every crate | uncovered (no `[lints]` table) | gated: workspace table, every crate inherits |
| RUST-LINT-2 | Clippy and rustdoc `-D warnings` on PRs | gated: code-quality.yml, pre-push | gated: code-quality.yml (tasker-core#376); release pre-flight clippy still lacks it |
| RUST-LINT-3 | `#[expect(reason)]`, never `#[allow]` | uncovered (no rule; ~19 `#[allow]`) | partial: written rule; lint commented out; ~33 `#[allow]` |
| RUST-LINT-4 | Lint adoption is audit-before-enforce | convention: a process rule, judged in review | convention: same |
| RUST-UNSAFE-1 | `#![forbid(unsafe_code)]` in every crate root | uncovered | uncovered (no production unsafe, but no forbid) |
| RUST-UNSAFE-2 | Unsafe sites are registered exceptions, with SAFETY comments | uncovered (~10 sites, unregistered) | partial: `undocumented_unsafe_blocks` lint; no register |
| RUST-UNSAFE-3 | FFI through binding frameworks | n/a (no FFI) | practiced (magnus, PyO3, napi-rs) |
| RUST-ERR-1 | `thiserror` in libraries, `anyhow` at edges | practiced | practiced |
| RUST-ERR-2 | No silent defaults for required values | uncovered | uncovered (~121 `unwrap_or_default`; doctrine exists) |
| RUST-ERR-3 | Panics are for bugs | convention: needs judgment per site | convention: same |
| RUST-TYPE-1 | Public types implement `Debug` | uncovered (lint not set) | gated: `missing_debug_implementations` (with RUST-LINT-2 once fixed) |
| RUST-TC-1 | Float stable, declare `rust-version` | partial: floats; no MSRV | partial: floats; MSRV on two crates only |
| RUST-TC-2 | Edition is a workspace setting | practiced | practiced |
| RUST-SQL-1 | Compile-checked queries; runtime queries registered | gated: `audit-sqlx-macro-exceptions.sh` | partial: macros dominant (~337 vs ~101 runtime); no register |

## Supply chain

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| SC-ADV-1 | `cargo audit` gates | gated: quality-gate.yml | uncovered: `continue-on-error` and `|| echo` |
| SC-ADV-2 | Reviewed, reasoned ignores | gated: by review of `.cargo/audit.toml` | partial: one ignore, no reason or status |
| SC-DENY-1 | Only crates.io | gated: `cargo deny check sources` | uncovered (no cargo-deny) |
| SC-DENY-2 | License allowlist | gated: `cargo deny check licenses` | uncovered |
| SC-DENY-3 | Bans (wildcards, deny list; duplicates warn) | uncovered (bans not run) | uncovered |
| SC-GHA-1 | Every `uses:` SHA-pinned | partial: privileged jobs gated by `audit-privileged-action-pins.sh`; 39/82 overall | practiced: every `uses:` pinned (tasker-core#376); no tripwire |
| SC-GHA-2 | Top-level `permissions:` | partial: 13/14 workflows; not gated | practiced: 12/12 (tasker-core#376); no tripwire |
| SC-GHA-3 | Release-chain triggers pinned | gated: `check-release-chain-triggers.sh` | uncovered |
| SC-IN-1 | Tool installs pinned or cooled | gated: mise `minimum_release_age`, `mise.lock` | uncovered |
| SC-IN-2 | Dependency updates for every ecosystem | practiced | partial: cargo and Actions; PR #341 adds the rest |
| SC-IN-3 | Lockfiles match manifests | partial: npm via `check-lockfile-versions.sh` | partial: PR #342 adds cargo, bundler and uv |
| SC-SEC-1 | gitleaks and CodeQL | gated: secret-scan.yml, codeql.yml, pre-commit | uncovered |

## Security

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| SEC-CRED-1 | Credentials are secret types | partial: `secrecy` in temper-client only | partial: tasker-secure exists; one consumer |
| SEC-CRED-2 | Credential `Debug` redacted, proven | gated: `audit-credential-debug.sh` | practiced (hand redaction); unproven |
| SEC-CRED-3 | Constant-time comparison | practiced | practiced |
| SEC-CRED-4 | One secret per purpose | gated: `audit-signature-secrets.sh` | uncovered |
| SEC-RED-1 | One redaction module | practiced (`temper-core/src/redact.rs`) | uncovered (duplicated `redact_url`) |
| SEC-RED-2 | Redact by origin, deny by default | practiced | uncovered |
| SEC-SQL-1 | Bind values, validate identifiers | practiced | practiced (queue and NOTIFY validators) |
| SEC-SQL-2 | Authorisation inside the query | practiced | convention: unexamined for tasker-core's model |
| SEC-AUTH-1 | Disabled-auth mode is loud and cannot ship | n/a (auth always on) | uncovered (auth off by default) |
| SEC-AUTH-2 | Authorise before reading the body | gated: `audit-route-auth.sh` | practiced (`authorize()` at the route) |
| SEC-AUTH-3 | Refusal does not reveal existence | practiced | unexamined |
| SEC-TEST-1 | Test doors never ship | gated: `check-production-features.sh` | uncovered |
| SEC-RPT-1 | SECURITY.md with private reporting | practiced | practiced |

## Concurrency

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| CONC-BOUND-1 | No unbounded channels | practiced (0 sites); ungated | practiced (0 sites); ungated |
| CONC-BOUND-2 | Bounds from configuration | uncovered (no rule) | practiced (1 literal outside tests); ungated |
| CONC-BOUND-3 | Declared at-bound strategy | uncovered | practiced (doctrine with recipe) |
| CONC-BOUND-4 | Queues observable | uncovered | practiced (`ChannelMonitor`) |
| CONC-FAIL-1 | Spawned work joined or supervised | unexamined | practiced (`catch_unwind` at boundaries) |
| CONC-FAIL-2 | Concurrent work is named | practiced (`#[act_span]`) | practiced (`spawn_named!`) |
| CONC-DB-1 | Atomic cross-process state in the database | practiced | practiced (CAS functions, `SKIP LOCKED`) |
| CONC-DB-2 | Idempotent retries by construction | practiced (create idempotency keys) | practiced (identity hash) |
| CONC-DB-3 | One decision per transaction | convention: judged in review | convention: same |

## Tripwires

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| TW-1 | Header states why, and what is NOT CHECKED | practiced | n/a (no tripwires yet) |
| TW-2 | Reviewed baseline, `--list`, `UPDATE_BASELINE` | practiced | n/a |
| TW-3 | Empty scan fails | practiced | n/a |
| TW-4 | Fixture override seam | practiced | n/a |
| TW-5 | Bite test | partial: 8 check scripts lack one | n/a |
| TW-6 | Derived set; CI covers all | gated: `cargo make tripwires` | n/a |
| TW-7 | Key on the bug, not the shape | convention: judged in review | n/a |

## Testing and CI

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| TEST-1 | Ignored tests registered with reasons | gated: `audit-ignored-tests.sh` | uncovered |
| TEST-2 | Never weaken a test to get green | convention: judged in review | convention: same (in CLAUDE.md) |
| TEST-3 | Every tier runs in CI | practiced | partial: `test-cluster` local only, by design |
| TEST-4 | Retries are reported | gated: `junit-summary.py` annotations | uncovered |
| TEST-5 | Coverage floors in CI | partial: nightly, advisory | uncovered (local only) |
| CI-1 | Cheap stage-1 gate | gated: quality-gate.yml | uncovered |
| CI-2 | One required aggregate check | gated: `ci-success` | gated: `CI Success` |
| CI-3 | Generated artifacts drift-checked | gated: every generated artifact | partial: codegen syntax only |
| CI-4 | Selective pre-commit hook | practiced | partial: fmt only, opt-in |
| CI-5 | Required checks run on `merge_group` | gated: `ci.yml` `merge_group` trigger; queue exercised | practiced: `ci.yml` `merge_group` trigger (tasker-core#376); first queue merge 2026-10-23; no tripwire |
| CI-6 | Job timeouts budget for cold-cache queue runs | unexamined | practiced: integration timeout 25→40 min (tasker-core#376) |

## Agent guidance

| Id | Rule | temper | tasker-core |
|---|---|---|---|
| AG-1 | Entry file is a router | practiced | uncovered (monolithic CLAUDE.md) |
| AG-2 | Rules state their reason | practiced | partial |
| AG-3 | Rules state their enforcement | uncovered | uncovered (`SQLX_OFFLINE` contradiction) |
| AG-4 | Facts derived or checked | partial: CLI and config references drift-gated | uncovered (stale crate list) |
| AG-5 | Baseline arrives as a projected skill | uncovered (not built) | uncovered |
| AG-6 | Hooks point at real paths | practiced | practiced (SessionStart path fixed, tasker-core#376); no check |
