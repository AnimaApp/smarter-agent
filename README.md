# smarter-agent

<img width="667" height="359" alt="image" src="https://github.com/user-attachments/assets/79ae29c7-f0d1-481e-abf5-88b3d14fb78f" />

**A public skill for minimal, self-checking, simulation-driven agent improvement.**

Agents often “learn” by adding another instruction and checking that the new sentence exists. That can bloat the prompt, duplicate an existing rule, or leave the actual decision unchanged.

`smarter-agent` combines three disciplines:

1. **Minimization** — choose the correct durable home, remove superseded wording, and keep the smallest sufficient behavioral contract without cutting safety or context.
2. **Self-checking** — falsify the candidate with conflict scans, positive/negative/boundary controls, actual decision outputs, and independent review.
3. **Simulation-driven self-improvement** — run baseline and candidate instruction snapshots against the same time-ordered evidence, compare observable decision vectors, then patch and replay.

The full loop:

1. define the old failure and expected behavioral delta;
2. compare the proposal with a smaller candidate;
3. audit every overlapping instruction surface;
4. run a hindsight-free two-arm counterfactual simulation;
5. test positive, negative, boundary, and minimization controls;
6. exercise actual tool order, stopping, severity, authorization, side effects, and completion claims;
7. require an independent adversarial `PASS` / `PARTIAL` / `FAIL` review;
8. patch only demonstrated gaps, minimize again, and replay;
9. preserve an auditable validation artifact.

It also forces an honest distinction between **manually validating one improvement** and **enforcing validation across every mutation path**.

## Why

A rewritten prompt can look perfect and still:

- lose to a conflicting instruction elsewhere;
- overfit the motivating incident;
- leak hindsight into the test;
- preserve the same premature stopping decision;
- broaden a safety or authorization rule;
- bypass review when changed through a different writer;
- be declared effective without independent evidence.

The core question is:

> If the original incident arrived now, with no hindsight, would these instructions force the desired investigation and prevent the old premature conclusion—without breaking the valid control case?

## Install

### Hermes Agent

```bash
hermes skills install AnimaApp/smarter-agent/skills/smarter-agent --yes
```

This full identifier is deterministic and works immediately after publication. It installs only the canonical skill bundle and its linked support files. The shorter `hermes skills install smarter-agent` form depends on source-index discovery and may lag a new repository.

Or copy `skills/smarter-agent/` into your Hermes skills directory.

### Claude Code, Codex, Cursor, and other skill-aware agents

Copy `skills/smarter-agent/` into the host's skills directory, or point the host at this repository. The skill remains opt-in unless the host's own skill system chooses it for a matching task. Instruction-file agents can use the repository's `AGENTS.md`; copying that file into another project intentionally makes the trigger active in that scope.

Host paths differ, but the canonical skill is always:

```text
skills/smarter-agent/SKILL.md
```

## Use

Load or invoke `smarter-agent` whenever a meaningful change is made to:

- skills or agent instructions;
- durable memory/profile conventions;
- system prompts or routing policies;
- safety/authorization boundaries;
- classification, evidence, escalation, or completion rules.

Then fill in [`skills/smarter-agent/templates/validation-report.md`](skills/smarter-agent/templates/validation-report.md). A specific change is behaviorally verified only when its behavioral verdict is `PASS`; unavailable independent review means behavioral `PARTIAL`. Runtime-enforcement coverage is reported separately, so one manually validated change cannot be mistaken for universal gating.

## Repository contents

- [`skills/smarter-agent/SKILL.md`](skills/smarter-agent/SKILL.md) — canonical, isolated skill.
- [`AGENTS.md`](AGENTS.md) — opt-in instruction-file adapter for hosts that load repository guidance.
- [`skills/smarter-agent/references/simulation-model.md`](skills/smarter-agent/references/simulation-model.md) — two-arm counterfactual model, decision vector, controls, and minimization objective.
- [`skills/smarter-agent/references/runtime-gating.md`](skills/smarter-agent/references/runtime-gating.md) — optional design guidance for hosts that choose to enforce universal mutation gating.
- [`skills/smarter-agent/templates/validation-report.md`](skills/smarter-agent/templates/validation-report.md) — replay and control artifact.
- [`validation/2026-08-19-initial-self-validation.md`](validation/2026-08-19-initial-self-validation.md) — the repository's own chronological review, controls, patches, and bounded verdict.
- [`scripts/check_bundle.py`](scripts/check_bundle.py) — deterministic bundle integrity check.
- [`tests/test_check_bundle.py`](tests/test_check_bundle.py) — positive and negative validator tests.

## What it does not claim

This repository provides the behavior and verification protocol. Installing it does **not** prove that your runtime intercepts every skill, memory, API, CLI, sync, cron, or direct-filesystem mutation. See the runtime coverage audit in the skill and [`skills/smarter-agent/references/runtime-gating.md`](skills/smarter-agent/references/runtime-gating.md).

## Validation

```bash
python3 scripts/check_bundle.py
python3 -m unittest discover -s tests -v
```

The checker validates structural completeness. It is not a substitute for replaying the changed agent behavior.

## License

MIT
