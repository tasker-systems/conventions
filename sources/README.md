# Sources

External guides this baseline has been checked against, one ledger per guide. A ledger records,
section by section, whether the guide's rule was **adopted**, **adapted**, already **covered**, or
**rejected** — and for everything but an adoption, why.

The doctrine in [`../doctrine/`](../doctrine/) is the authority, not these guides. A ledger exists
so that:

- **an adopted rule is restated in doctrine** with our id, our reason and an enforcement status in
  [`rules.md`](../doctrine/rules.md). "Google says so" is never the reason; the reason is written
  out, and the ledger points back to where the idea came from;
- **a rejection is not re-litigated.** The next session that reads the same guide finds the
  decision and its reason here, instead of proposing the rule again;
- **the reading is dated.** Each ledger names the revision it was read against. When the guide
  changes, the ledger is re-read against the new revision, not patched from memory.

Ledgers are reference for people changing this repository. They are not projected into consuming
repos; the doctrine is.

## Ledgers

| Guide | Ledger | Read |
|---|---|---|
| Google Rust style guide | [`google/rust.md`](google/rust.md) | 2026-10-23 |
| Google Python style guide | [`google/python.md`](google/python.md) | 2026-10-23 |
| Google TypeScript style guide (and the JavaScript and HTML/CSS guides) | [`google/typescript.md`](google/typescript.md) | 2026-10-23 |
| Google Shell style guide | [`google/shell.md`](google/shell.md) | 2026-10-23 |
| Google Markdown guide (docguide) and JSON style guide | [`google/docs-and-json.md`](google/docs-and-json.md) | 2026-10-23 |

Not read, because nothing in the suite is written in the language: C++, Go, Java, C#, Objective-C,
Swift, Kotlin, R, Common Lisp, Vim script, Verilog, XML. Google publishes no Ruby guide, so the
Ruby surfaces (tasker-core's magnus bindings, temper's generated gem) have no ledger here.

Google's style guides are licensed CC-BY 3.0. Ledgers restate and cite them, and do not reproduce
their text.
