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
- **An entry point** is what a client calls or names. For an HTTP API it is an operation,
  identified by its method and path template with parameter names erased, so `/items/{id}` and
  `/items/{item_id}` are one operation. For a library it is a public item, identified by its path.
- **The resolved form** of an entry point is its shape with every reference resolved in place. For
  an operation, that covers every `$ref` reached from its parameters, request body, responses,
  headers and callbacks, through components of every kind. A reference back into a node already
  being resolved is compared by name, so a cycle ends.
- **A break** is what the comparator reports when it judges one form against another.
- **A declared break** is the PR's own statement that a break is intended: a version class, a
  register entry, a label.

**COMPAT-1 — a gate charges a PR only with breaks a client of the last release can observe, and
only with the ones the PR made.** The gate judges each entry point in its resolved form, three
times: release against head, release against base, and base against head. The PR is charged with
the breaks that release against head reports and release against base does not. Nothing else is
charged.

The consequences:

- **Shape born in the window** (an entry point absent at the release, or a schema reached only
  through a property, parameter or response the release did not have) can move, be renamed or be
  removed freely. Against the release, it is growth.
- **Released shape** is judged against its released form. This holds wherever the change is made:
  in the entry point itself, in a component it reaches, or in a window-born component that a
  released location now holds. A window-born parameter that becomes required on a released
  operation is charged.
- **A re-birth** is shape the release had, which the window removed and the PR restores. It is
  judged against its released form at every depth, whether it is an operation, a schema or a single
  property. It is charged if it differs as a break would, and not charged if restored unchanged.
- **An earlier PR's declared break** is not charged again, because release against base already
  reports it. A further break this PR makes on the same entry point is charged, because it is a
  break release against base does not report.

Where the comparator returns only a verdict per entry point, and not the breaks themselves, the
gate charges an entry point when base against head breaks it and release against head breaks it.
This fallback can charge a PR with an earlier declared break on the same entry point. It never
waves through a break the PR made. The consumer records that residue in its status.

The comparator is unchanged; only what it is pointed at changes. Every tolerance and every residue
it has carries over. There is one place where judging against the release can expose a residue that
judging against the base would hide. A property that is new by name, on a schema whose released form
admitted it through `additionalProperties` or `patternProperties`, is released shape on the input
side: a client of the release could already send it. A comparator that reads such a property as
growth must not be used for this rule until it judges the property against what the release
admitted. Until then, the consumer records the gap as residue. Every context the comparator derives
from a pair of contracts (temper's input-only side, for example) is derived from the pair being
judged.

*Why:* a break is something a client built against a release can observe. For a surface that
clients obtain only through a release, no client has seen shape born since that release. A gate
that measures only against the PR's base reports breaks no such client can see, and pushes its
author to declare a false break or to bend the design around the gate. A gate that measures only
against the release charges a PR with every earlier PR's declared break. Taking the difference of
the two release-relative judgements charges exactly the observable breaks this PR introduced.
Judging resolved entry points, not named components, follows what a client actually sends and
receives. A component is judged where it is used, so a window-born component held at a released
location cannot carry a break past the gate.

*Residue (provisional, pending an owner's ruling):* a surface deployed continuously from the
protected branch (a hosted API that auto-deploys `main`) reaches clients before it is released. A
client that integrated against the deployment can observe window-born shape, and this rule does
not protect that client. A consumer whose deployed surface needs that protection measures that
surface against the PR's base alone, and says so in its status.

**COMPAT-2 — the last release comes from the release tooling's own derivation, and a ref that is
not provably the newest release fails closed.** The gate calls the derivation its release tooling
uses to open the window; it does not keep a second copy. A ref is the last release only when all
four hold:

- it is a tag in the release tooling's own tag form;
- it is an ancestor of the PR's base;
- it was found in a history that holds it: the clone is not cut short above it, and tags were
  fetched;
- no tag in the release form on the remote (`git ls-remote --tags`, for example) is newer and an
  ancestor of the base.

A derivation's fallback is never a release: a root commit, a shallow boundary, a hand-given
override. The derivation reports a fallback in its output, not only in a log line. A gate that
cannot tell whether it got a fallback treats it as one.

What was present at the release is read from what the release published. Where that differs from
the tree at the tag (a crate on its registry), the published copy is read. It is never inferred from
history. "The latest commit that added a node", for example, falls in the window for a re-birth.

The gate measures against the last release as of merge. Either a merge queue re-runs it, or branch
protection requires an up-to-date base. A consumer with neither records release staleness as
residue.

A repository with several release streams (per-crate or per-package tags) measures each surface
against the last release of every stream that ships it. A surface shipped by more than one stream
breaks if it breaks against any of them. A release cut on a branch the base does not contain (a
hotfix on a maintenance line) is such a stream: a surface it shipped is judged against it as well.
Where the gate does not do that, the consumer records it as residue.

When no ref qualifies, or the artifact cannot be read at it, the gate measures against the PR's
base alone and says so.

*Why:* two derivations of "the last release" drift, and then the gate and the version calculator
disagree about which window a change belongs to. A fallback ref is worse than none: a shallow CI
clone can make the PR's own head the "root", and every entry point then equals its "released form".
An older genuine tag is as bad: shape shipped since it reads as window-born. A gate that cannot find
the release and treats everything as new waves every break through. "I could not look" is not
"nothing shipped". The base-only verdict is stricter than the release-relative one everywhere except
a re-birth, which only the release can reveal. So falling back can redden a PR, and passes nothing
COMPAT-1 refuses except a re-birth.

## Bite cases

A gate that claims COMPAT-1 and COMPAT-2 carries these in its bite test ([TW-5](tripwires.md)).

COMPAT-1:

1. A schema born in the window, reached only through a new optional property of a released
   operation, moves as growth. This is temper#1388's shape.
2. A released operation whose resolved form breaks against the release fails without a declared
   break.
3. With the release reference removed from the gate, case 1 fails.
4. A re-birth that differs from its released form fails: once as an operation, once as a single
   property.
5. A window-born parameter component on a released operation that becomes required fails.
6. An operation an earlier PR broke (declared) passes when this PR changes it only in ways the
   release did not have, and fails when this PR breaks it further.
7. A path whose template parameter was renamed is judged against its released form.
8. A property admitted at the release by `additionalProperties`, then narrowed by name, fails.

COMPAT-2:

9. With no release ref resolvable, the gate gives the base-only verdict.
10. A shallow clone without tags gives the base-only verdict, never a verdict against the fallback
    commit.
11. A tag in the release form on a commit that is not an ancestor of the base is not taken as the
    release.
12. A clone holding an older release tag, but not the newest, gives the base-only verdict.

## Not specified

- **Which surfaces need a compatibility gate.** That is a separate ruling per surface. A consumer
  without one records these rules as `n/a`, with that reason.
- **A shared checker.** None ships from this repository. Only the consumer's own comparator can
  enforce the rule, and a copy here would be either a trivial presence check or a second
  comparator. A shared "last release" helper would be the second derivation COMPAT-2 forbids.
- **How a comparator resolves references** (inlining, or walking with a visited set). Any method
  that judges the resolved form, and ends on a cycle, will do.
