# Roadmaps

How a repository publishes where its work is going. A roadmap is read by people who will not open
the work records behind it, so it is where a repository's view of its own work is most often
taken on trust. These rules keep that view answerable to the records.

The terms are those of the work records the consumers already keep: a **goal** states an outcome
and what it protects, and a **work item** (a task) advances a goal. A work item is **claimed** by
the one session holding it, and **ready** when the workflow has marked it claimable.

**ROAD-1 — a roadmap is a dated snapshot, never a living plan.** Each roadmap is a new record that
states the date it describes, and whether its lanes were read from the records or drawn by hand. A
newer snapshot supersedes an older one, which stays as it was. *Why:* a roadmap edited in place
loses what was believed when, and a reader cannot tell a stated direction from a changed one.

**ROAD-2 — the lanes are what the records say.**
- **Now** is work that is claimed, or ready and unclaimed.
- **Next** is work that is filed and waiting on a need.
- **Later** is a goal with no filed work.

A snapshot drawn by hand before the records can draw these lanes names the stand-in it used for
each one, such as work in progress standing in for Now while no work item is marked ready. *Why:* a
lane assigned by opinion drifts from the work, and a stand-in nobody names is read as the rule.

**ROAD-3 — goals are grouped by one declared key, holding one value from a ruled vocabulary.** A
repository chooses the key that buckets its goals above the goal (a product area, say), and its
owner rules the closed set of values. Every open goal carries exactly one value. The vocabulary
belongs to the repository; this baseline does not set it. *Why:* with exactly one bucket per goal,
the snapshot's counts add up, and a key with free values grows a new bucket for every goal that
does not fit.

**ROAD-4 — value, risk and size are read from the goal, never scored per item.** A snapshot says
what each goal brings or closes in the goal's own terms: what it protects, and the clauses it
states. It does not ask a work item for a value, risk or size score. *Why:* a per-item score is a
guess made before the work, like an effort estimate, and a roadmap sorted by guesses reads as if
it were measured.

**ROAD-5 — a snapshot states what it leaves out.** It counts the filed work that advances no open
goal, names the goal statuses it omits, and names any grouping it could not draw. *Why:* a reader
takes what is absent from a roadmap as not happening, and coverage is never inferred from absence.

**ROAD-6 — a line written for a wider audience states the outcome, not the current weakness.**
Where a roadmap's readers are wider than those of the goal records it is drawn from, each line says
what the goal brings or closes. It does not describe how the system falls short today. A goal
whose own title discloses a live hole is raised with its owner before the snapshot is published.
*Why:* a goal record often describes the hole it closes in detail, and a roadmap is not the place
to disclose one; live holes go through the private channel
([SEC-RPT-1](security.md#reporting)).
