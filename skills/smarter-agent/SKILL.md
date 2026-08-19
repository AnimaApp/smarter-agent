---
name: smarter-agent
description: "Use after meaningful instruction changes; replay behavior, test controls, and independently verify improvement."
version: 1.0.0
author: Ofer LaOr
license: MIT
metadata:
  tags: [self-improvement, agent-skills, validation, simulation, evals]
---

# Smarter Agent

Make self-improvement minimal, simulated, and evidence-driven. Whenever an agent meaningfully changes a skill, memory-backed convention, system prompt, routing rule, safety boundary, or completion policy, improve the smallest sufficient instruction surface and validate the resulting behavior before calling the change effective.

This skill is a verification and optimization discipline, not proof that every agent mutation is automatically gated. Follow the loop below manually unless the host runtime demonstrably enforces it for every mutation path.

## Three pillars

### 1. Minimization

Make the smallest durable change that forces the desired decision. Choose the correct instruction surface, remove redundant or superseded wording, and minimize tokens and semantic surface only after preserving correctness, safety, authorization, and necessary context. Minimal means **smallest sufficient behavioral contract**, not shortest text.

### 2. Self-checking

Falsify the candidate change before accepting it. Audit conflicts, compare old and candidate decisions, run positive, negative, and boundary controls, inspect the actual decision output, and require an independent verdict.

### 3. Simulation-driven self-improvement

Use a counterfactual simulation model with two arms:

- **baseline arm:** replay the case under the old instruction snapshot;
- **candidate arm:** replay the same evidence chronology under the proposed snapshot.

An independent evaluator compares decisions at each checkpoint. The candidate is accepted only if it fixes the target failure, preserves valid controls, and is no broader than necessary. See `references/simulation-model.md`.

## Trigger

Run this loop after a change that can alter a decision: priority or tool order, escalation or stopping criteria, authorization or safety boundaries, classification, evidence thresholds, remediation choices, cross-system routing, what the agent claims as complete, or where durable knowledge is stored.

Skip only typo, formatting, or purely factual reference updates that cannot change a decision. When uncertain, run the loop.

## The improvement loop

### 1. Define the behavioral delta

Write down:

- the old failure;
- the new expected behavior;
- the exact decision point where the result should diverge;
- observable evidence that would prove the divergence.

Do not use “the wording changed” as success evidence.

### 2. Minimize the proposed improvement

Choose the narrowest durable home for the behavior:

- use memory for a compact, stable fact or preference;
- use a skill for a reusable procedure, decision rule, or multi-step workflow;
- update an existing rule instead of creating a duplicate when ownership is clear;
- remove or replace superseded wording so old and new rules cannot both fire;
- keep examples only when they disambiguate a decision boundary;
- preserve safety, authorization, evidence, and failure-handling clauses even when they cost tokens.

Compare the proposed edit with at least one smaller alternative. Prefer the smaller one only if both produce the same correct decisions across the replay and controls. If no plausible smaller wording exists, record the attempted reduction and why it failed; do not mark the minimization control not applicable. Record instruction locations touched, added/removed token or line counts, duplicated concepts removed, and why any remaining wording is necessary.

Minimization is lexicographic: first correctness and safety, then target behavior, then non-regression, then smaller instruction surface. Never trade an earlier objective for fewer words.

### 3. Audit the complete instruction surface

Inspect the edited file and every linked reference, template, script, example, generated copy, installed duplicate, durable memory/profile convention, platform prompt, scheduled-job prompt, and repository mirror that can influence the same decision.

Search for the old phrase, synonyms, semantic equivalents, and conflicting higher-priority instructions. Record each surface inspected and every unresolved conflict.

### 4. Run the counterfactual simulation

Select a real prior failure or a preserved equivalent fixture. Freeze the evidence sequence and run two isolated arms:

1. **Baseline:** old snapshot, evidence revealed in original chronological order.
2. **Candidate:** proposed snapshot, the identical evidence sequence and checkpoints.

Do not leak the eventual diagnosis, desired answer, later evidence, or one arm's output into the other. Keep tools, model settings, fixtures, and evaluator rubric fixed where the host permits. When stochasticity matters, run multiple trials and report the distribution rather than choosing a favorable sample.

At each checkpoint, record:

- evidence available then;
- decision under the old instructions;
- decision under the changed instructions;
- whether tool order, stopping criteria, severity, owner decision, side-effect boundary, or completion claim actually changed.

### 5. Add positive and negative controls

The positive control is the motivating failure: the new behavior must trigger.

