# Concurrency and distributed state

Mostly from tasker-core, whose orchestration is the more demanding distributed system. These rules
apply wherever a service runs concurrent work or shares state across processes.

## Bounded resources

**CONC-BOUND-1 — no unbounded channels.** `tokio::sync::mpsc::unbounded_channel`,
`std::sync::mpsc::channel` and similar are refused by clippy's `disallowed-methods`
([`rust/clippy.toml`](../rust/clippy.toml)). *Why:* an unbounded queue turns a slow consumer into
unbounded memory growth, and the failure shows up far from its cause.

**CONC-BOUND-2 — bounds come from configuration.** A channel, pool or semaphore capacity in
production code is read from configuration, not written as a literal. Tests may use literals.
*Why:* the right bound depends on the deployment, and a literal hides the decision.
(tasker-core: `docs/development/mpsc-channel-guidelines.md`.)

**CONC-BOUND-3 — every bound declares what happens when it is reached.** One of:
- block (backpressure to the producer);
- `try_send` and drop, with a metric;
- send with a timeout;
- retry with backoff.

*Why:* "what happens when it is full" is the design decision; the capacity is just a number.

**CONC-BOUND-4 — bounded queues are observable.** Queue depth and saturation are exported as
metrics.

## Failure is heard

**CONC-FAIL-1 — spawned work is joined or supervised.** Every spawned task is either joined (its
`JoinHandle` result inspected) or owned by a supervisor that observes its exit. A panic at an actor
or handler boundary is contained (`catch_unwind`, or the `JoinError` inspected) and reported. *Why:*
a detached task that panics disappears; the work it was doing silently stops.

**CONC-FAIL-2 — concurrent work is named.** Spawned tasks are named (tasker-core's `spawn_named!`)
and acts carry their own tracing span (temper's `#[act_span]`, with `skip_all` so arguments are not
recorded by accident). *Why:* a trace or a tokio-console view should say what each unit of work is.

## Coordination in the database

**CONC-DB-1 — cross-process state changes are atomic in the database.** State transitions use
compare-and-set in SQL (a transition function, or `UPDATE ... WHERE state = $expected`). Work claiming
uses `FOR UPDATE SKIP LOCKED`. Uniqueness that matters is a constraint. *Why:* application-level
checks race; the database is the only place both processes see the same truth (tasker-core's Defense
in Depth: atomicity, state-machine guards, transactions, then application filtering).

**CONC-DB-2 — retries are idempotent by construction.** An operation that may be retried carries an
identity (an identity hash, or a caller-supplied idempotency key) that the database enforces, so a
retry converges on the first result instead of duplicating it.

**CONC-DB-3 — a transaction is scoped to one decision.** Begin, do the reads and writes the decision
needs, commit. No network calls to other services while a transaction is held open.

## Not specified in v0

- Cadence, rate and volume limits (rate limiting, load shedding): open. Neither repo states a shared
  rule yet, and these are exactly the axes a register should not claim to have closed.
- Choice of runtime: tokio is used by both and assumed; no rule states it.
