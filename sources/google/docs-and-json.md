# Google Markdown guide and JSON style guide — ledger

Sources, read 2026-10-23: the Markdown guide
([`docguide/style.md`](https://github.com/google/styleguide/blob/gh-pages/docguide/style.md),
`best_practices.md`, `philosophy.md`) and the
[JSON style guide](https://github.com/google/styleguide/blob/gh-pages/jsoncguide.md). CC-BY 3.0,
© Google; restated, not copied. Ledger format: [`../README.md`](../README.md).

## Markdown

| Guide rule | Verdict | Our rule | Note |
|---|---|---|---|
| ATX headings, one H1, fenced code, consistent list markers, no trailing whitespace | adopt | DOC-1 | markdownlint MD003/MD004/MD009/MD025/MD046/MD048 |
| Unique headings | adopt | DOC-1 | MD024 `siblings_only` |
| Declare the code-block language | adopt | DOC-2 | MD040; `text` for diagrams |
| 80-character lines | adapt | DOC-3 | 100, matching rustfmt and ruff |
| Minimum viable docs; update docs with code; delete dead docs | covered | AG-4, CI-3 | |
| "Duplication is evil" | covered | AG-1, AG-5 | |
| Absolute link paths | reject | DOC-4 | Relative links are what work on GitHub; they are checked to resolve instead |
| Prefer lists to tables | reject | — | The rule register is tables, and agents read them well |
| `[TOC]`, the page layout template | reject | — | Gitiles-specific |
| Avoid HTML | adapt | — | Allowed where Markdown cannot express it; not ruled |

## JSON

| Guide rule | Verdict | Our rule | Note |
|---|---|---|---|
| camelCase property names | reject | API-JSON-1 | Both APIs are 100% snake_case, and the SDKs are generated from them |
| Enum values as strings | adopt | API-JSON-1 | With a pinned casing: snake_case |
| Dates as RFC 3339 | adopt | API-JSON-3 | Typed `date-time` in the spec; `*_at` reserved for timestamps |
| Durations as ISO 8601 | reject | API-JSON-4 | Integers with a unit suffix |
| The `error` object | adapt | API-JSON-2 | `{error: {code, message, details?}}` with a string code; Google's integer `code` and `errors[]` rejected |
| Top-level `data` envelope; `apiVersion`, `kind`, `context`, property ordering | reject | API-JSON-5 | The HTTP status and the resource are enough |
| Reserved paging property names | reject | API-JSON-5 | The names rejected; the idea kept (a list says whether it is complete) |
| Omit null-valued properties | adapt | — | Per field, declared in the spec; stated silence |
| (silent) The spec matches the wire | — | API-JSON-2 | Ours; the guide predates OpenAPI |
