# Roadmaps

How a repository publishes where its work is going. A roadmap is read by people who will not open
the work records behind it, so it is where a repository's view of its own work is most often
taken on trust. These rules keep that view answerable to the records.

**Terms.** A **goal** is a recorded outcome with a statement of what it protects. A **work item**
advances at most one goal, and is **filed** once it is recorded in the tracker. A work item is
**claimed** while someone is working it, and **ready** when it can be started now. A goal is
**open** until it is closed or abandoned. A lane is **read from the records** when it is computed
from them, and **drawn by hand** when a person assigns it. A repository's guidance names which
field or state in its own tracker carries each term, and which goal statuses it has.

**ROAD-1 — a roadmap is a dated snapshot, never a living plan.** Each roadmap is a new record that
states the date it describes, and which of its lanes were read from the records. A newer snapshot
supersedes an older one, which stays as it was, with one exception: a published line that
discloses an unfixed security weakness is withdrawn ([SEC-RPT-1](security.md#reporting)), and the
snapshot says that a line was withdrawn. *Why:* a reader sees only the current text, and cannot
tell a stated direction from a changed one without digging through history.

**ROAD-2 — the lanes are what the records say.** Each open goal sits in exactly one lane:
- **Now:** some of its work is claimed, or ready and unclaimed.
- **Next:** it has filed work, none of it claimed or ready.
- **Later:** it has no filed work.

Each goal's line states how many of its work items are claimed, how many are ready and unclaimed,
and how many are filed in all, so a goal with one small claimed item is not read as one being
worked in earnest. A snapshot that does not read every lane from the records names, for each lane
it did not read, how that lane was assigned, such as work in progress standing in for Now while no
work item is marked ready. *Why:* a lane assigned by opinion drifts from the work, and a stand-in
nobody names is read as the rule.

**ROAD-3 — goals are grouped by one declared key, holding one value from a written vocabulary.** A
repository chooses the key that groups its goals (a product area, say). Its owner decides the
closed set of values and writes it down in the repository. Every open goal carries exactly one
value. The vocabulary belongs to the repository; this baseline does not set it. *Why:* with one
group per goal and one lane per goal, the snapshot's counts of goals add up, and a key with free
values grows a new group for every goal that does not fit.

**ROAD-4 — value, risk and size are read from the goal, never scored per item.** A snapshot says
what each goal brings or closes in the goal's own terms: what it protects, and the outcomes it
states (subject to ROAD-6 where the readers are wider). It does not ask a work item for a value,
risk or size score, and orders goals by group and lane, not by a score. *Why:* a per-item score is
a guess made before the work, like an effort estimate, and a roadmap sorted by guesses reads as if
it were measured.

**ROAD-5 — a snapshot states what it leaves out.** It counts the filed work that advances no open
goal, names the goal statuses it omits, and lists by name, under its own heading, every open goal
that carries no group value. It counts, without naming them, the goals withheld under ROAD-6.
*Why:* a reader takes what is absent from a roadmap as not happening, and coverage is never inferred
from absence.

**ROAD-6 — a line written for a wider audience states the outcome, not the current weakness.**
Where a roadmap's readers are wider than those of the goal records it is drawn from, each line says
what the goal brings or closes. It does not describe how the system falls short today. A goal whose
title discloses an unfixed security weakness is retitled by its owner, or left out and counted
under ROAD-5, before the snapshot is published. *Why:* a goal record often describes the hole it
closes in detail, and a roadmap is not the place to disclose one; unfixed weaknesses go through the
private channel ([SEC-RPT-1](security.md#reporting)).

## Not specified

Where a roadmap lives (a file in the repository or a record in its tracker), its format, and how
often it is redrawn are the repository's choice. So is the order of goals within a lane.
