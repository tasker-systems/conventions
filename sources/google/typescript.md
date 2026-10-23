# Google TypeScript style guide — ledger

Source: [google/styleguide `tsguide.html`](https://google.github.io/styleguide/tsguide.html), with
the [JavaScript](https://google.github.io/styleguide/jsguide.html) and
[HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html) guides skimmed for anything the
TypeScript guide lacks. Read 2026-10-23. CC-BY 3.0, © Google; restated, not copied. Ledger format:
[`../README.md`](../README.md).

Google's guide assumes its own toolchain (Closure, tsetse conformance checks, clang-format) and
downlevelled output. Ours is Biome and `tsc`, with code that Node, Bun and Deno run by
type-stripping. Biome rule names below were checked against Biome 2.5.15.

| Guide rule | Verdict | Our rule | Note |
|---|---|---|---|
| Use `import type` / `export type` | adopt | TS-CFG-2 | `useImportType`, `useExportType`, `verbatimModuleSyntax` |
| Named exports, no default exports | adapt | TS-MOD-1 | `noDefaultExport`, with an override for framework-required defaults |
| No `namespace` | adopt | TS-CFG-2 | `noNamespace` |
| No `const enum`; plain `enum` allowed | adapt | TS-CFG-2 | Stricter: no `enum` at all (`noEnum`, `erasableSyntaxOnly`), because type-stripping cannot emit one |
| Prefer parameter properties | reject | TS-CFG-2 | Parameter properties are not erasable syntax; `noParameterProperties` |
| No `#private` fields | reject | — | Google's reason is downlevelling cost; we target ES2022. Stated silence |
| `any` is discouraged; prefer `unknown` | adopt | TS-TYPE-1 | `noExplicitAny` at error, not warn |
| Avoid non-null assertions; justify type assertions | adopt | TS-TYPE-2 | `noNonNullAssertion`; `as` comment is review-held |
| No `@ts-ignore`; `@ts-expect-error` only in tests | adapt | TS-SUP-1 | `@ts-expect-error <reason>` allowed anywhere — the same idea as `#[expect(reason)]` |
| Throw only `Error` instances | adopt | TS-ERR-1 | `useThrowOnlyError` |
| `===`, except `== null` | covered | — | `noDoubleEquals` with `ignoreNull` (config only) |
| `const`/`let`, no `var` | covered | — | `useConst`, `noVar` (config only) |
| `T[]` for simple array types | adopt | — | `useConsistentArrayType` (config only, no doctrine row) |
| No `for…in` on arrays | covered | — | Practiced, 0 sites |
| Optional `?` vs `\| undefined` | adapt | TS-CFG-1 | They differ in meaning under `exactOptionalPropertyTypes`, which the base turns on |
| Interfaces over type-literal aliases | reject | — | 55 sites of churn, no defect class |
| Braces on every block | reject | — | 680+ sites, no defect class |
| Function declarations over arrow functions; `this` rules | reject | — | Review judgment |
| Naming: lowerCamelCase properties | reject | TS-NAME-1 | Wire types keep the API's snake_case |
| Naming: no `_` prefix; no `I` prefix | adapt | TS-NAME-1 | `_` allowed for unused bindings (how tsc and Biome mark them); no `I` prefix kept |
| JSDoc for documentation, `//` for implementation | adapt | TS-DOC-1 | Required only for published packages' exports |
| Decorators | reject | — | None in use; stated silence |
| Closure, `goog.*`, `@fileoverview`, copyright headers, tsetse, clang-format | reject | — | Google toolchain |
| Generated code | — | TS-GEN-1 | Not addressed by Google; we have schema.ts, ts-rs and napi outputs |
| HTML/CSS guide | reject | — | Tailwind plus temper's colour-token guards cover what matters |
| (silent) Linter warnings as non-failing | — | TS-TOOL-2 | Ours: no rule at `warn`; CI runs `--error-on-warnings` |
