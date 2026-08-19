# Self-improvement validation report

## Mutation

- Target:
- Mutation path / writer:
- Origin session or evidence:
- Old snapshot artifact URI/path:
- Old snapshot SHA-256:
- New snapshot artifact URI/path:
- New snapshot SHA-256:
- Behavioral significance: meaningful / non-behavioral

## Intended delta

- Old failure:
- New expected behavior:
- Exact decision point:
- Observable proof:

## Minimization audit

- Durable home chosen (memory / existing skill / new skill / other):
- Smaller alternative tested:
- Instruction locations added / changed / removed:
- Approximate tokens or lines added / removed:
- Duplicated or superseded concepts removed:
- Wording retained and why it is necessary:
- Safety/authorization/evidence clauses preserved:

## Instruction-surface conflict audit

| Surface | Old wording / semantic equivalent searched | Finding | Resolved? |
|---|---|---|---|
| | | | |

## Counterfactual simulation setup

- Fixture / motivating case:
- Frozen evidence sequence:
- Baseline snapshot:
- Candidate snapshot:
- Model, tools, and settings held constant:
- Trial count per arm:
- Per-trial decision-vector results or durable artifact URI/path:
- Aggregate pass/fail distribution:
- Variance / instability observed:
- Acceptance statistic and threshold:
- Predeclared acceptance rule:
- Evaluator rubric/version:

## Chronological two-arm replay

Do not include evidence before it was originally available or leak one arm's output into the other.

| Checkpoint | Evidence available then | Baseline decision vector | Candidate decision vector | Expected divergence | Result |
|---|---|---|---|---|---|
| | | | | | |

## Controls

### Positive control

- Fixture:
- Expected trigger:
- Actual decision output:
- Result: PASS / FAIL

### Negative control

- Similar fixture that must not trigger:
- Expected preserved path:
- Actual decision output:
- Result: PASS / FAIL

### Boundary controls

- Authorization / threshold / severity edge:
- Expected:
- Actual:
- Result: PASS / FAIL / NOT APPLICABLE

### Minimization control

- Smaller candidate or attempted reduction:
- If no smaller candidate survived, why the attempted reduction failed:
- Decision-vector equivalence across replay and controls:
- Chosen candidate and reason:
- Result: PASS / FAIL

## Actual output exercised

- Tool order:
- Stop/continue decision:
- Severity/classification:
- Authorization/owner decision:
- Side-effect boundary:
- Completion claim:

## Independent adversarial review

- Reviewer/session:
- Isolation evidence:
- Verdict: PASS / PARTIAL / FAIL
- Residual gaps:
- Exact failed checkpoint(s):

## Patch and rerun

| Patch | Reason | Replayed checkpoints/controls | Result |
|---|---|---|---|
| | | | |

## Runtime coverage

- Mutation paths verified:
- Mutation paths bypassing the gate:
- Coverage verdict: PASS / PARTIAL / FAIL

## Verdicts and certification scope

- Behavioral validation verdict for this specific mutation: PASS / PARTIAL / FAIL
- Runtime-enforcement coverage verdict across mutation paths: PASS / PARTIAL / FAIL
- Remaining limitations:
- Activation/certification decision:

Certification semantics:

- The specific mutation is behaviorally verified only when its behavioral verdict is `PASS`.
- Behavioral `PARTIAL` or `FAIL` blocks an effectiveness claim for that mutation.
- Behavioral `PASS` may coexist with runtime coverage `PARTIAL`: the report may say **this mutation was replay-validated**, but must not claim the runtime universally enforces the loop.
- Universal-enforcement certification is `PASS` only when both behavioral validation and runtime-enforcement coverage are `PASS`.
- An unavailable independent reviewer makes the behavioral verdict `PARTIAL`.

A replay pass is evidence, not a guarantee of future model behavior.
