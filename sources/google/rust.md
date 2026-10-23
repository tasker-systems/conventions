# Google Rust style guide — ledger

Source: [google/styleguide `rustguide.md`](https://github.com/google/styleguide/blob/gh-pages/rustguide.md)
(rendered at <https://google.github.io/styleguide/rustguide.html>), read 2026-10-23. The guide is
CC-BY 3.0, © Google; rules below are restated, not copied. How a ledger is used:
[`../README.md`](../README.md).

The guide's own aims — readability over writeability, rules that favour automation, consistency
with the wider ecosystem, rules that pull their weight — match [tenet 1](../../doctrine/tenets.md).
Its fourth aim, smoothing Google's large-scale changes, has no counterpart here; rules that exist
only for it are rejected.

**Verdicts:** **adopt** — taken as written; **adapt** — the intent taken, the letter changed;
**covered** — already in doctrine; **reject** — not taken, with the reason.

| Guide section | Verdict | Our rule | Note |
|---|---|---|---|
| Follow public Rust style rules (Rust Style Guide, API Guidelines) | adopt | RUST-FMT-1, RUST-API-5 | Already our practice; now written down |
| Apply API design rules in context (library vs application) | adopt | RUST-API-1 | "Library" defined by publish/consumed-across-repos |
| Prefer small crates; flat file layout | reject | — | Chromium build-graph rules; Cargo conventions apply |
| Name files after the primary item; no APIs in non-leaf modules | adopt | RUST-ORG-2 | |
| Don't use glob imports; don't define preludes | adopt | RUST-ORG-1 | `clippy::wildcard_imports` |
| A `use` imports from one module (`imports_granularity = Module`) | reject | — | Nightly-only rustfmt option; RUST-TC-1 floats stable |
| Locally scoped trait imports; qualify free functions; types unqualified | reject | — | The guide's stated purpose is ending reviewer disagreement; rustfmt defaults do that here |
| Use the appropriate formatting tool; rustfmt settings | adapt | RUST-FMT-1 | Defaults only; the three non-default options are nightly-only |
| Opting out of formatting only for alignment or generated code | adopt | RUST-FMT-1 | |
| Avoid `Rc`/`Arc`; prefer borrows over deep copies | reject | — | Stated silence: `Arc` is idiomatic shared state in tokio services |
| Accept flexible references | adopt | RUST-API-4 | `ptr_arg`, `borrowed_box` |
| Iterators vs owned collections; `impl Into` parameters | reject | — | The guide exempts application code, which is most of ours; library review judges it |
| Prefer `enum` over `bool` in APIs | adopt | RUST-TYPE-2 | |
| Reporting errors: `Option` / `Result` / `panic!` | covered | RUST-ERR-1, RUST-ERR-3 | RUST-ERR-3 now states the three channels |
| Newtypes versus type aliases; named fields over tuples | adopt | RUST-TYPE-2 | Tied to tenet 11 |
| Add trait impls when needed | reject | — | Restates YAGNI; no rule to hold |
| Implement standard traits instead of custom methods; derive where possible; `Default`; `len`+`is_empty` | adopt | RUST-API-3 | Four named style/complexity lints |
| Generics versus `dyn Trait` | reject | — | Performance judgment; both repos use `dyn` deliberately for plug-in seams |
| When to define a trait; extension traits | adapt | RUST-API-5 | Kept only the `…Ext` naming; "don't organise code with traits" is review judgment |
| Error types should be `Copy` | reject | — | Our errors carry context (`String`, sources); `thiserror` types are rarely `Copy` |
| Pair `From` impls with constructors; options structs implement `Default` | reject | — | Taste, below the bar of a rule |
| Handling poison: never reach into a poisoned mutex | adapt | CONC-FAIL-3 | Allowed where every write is whole-value, with a comment |
| Don't use async; don't start std threads; `fuchsia_sync::Mutex` | reject | — | Chromium/Fuchsia-specific; both repos are tokio services |
| Macros: prefer non-macro facilities | adopt | RUST-MACRO-1 | |
| Naming methods, initialisers, getters/setters, extension traits | adopt | RUST-API-5 | `wrong_self_convention` |
| Naming lifetimes and generic parameters; avoid abbreviations | reject | — | Taste; review judges it |
| Documentation: public APIs documented, panics documented, safety documented, no restating comments | adopt | RUST-DOC-1 | `missing_docs` on library crates |
| Unsafe: only when no safe way; safe abstraction; `SAFETY:`; justification and benchmarks | adapt | RUST-UNSAFE-1, -2 | Ours is stricter (`forbid` by default); the justification questions are added to the register entry |
| No unstable features | adopt | RUST-TC-3 | Self-enforcing on stable |
| Implement expected API sets together | adopt | RUST-API-3 | `len_without_is_empty` |
| Don't access `#[doc(hidden)]` items you don't own | reject | — | True, rare, and unenforceable short of review |
| Use `const fn` responsibly | reject | — | Only matters for published crates; review judges it |
| Avoid operator overloading for non-mathematical purposes | adopt | RUST-READ-1 | |
| `#[non_exhaustive]` on public enums and structs | adapt | RUST-API-2 | Published types only; internal types stay exhaustive |
| `#[must_use]` on functions and types | adopt | RUST-API-6 | |
| Do not run code before `main()` | adapt | RUST-INIT-1 | napi-rs uses `ctor` for module registration, so no cargo-deny ban |
| Don't overuse type inference | adopt | RUST-READ-1 | |
| Prefer pattern matching over check-then-unwrap; `expect` over `unwrap` | adopt | RUST-ERR-4 | `unnecessary_unwrap`, `unwrap_used` |
| Don't omit patterns on `non_exhaustive` enums (`non_exhaustive_omitted_patterns`) | reject | — | The lint is unstable |
| Context strings on assertions | adopt | RUST-READ-1 | |
| Don't use combinator chains when iteration is clearer | adopt | RUST-READ-1 | |
| Don't call `panic::catch_unwind` | adapt | RUST-PANIC-1 | Defense in depth only, and only under `panic = "unwind"`. Reading this section found that tasker-core's release profile aborts while three containment sites depend on unwinding |
| Prefer `format!`/`write!` to concatenation | reject | — | Micro-style; clippy covers the cases that matter |
| Use the right per-codebase test framework | covered | TEST-* | `#[test]` and nextest |
