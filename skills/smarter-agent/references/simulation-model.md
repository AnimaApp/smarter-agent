# Simulation model

`smarter-agent` treats instruction improvement as a controlled counterfactual experiment, not a prose-editing task.

## Roles

- **Improver:** proposes the smallest candidate change and states the target failure.
- **Actor under test:** makes decisions from an instruction snapshot and time-ordered evidence.
- **Simulator:** presents identical fixtures and evidence checkpoints to each arm; it must not reveal future evidence.
- **Evaluator:** independently compares outputs against a frozen rubric and controls. It does not edit the candidate.

A single model may play different roles only in isolated contexts with fresh prompts and no leaked conclusions. Independent evaluation still requires a separate context or agent; self-critique in the improver's context does not qualify.

## Two-arm counterfactual

### Baseline arm

- Load the immutable old instruction snapshot.
- Reveal evidence in the original chronological order.
- Capture the actual decision at every checkpoint.

### Candidate arm

- Load the immutable proposed snapshot.
- Use the same model configuration, tools, fixture, evidence order, and checkpoints when the host permits.
- Capture the same decision fields.

Do not share chain-of-thought, eventual diagnosis, evaluator conclusions, or one arm's outputs with the other arm. The durable artifact should contain decisions and concise rationales, not private hidden reasoning.

## Decision vector

At every checkpoint compare observable behavior:

```text
(tool sequence,
 evidence requested,
 continue/stop,
 classification/severity,
 authorization or owner decision,
 side-effect boundary,
 completion claim)
```

A wording difference with an unchanged decision vector is not behavioral improvement.

## Controls

- **Positive control:** the motivating failure must take the desired new path.
- **Negative control:** a similar valid case must remain on its prior path.
- **Boundary controls:** exercise thresholds, authorization edges, severity transitions, empty evidence, and ambiguous evidence where relevant.
- **Minimization control:** compare the candidate with a smaller alternative. If the smaller version preserves every decision vector, prefer it. If no plausible smaller candidate exists, document the attempted reduction and why it failed; the control is never silently skipped.

## Optimization objective

Use lexicographic ordering, not one blended score:

1. preserve safety and authorization;
2. correct the motivating failure;
3. preserve negative and boundary controls;
4. avoid unresolved instruction conflicts;
5. minimize changed instruction locations, duplicated concepts, and tokens/lines;
6. prefer clearer wording when size is equivalent.

A smaller candidate that loses an earlier objective is worse. Do not reward prompt golf.

## Deterministic and stochastic runs

For deterministic paths, one exact replay per arm can be sufficient when all decision outputs and controls are captured.

For stochastic model behavior:

- pin model/version/settings where possible;
- use the same trial count and fixtures per arm;
- predeclare the acceptance rule;
- report all trials or aggregate distributions, not a selected favorable run;
- treat unstable or overlapping results as `PARTIAL` unless the acceptance rule is met.

## Acceptance rule

The evaluator returns:

- `PASS` when the candidate fixes the positive case, preserves all controls and safety boundaries, has no material conflict, and no tested smaller candidate is equally effective;
- `PARTIAL` when evidence, independence, stability, minimization, or mutation-path coverage is incomplete;
- `FAIL` when the target failure survives, any valid control regresses, safety/authorization broadens, or a material conflict remains.

After `PARTIAL` or `FAIL`, patch only the demonstrated gap, minimize again, and replay both arms at the failed checkpoints plus all controls.

## Honest limitations

This simulation estimates future behavior; it does not guarantee it. Results are scoped to the snapshots, fixtures, models, tools, and mutation paths tested. Installing the skill does not create a universal runtime gate.
