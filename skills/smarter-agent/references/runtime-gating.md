# Runtime gating for self-improvement

The skill loop can be followed manually. Universal enforcement requires a runtime architecture that makes validation part of mutation, not an optional review afterward.

## Required state machine

```text
PROPOSED → STAGED → PENDING_VALIDATION → PASS → ACTIVE
                                  ├──→ PARTIAL → BLOCKED
                                  └──→ FAIL    → BLOCKED
```

A meaningful change must not be certified—and preferably must not become active—before `PASS`.

## Mutation transaction

Every supported writer should call one shared service that:

1. locks the target or records a compare-and-swap revision;
2. captures an immutable old snapshot before any write;
3. stages the proposed new snapshot;
4. classifies whether behavior can change;
5. stores origin, actor/session, mutation path, target, evidence, and hashes;
6. runs conflict scan, chronological replay, controls, and independent review;
7. persists the report and rating;
8. atomically activates only a passing snapshot;
9. leaves the old active snapshot unchanged on `PARTIAL`, `FAIL`, crash, or timeout.

## Writers to cover

Inventory and test all of them:

- skill create, patch, edit, and support-file writes;
- memory/profile writes;
- background curator/self-improvement jobs;
- dashboard and API updates;
- CLI/registry/hub install, update, and sync;
- repository synchronization;
- cron and delegated sessions;
- direct filesystem writers.

A filesystem watcher can detect out-of-process changes, but certification requires both old and new snapshots. If the watcher saw only the new state, quarantine/revert the change or label it unverified; do not reconstruct the old state by guessing.

## Persistence schema

At minimum persist:

- mutation id and timestamps;
- target path and mutation entrypoint;
- origin session/job/actor;
- old and new content hashes plus immutable snapshots;
- significance classification and rationale;
- replay fixture and chronological checkpoints;
- positive, negative, and boundary controls;
- actual decision outputs;
- reviewer identity/isolation and verdict;
- final rating, residual gaps, and activation state.

## Coverage test

For every writer:

1. mutate a fixture through that exact entrypoint;
2. assert old/new snapshots exist;
3. assert the mutation remains pending before review;
4. force `FAIL` and assert the old version stays active;
5. force timeout/crash and assert fail-closed behavior;
6. produce `PASS` and assert atomic activation;
7. verify the durable report links to the mutation and origin.

Also test an unsupported direct write. The system must detect and mark it unverified rather than silently certifying it.

## Non-solutions

These are useful signals but not universal gates:

- a post-write callback with no old snapshot;
- a periodic review job;
- a counter saying “skill review ran”;
- checking that a new phrase exists;
- running the loop only for one tool or foreground session;
- asking the same agent to approve its own edit;
- declaring activation successful before the independent verdict is durable.
