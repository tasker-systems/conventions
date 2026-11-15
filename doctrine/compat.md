# Compatibility gates

How a gate that judges compatibility decides what counts as a break. Such a gate might be a
declared-class gate over an OpenAPI spec (temper's `wire-class-crosscheck.sh`), a semver check over
a published crate or package, or any other check that compares one revision's shape with another's.
This file does not say which surfaces need such a gate, or how to compare two shapes: that is the
consumer's own comparator. It says **what the comparator is pointed at**. Enforcement status per
repo is in [`rules.md`](rules.md).

Terms:

- **The last release** is the newest release of the surface that qualifies under COMPAT-2.
- **The window** is every change merged since the last release.
- **A node** is a unit the gate's comparator judges: a path, a schema, a component, or a public
  item.
- **A node's identity** is what a client addresses. A path is identified by its method and template
  with parameter names erased, so `/items/{id}` and `/items/{item_id}` are one node. A schema,
  component or item is identified by its name.
- **A node is window-born** when no node with its identity is in the artifact at the last release.
- **A declared break** is the PR's own statement that a break is intended: a version class, a
  register entry, a label.

**COMPAT-1 — a gate charges a PR only with breaks a client of the last release can observe.** A
node the PR moves is judged in one of three ways:

- **A released node** (present at the last release) breaks only when the PR's movement breaks
  against the PR's base, *and* the node breaks against its form at the last release. A re-birth
  counts as such a movement. A re-birth is a node present at the release, absent at the base, and
  present again at head. It is judged against its released form: a break if it differs as a break
  would, and no break if it is restored unchanged.
- **A confined window-born node** may move, be renamed or be removed as growth.
- **An unconfined window-born node** is judged against the PR's base alone, exactly as without this
  rule.

A window-born node is **unconfined**, at head, when either of these holds:

- a reference into it, or into a window-born node that reaches it, is held at a location the last
  release already had. Such a location is a property, parameter, response or path that existed at
  the release, and it includes a key gained beside keys the release had (a `$ref`, an `allOf`, an
  `additionalProperties`);
- it is reachable from any node that breaks against its released form.

References from anywhere in the artifact count, not only from nodes the comparator judges: a
component of any kind, a discriminator mapping, a webhook, a callback. Every other window-born node
is **confined**: every reference into it, and into every window-born node that reaches it, is held
at a location the release did not have, and no broken node reaches it. Reachability is followed to
a fixed point, so a cycle of window-born nodes is judged as one.

A `$ref` belongs to the node that holds it. A `$ref` swapped at a location the release had is a
change to a released node, judged against its released form like any other. A `$ref` swapped at a
location the release did not have is growth while the nodes it reaches are confined.

The comparator is unchanged; the rule changes only what it is pointed at. Every tolerance and
residue the comparator has carries over, and confinement must not widen one. A referrer whose
change the comparator cannot see (a key gained beside released keys) counts as reaching for
confinement. Every context the comparator derives from a pair of contracts (temper's input-only
side, for example) is derived from the pair being judged.

*Why:* a break is something a client built against a release can observe. For a surface that
clients obtain only through a release, no client has seen a node born since that release. A gate
that measures only against the PR's base reports breaks no such client can see, and pushes its
author to declare a false break or to bend the design around the gate. A gate that measures only
against the release charges a PR with an earlier PR's declared break. Confinement closes the gap
between the two. Without it, a released location could reach a window-born node and carry new
breakage to release clients through it.

*Residue:* a surface deployed continuously from the protected branch (a hosted API that
auto-deploys `main`) reaches clients before it is released. A window-born node there can be
observed by a client that integrated against the deployment, and this rule does not protect that
client. A consumer whose deployed surface needs that protection measures that surface against the
PR's base alone, and says so in its status.

**COMPAT-2 — the last release comes from the release tooling's own derivation, and a ref that is
not provably a release fails closed.** The gate calls the derivation its release tooling uses to
open the window. It does not keep a second copy of it. A ref qualifies as the last release only
when all three hold:

- it is a tag in the release tooling's own tag form;
- it is an ancestor of the PR's base;
- it was found in a history that holds it, so the clone is not cut short above it and its tags are
  fetched.

A derivation's fallback is never a release: a root commit, a shallow boundary, a hand-given
override. The derivation reports a fallback in its output, not only in a log line, and a gate that
cannot tell whether it got one treats it as a fallback. Presence at the release is read from what
the release published. Where that differs from the tree at the tag (a crate on its registry), the
published copy is the one read. Presence is never inferred from history. "The latest commit that
added a node", for example, falls in the window for a re-birth and would read it as window-born.
The gate reads the release when the PR merges (a merge queue re-runs it), so a release cut while
the PR is open is the one it measures against. When no ref qualifies, or the artifact cannot be
read at it, the gate measures against the PR's base alone and says so.

*Why:* two derivations of "the last release" drift, and then the gate and the version calculator
disagree about which window a change belongs to. A fallback ref is worse than none: a shallow CI
clone can make the PR's own head the "root", and every node then equals its "released form". A
gate that cannot find the release and treats every node as new waves every break through: "I could
not look" is not "nothing shipped". The base-only verdict is stricter than the release-relative one
everywhere except a re-birth, which only the release can reveal. So falling back can redden a PR,
and can never pass anything COMPAT-1 refuses, except a re-birth.

## Bite cases

A gate that claims COMPAT-1 and COMPAT-2 carries these in its bite test ([TW-5](tripwires.md)).

COMPAT-1:

1. A moved window-born node passes as growth.
2. A moved node that existed at the release still fails without a declared break.
3. With the release reference removed from the gate, case 1 fails.
4. A re-birth that differs from its released form fails.
5. A window-born node reached from a referrer that broke against the release fails, both with a
   schema as the referrer and with a path.
6. A window-born node reached through a `$ref` gained beside the keys of a released property fails.
7. A window-born node referenced only from a component the comparator does not judge is still
   reached as case 6 would reach it.
8. A path whose template parameter was renamed is judged against its released form.

COMPAT-2:

9. With no release ref resolvable, the gate gives the base-only verdict.
10. A shallow clone without tags gives the base-only verdict, never a verdict against the fallback
    commit.
11. A tag in the release form on a commit that is not an ancestor of the base is not taken as the
    release.

## Not specified

- **Which surfaces need a compatibility gate.** That is a separate ruling per surface. A consumer
  without one records these rules as `n/a`, with that reason.
- **A shared checker.** None ships from this repository. Only the consumer's own comparator can
  enforce the rule, and a copy here would be either a trivial presence check or a second
  comparator. A shared "last release" helper would be the second derivation COMPAT-2 forbids.
- **Several release streams in one repository** (per-crate or per-package tags). Each stream's gate
  measures against its own last release. A node shipped by more than one stream is judged against
  the last release of each, and breaks if it breaks against any.