Add at least one negative control that resembles the failure but must preserve the old valid path. Add boundary controls when the rule has thresholds, authorization edges, or severity levels. A change that “fixes” the incident by triggering everywhere fails.

### 6. Exercise the actual decision output

Simulate or run the real decision path, not a keyword check. Verify the output that matters: tools called and their order, evidence requested, stop/continue decision, severity, authorization check, requested owner input, side effect, and final completion claim.

Never execute destructive or externally visible side effects merely to test this skill. Use fixtures, mocks, dry runs, sandboxes, or read-only probes. If safe simulation cannot cover the boundary, mark it unverified.

### 7. Require independent adversarial review

Give a separate reviewer the original evidence, old and new instruction surfaces, replay transcript, and controls. Forbid edits. Do not tell the reviewer the desired verdict.

Require one rating:

- `PASS`: desired behavior changes, valid behavior is preserved, and no material conflict remains;
- `PARTIAL`: some behavior improved, but coverage, evidence, or controls are incomplete;
- `FAIL`: the old failure survives, a control regresses, or a material conflict remains.

The reviewer must identify residual gaps and the exact checkpoint where each appears. If an independent reviewer is unavailable, the result is `PARTIAL`, never `PASS`.

### 8. Patch, minimize, and replay again

Apply only validated fixes. Remove wording that the simulation proves unnecessary, then re-run the conflict audit, both simulation arms at the failed checkpoint, all positive and negative controls, and independent review. Do not call the change effective while any material finding is unresolved or the rating is `PARTIAL`/`FAIL`.

### 9. Preserve an auditable artifact

Record:

- change and intended delta;
- old and new snapshot content or durable artifact URI/path, plus a hash for each;
- alternative candidate considered, instruction-surface delta, duplicated wording removed, and why remaining text is necessary;
- baseline and candidate simulation settings, trials, and checkpoint outputs;
- instruction surfaces inspected;
- chronological evidence and decisions;
- positive, negative, and boundary controls;
- expected versus actual behavior;
- independent verdict and residual gaps;
- patches applied and rerun results;
- final `PASS`/`PARTIAL`/`FAIL`;
- limitations and untested mutation paths.

A successful replay is evidence, not a guarantee of future model behavior.

## Default falsification question

> If the original incident arrived now, with no hindsight, would these instructions force the desired investigation and prevent the old premature conclusion—without breaking the valid control case?

If the answer is not demonstrated by the replay, the change is not verified.

## Runtime coverage audit

Do not claim this loop runs on every self-improvement unless the live runtime has been verified across every writer, including:

- foreground skill create/edit/patch/support-file operations;
- memory and profile updates;
- background curator or self-improvement jobs;
- dashboard/API full-content updates;
- CLI, registry, hub, install, update, and sync operations;
- direct filesystem and repository changes;
- cron or delegated sessions that bypass normal review.

For each path, verify that the system captures old and new snapshots, classifies behavioral significance, associates origin/session/evidence, runs conflict scan + chronological replay + controls + independent review, and persists `PENDING`, `PASS`, `PARTIAL`, or `FAIL`.

A periodic review, post-write callback, generic counter reset, or the existence of this skill is not universal enforcement. If any supported mutation path bypasses the gate, report coverage as `PARTIAL` or `FAIL` and name the bypass.

## Strong runtime design

Universal enforcement requires a shared mutation transaction used by every supported writer:

1. Capture the old snapshot before mutation.
2. Stage and capture the new snapshot after mutation.
3. Persist origin, session, path, evidence, and significance classification.
4. Keep meaningful changes `PENDING` while validation runs.
5. Run conflict audit, chronological replay, controls, and independent review.
6. Persist the artifact and final rating.
7. Prevent effectiveness claims—and preferably activation—while status is `PENDING`, `PARTIAL`, or `FAIL`.
8. Reconcile direct/out-of-process file changes with a watcher that can recover both snapshots or refuse to certify them.

A post-write hook alone is insufficient because it may miss the old snapshot and out-of-process writers.

## Failure rules

- No hindsight in chronological replay.
- No `PASS` based only on prose, grep, schema validity, or a successful write.
- No self-review substituted for independent review.
- No activation/effectiveness claim with unresolved material findings.
- No silent broadening of authorization or side effects.
- No destructive live test when a fixture or read-only probe can exercise the decision.
- No claim of universal coverage without mutation-path evidence.

Use `templates/validation-report.md` for the artifact and `references/runtime-gating.md` when implementing host-level enforcement.
