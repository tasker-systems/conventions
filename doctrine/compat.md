# Compatibility gates

How a gate that judges compatibility decides what counts as a break: a declared-class gate over an
OpenAPI spec (temper's `wire-class-crosscheck.sh`), a semver check over a published crate or
package, or any other check that compares one revision's shape with another's. This file does not
say which surfaces need such a gate, or how to compare two shapes. That is each consumer's own
comparator. It says **what the comparator is pointed at**. Enforcement status per repo is in
[`rules.md`](rules.md).

Terms used below:

- **The window** is the open window: every change since the last release.
- **A node** is the unit the gate's comparator judges: a path, a schema, a component, or a public
  item.
- **Window-born** means a node that is absent from the artifact at the last release.

**COMPAT-1 — a gate charges a PR only with breaks a shipped client can observe.** For each node
the PR moves, the movement counts as breaking only when both hold:

- **the PR made it.** The node breaks against the PR's base, or the PR re-births it;
- **a shipped client can see it.** The node also breaks against its own form at the last release.

A window-born node can move, be renamed or be removed freely, as growth, while it is *confined*.
Confined means every node that refers to it at head is one of these:

- itself window-born and confined;
- present at the last release and not broken against its released form.

A node that was present at the last release, is absent at the PR's base and is present again at
head is a **re-birth**. It is not window-born. It is judged against its released form, and it is a
break if it differs from that form the way a break would. Restored unchanged, it is no break. A
`$ref` belongs to the node that holds it. So when a released field swaps its `$ref`, a released
node changes, and that is judged against the release. The swap passes only when the field holding
it is itself window-born.

*Why:* a break is something a client built against a release can observe, and no such client has
seen a node born since that release. A gate that measures only against the PR's base reports
breaks that no client can see. Its author is then pushed to declare a break that is not one, or
to bend the design around the gate. A gate that measures only against the release charges a PR
with an earlier PR's declared break. Confinement closes the remaining gap. Without it, a released
node that already broke in the window could pass further breakage through a window-born schema it
refers to. The rule changes only the reference that the comparator is pointed at, never the
comparator. Every tolerance and every known residue the comparator has carries over unchanged.

**COMPAT-2 — the last release is found the way the release tooling finds it, read at that ref,
and an unfound release fails closed.** The gate takes the last-release ref from the same
derivation the consumer's release tooling uses to open its window. It calls that derivation; it
does not hold a second copy. Whether a node was present at the release is read from the artifact
at that ref, never inferred from history (the first commit a node appears in, for example).
History would read a re-birth as window-born. When no release ref resolves, or the ref is not a
release, or the artifact cannot be read at it, the gate measures against the PR's base alone and
says so. It never measures against an empty release. *Why:* two derivations of "the last release"
drift, and then the gate and the version calculator disagree about which window a change belongs
to. A gate that cannot find the release, and so treats every node as new, waves every break
through: "I could not look" is not "nothing shipped". The base-only verdict is the stricter of the
two, so falling back to it can redden a PR but never pass a break.

## Bite cases

A gate that claims COMPAT-1 carries these in its bite test ([TW-5](tripwires.md)):

1. A moved window-born node passes as growth.
2. A moved node that existed at the release still fails without a break declaration.
3. With the release reference removed from the gate, case 1 fails.
4. A re-birth that differs from its released form fails.
5. A window-born node whose referrer broke against the release fails.
6. With no release ref resolvable, the gate gives the base-only verdict.

## Not specified

- **Which surfaces need a compatibility gate.** That is a separate ruling per surface. A consumer
  without one records these rules as `n/a`, with that reason.
- **A shared checker.** None ships from this repository. Only the consumer's own comparator can
  enforce the rule, and a copy here would be either a trivial presence check or a second
  comparator. A shared "last release" helper would be the second derivation COMPAT-2 forbids.
- **Several release streams in one repository** (per-crate or per-package tags). Each stream's
  gate measures against its own last release. How a repository names those streams is its release
  tooling's business.
