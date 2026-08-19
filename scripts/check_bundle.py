#!/usr/bin/env python3
"""Validate the structural and behavioral contracts of smarter-agent."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "scripts/check_bundle.py",
    "tests/test_check_bundle.py",
    "validation/2026-08-19-initial-self-validation.md",
    "skills/smarter-agent/SKILL.md",
    "skills/smarter-agent/references/simulation-model.md",
    "skills/smarter-agent/references/runtime-gating.md",
    "skills/smarter-agent/templates/validation-report.md",
)

SKILL = "skills/smarter-agent/SKILL.md"
REPORT = "skills/smarter-agent/templates/validation-report.md"
GATING = "skills/smarter-agent/references/runtime-gating.md"
SIMULATION = "skills/smarter-agent/references/simulation-model.md"

# Each invariant requires all patterns. These checks validate the documented
# contract's structure and semantics; actual behavioral proof still requires a
# chronological replay and independent review.
CONTRACTS: dict[str, dict[str, tuple[str, ...]]] = {
    SKILL: {
        "behavioral delta": (
            r"## The improvement loop",
            r"Define the behavioral delta",
            r"old failure",
            r"exact decision point",
            r"observable evidence",
        ),
        "three pillars": (
            r"### 1\. Minimization",
            r"### 2\. Self-checking",
            r"### 3\. Simulation-driven self-improvement",
            r"smallest sufficient behavioral contract",
        ),
        "minimization": (
            r"Minimize the proposed improvement",
            r"use memory for a compact, stable fact or preference",
            r"use a skill for a reusable procedure",
            r"Compare the proposed edit with at least one smaller alternative",
            r"do not mark the minimization control not applicable",
            r"Minimization is lexicographic",
            r"Never trade an earlier objective for fewer words",
        ),
        "complete conflict audit": (
            r"Audit the complete instruction surface",
            r"every linked reference, template, script, example, generated copy",
            r"synonyms, semantic equivalents",
        ),
        "two-arm simulation": (
            r"Run the counterfactual simulation",
            r"Baseline:.*old snapshot",
            r"Candidate:.*proposed snapshot",
            r"identical evidence sequence and checkpoints",
            r"Do not leak the eventual diagnosis",
            r"multiple trials and report the distribution",
        ),
        "positive negative boundary controls": (
            r"Add positive and negative controls",
            r"positive control",
            r"negative control",
            r"Add boundary controls",
            r"triggering everywhere fails",
        ),
        "actual decision output": (
            r"Exercise the actual decision output",
            r"not a keyword check",
            r"tools called and their order",
            r"stop/continue decision",
            r"side effect",
            r"completion claim",
        ),
        "independent review": (
            r"Require independent adversarial review",
            r"separate reviewer",
            r"Do not tell the reviewer the desired verdict",
            r"If an independent reviewer is unavailable, the result is `PARTIAL`",
        ),
        "patch and replay": (
            r"Patch, minimize, and replay again",
            r"Remove wording that the simulation proves unnecessary",
            r"Re-run the conflict audit",
            r"all positive and negative controls",
        ),
        "reviewable snapshots": (
            r"old and new snapshot content or durable artifact URI/path, plus a hash for each",
        ),
        "manual versus universal enforcement": (
            r"not proof that every agent mutation is automatically gated",
            r"Do not claim this loop runs on every self-improvement unless",
            r"If any supported mutation path bypasses the gate, report coverage as `PARTIAL` or `FAIL`",
        ),
        "pending gate": (
            r"captures old and new snapshots",
            r"persists `PENDING`, `PASS`, `PARTIAL`, or `FAIL`",
            r"Keep meaningful changes `PENDING` while validation runs",
            r"Prevent effectiveness claims.*`PENDING`, `PARTIAL`, or `FAIL`",
        ),
    },
    REPORT: {
        "snapshot artifacts and hashes": (
            r"Old snapshot artifact URI/path",
            r"Old snapshot SHA-256",
            r"New snapshot artifact URI/path",
            r"New snapshot SHA-256",
        ),
        "actual output report": (
            r"## Actual output exercised",
            r"Tool order",
            r"Stop/continue decision",
            r"Side-effect boundary",
            r"Completion claim",
        ),
        "control report": (
            r"### Positive control",
            r"### Negative control",
            r"### Boundary controls",
            r"### Minimization control",
            r"Smaller candidate or attempted reduction",
            r"why the attempted reduction failed",
            r"Result: PASS / FAIL",
        ),
        "simulation report": (
            r"## Counterfactual simulation setup",
            r"Frozen evidence sequence",
            r"Trial count per arm",
            r"Per-trial decision-vector results or durable artifact URI/path",
            r"Aggregate pass/fail distribution",
            r"Variance / instability observed",
            r"Acceptance statistic and threshold",
            r"Predeclared acceptance rule",
            r"## Chronological two-arm replay",
            r"Baseline decision vector",
            r"Candidate decision vector",
        ),
        "minimization report": (
            r"## Minimization audit",
            r"Smaller alternative tested",
            r"Duplicated or superseded concepts removed",
            r"Wording retained and why it is necessary",
        ),
        "independent report": (
            r"## Independent adversarial review",
            r"Reviewer/session",
            r"Isolation evidence",
            r"Exact failed checkpoint",
        ),
        "separate verdicts": (
            r"Behavioral validation verdict for this specific mutation",
            r"Runtime-enforcement coverage verdict across mutation paths",
            r"Behavioral `PASS` may coexist with runtime coverage `PARTIAL`",
            r"Universal-enforcement certification is `PASS` only when both",
            r"unavailable independent reviewer makes the behavioral verdict `PARTIAL`",
        ),
    },
    GATING: {
        "transaction snapshots": (
            r"captures an immutable old snapshot before any write",
            r"stages the proposed new snapshot",
            r"old and new content hashes plus immutable snapshots",
        ),
        "pending activation gate": (
            r"PROPOSED → STAGED → PENDING_VALIDATION → PASS → ACTIVE",
            r"must not be certified.*before `PASS`",
            r"old active snapshot unchanged on `PARTIAL`, `FAIL`, crash, or timeout",
        ),
        "writer coverage": (
            r"skill create, patch, edit",
            r"memory/profile writes",
            r"dashboard and API updates",
            r"repository synchronization",
            r"direct filesystem writers",
        ),
    },
    SIMULATION: {
        "isolated roles": (
            r"Improver:",
            r"Actor under test:",
            r"Simulator:",
            r"Evaluator:",
            r"self-critique in the improver's context does not qualify",
        ),
        "decision vector": (
            r"tool sequence",
            r"evidence requested",
            r"continue/stop",
            r"authorization or owner decision",
            r"side-effect boundary",
            r"completion claim",
        ),
        "lexicographic minimization": (
            r"Use lexicographic ordering",
            r"preserve safety and authorization",
            r"minimize changed instruction locations",
            r"Do not reward prompt golf",
        ),
        "stochastic honesty": (
            r"same trial count",
            r"predeclare the acceptance rule",
            r"report all trials or aggregate distributions",
            r"unstable or overlapping results as `PARTIAL`",
        ),
    },
    "AGENTS.md": {
        "three pillars": (
            r"\*\*Minimize:\*\*",
            r"\*\*Self-check:\*\*",
            r"\*\*Simulate improvement:\*\*",
            r"minimization controls",
            r"baseline and candidate snapshots",
        ),
        "opt-in scope": (
            r"public repository is self-contained and opt-in",
            r"do not modify an existing agent runtime by themselves",
        ),
        "no universal overclaim": (
            r"not evidence that every mutation path is automatically gated",
            r"report coverage as `PARTIAL` or `FAIL` and name the bypass",
        ),
    },
}

# Contradiction guards catch common semantic reversals that can otherwise sit
# beside the required wording and make a presence-only check pass.
FORBIDDEN_PATTERNS: dict[str, dict[str, tuple[str, ...]]] = {
    SKILL: {
        "safety subordinated to size": (
            r"(?:prioriti[sz]e|prefer|choose) (?:fewer words|shorter text|smaller prompts?).{0,80}(?:over|instead of) (?:safety|correctness|authorization)",
            r"(?:safety|correctness|authorization).{0,80}(?:may|can|should) be (?:cut|removed|sacrificed).{0,80}(?:shorter|smaller|fewer)",
            r"(?:shortness|brevity|compactness|size reduction).{0,80}(?:takes? precedence|outranks?|comes? before).{0,80}(?:safety|correctness|authorization)",
        ),
        "duplicate guidance": (
            r"(?:keep|add|prefer) (?:redundant|duplicate|duplicated) (?:rules|wording|instructions)",
            r"do not remove (?:redundant|duplicate|superseded) (?:rules|wording|instructions)",
            r"(?:retain|preserve|keep).{0,60}(?:repeated|redundant|duplicate) guidance.{0,80}(?:reinforce|emphasi[sz]e)",
        ),
        "negative control reversal": (
            r"(?m)^.*negative control[^\n]{0,100}(?:must|should) (?:trigger|take the new path)",
            r"(?m)^.*(?:trigger|take the new path)[^\n]{0,100}negative control",
            r"negative controls?.{0,100}(?:expected|required) to adopt (?:the )?changed behavior",
        ),
        "optional minimization": (
            r"minimization control.{0,100}(?:is optional|may be skipped)",
            r"minimization control.{0,100}(?:may|can) be marked (?:N/?A|not applicable)",
        ),
        "pillar skipping": (
            r"(?:skip|disable|ignore|omit) (?:the )?(?:minimization|self-checking|simulation) (?:pillar|phase|step|control)",
            r"(?:self-checking|simulation) (?:pillar|phase|step).{0,60}(?:can|may) be omitted",
        ),
    },
    SIMULATION: {
        "stochastic cherry-picking": (
            r"report (?:only )?(?:the )?(?:best|most favorable) trial",
            r"discard (?:failed|unfavorable) trials",
            r"publish (?:only )?(?:the )?(?:highest-scoring|best) run.{0,80}omit the rest",
        ),
        "arm contamination": (
            r"use different evidence (?:for|in) (?:each|the) arm",
            r"share (?:the )?(?:baseline|candidate) output with the other arm",
        ),
        "self-review substitution": (
            r"self-critique.{0,80}(?:qualifies|counts) as independent",
        ),
    },
    REPORT: {
        "stochastic cherry-picking": (
            r"report (?:only )?(?:the )?(?:best|most favorable) trial",
            r"publish (?:only )?(?:the )?(?:highest-scoring|best) run.{0,80}omit the rest",
        ),
        "optional minimization result": (
            r"### Minimization control[\s\S]{0,500}Result:.*NOT APPLICABLE",
        ),
        "negative control reversal": (
            r"(?m)^.*negative control[^\n]{0,100}(?:must|should) (?:trigger|take the new path)",
        ),
    },
    "AGENTS.md": {
        "scope contradiction": (
            r"(?:not|no longer) opt-in",
            r"appl(?:y|ies) globally (?:without|regardless of) (?:installation|consent|user action)",
            r"automatically modif(?:y|ies) (?:the )?(?:existing|live) agent runtime",
            r"universal enforcement (?:is )?guaranteed",
            r"govern(?:s)? every agent.{0,100}even if nobody installs",
        ),
        "pillar contradiction": (
            r"(?:skip|disable|ignore) (?:the )?(?:minimization|self-check|simulation) (?:pillar|step|control)",
        ),
    },
}


def _read(path: Path, errors: list[str], relative: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {relative}: {exc}")
        return ""


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {relative}")

    for relative, contracts in CONTRACTS.items():
        path = root / relative
        if not path.is_file():
            continue
        text = _read(path, errors, relative)
        for invariant, patterns in contracts.items():
            missing = [pattern for pattern in patterns if not re.search(pattern, text, re.IGNORECASE | re.DOTALL)]
            if missing:
                errors.append(
                    f"{relative} violates contract '{invariant}'; missing: " + ", ".join(missing)
                )

    for relative, forbidden_groups in FORBIDDEN_PATTERNS.items():
        path = root / relative
        if not path.is_file():
            continue
        text = _read(path, errors, relative)
        for invariant, patterns in forbidden_groups.items():
            matched = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE | re.DOTALL)]
            if matched:
                errors.append(
                    f"{relative} contradicts contract '{invariant}'; forbidden: " + ", ".join(matched)
                )

    skill_path = root / SKILL
    if skill_path.is_file():
        text = _read(skill_path, errors, SKILL)
        if not text.startswith("---\n") or "\nname: smarter-agent\n" not in text:
            errors.append("skill frontmatter is missing or has the wrong name")

        # Hermes resolves support paths relative to the installable skill dir.
        skill_dir = skill_path.parent
        linked = set(re.findall(r"`((?:references|templates|scripts|assets)/[^`]+)`", text))
        expected = {
            "references/runtime-gating.md",
            "references/simulation-model.md",
            "templates/validation-report.md",
        }
        if not expected.issubset(linked):
            errors.append(f"skill must link bundled support files: {sorted(expected - linked)}")
        for relative in sorted(linked):
            target = skill_dir / relative
            if not target.is_file() or target.stat().st_size == 0:
                errors.append(f"missing or empty linked support file: {relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: smarter-agent bundle satisfies all documented contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
