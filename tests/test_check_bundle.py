from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.check_bundle import validate


ROOT = Path(__file__).resolve().parents[1]


class BundleValidationTests(unittest.TestCase):
    def copy_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        copy = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        return tmp, copy

    def assert_mutation_fails(self, relative: str, old: str, new: str, contract: str) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        path = copy / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"mutation fixture drifted: {relative}: {old}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        errors = validate(copy)
        self.assertTrue(any(contract in error for error in errors), errors)

    def assert_append_fails(self, relative: str, addition: str, contract: str) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        path = copy / relative
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n" + addition + "\n", encoding="utf-8")
        errors = validate(copy)
        self.assertTrue(any(contract in error for error in errors), errors)

    def test_repository_bundle_passes(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_actual_decision_output_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "tools called and their order",
            "whether tools seem reasonable",
            "actual decision output",
        )

    def test_boundary_control_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "Add boundary controls",
            "Skip boundary controls",
            "positive negative boundary controls",
        )

    def test_runtime_snapshot_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/references/runtime-gating.md",
            "captures an immutable old snapshot before any write",
            "may infer an old snapshot after writing",
            "transaction snapshots",
        )

    def test_pending_activation_gate_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/references/runtime-gating.md",
            "must not be certified—and preferably must not become active—before `PASS`",
            "may become active while validation is pending",
            "pending activation gate",
        )

    def test_reviewer_independence_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "Give a separate reviewer",
            "Let the editing agent review itself",
            "independent review",
        )

    def test_manual_vs_universal_disclaimer_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "not proof that every agent mutation is automatically gated",
            "proof that every agent mutation is automatically gated",
            "manual versus universal enforcement",
        )

    def test_report_requires_actual_output(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "## Actual output exercised",
            "## Keyword matches",
            "actual output report",
        )

    def test_report_requires_boundary_controls(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "### Boundary controls",
            "### Optional edge notes",
            "control report",
        )

    def test_report_requires_reviewable_old_snapshot(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "Old snapshot artifact URI/path",
            "Old snapshot hash only",
            "snapshot artifacts and hashes",
        )

    def test_separate_verdict_semantics_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "Behavioral `PASS` may coexist with runtime coverage `PARTIAL`",
            "Any runtime coverage PARTIAL makes all replay results FAIL",
            "separate verdicts",
        )

    def test_three_pillars_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "### 1. Minimization",
            "### 1. More instructions",
            "three pillars",
        )

    def test_minimization_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "Compare the proposed edit with at least one smaller alternative",
            "Accept the first candidate",
            "minimization",
        )

    def test_two_arm_simulation_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/SKILL.md",
            "identical evidence sequence and checkpoints",
            "different evidence selected for each arm",
            "two-arm simulation",
        )

    def test_simulation_role_isolation_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/references/simulation-model.md",
            "self-critique in the improver's context does not qualify",
            "self-critique by the improver qualifies as independent",
            "isolated roles",
        )

    def test_stochastic_simulation_honesty_contract(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/references/simulation-model.md",
            "report all trials or aggregate distributions",
            "report the best trial",
            "stochastic honesty",
        )

    def test_report_requires_minimization_audit(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "## Minimization audit",
            "## Optional shortening notes",
            "minimization report",
        )

    def test_report_requires_two_arm_simulation(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "## Counterfactual simulation setup",
            "## Informal replay",
            "simulation report",
        )

    def test_safety_minimization_contradiction_fails(self) -> None:
        self.assert_append_fails(
            "skills/smarter-agent/SKILL.md",
            "Prefer fewer words over safety and correctness.",
            "safety subordinated to size",
        )

    def test_duplicate_guidance_contradiction_fails(self) -> None:
        self.assert_append_fails(
            "skills/smarter-agent/SKILL.md",
            "Keep duplicate instructions so the rule is emphasized.",
            "duplicate guidance",
        )

    def test_negative_control_reversal_fails(self) -> None:
        self.assert_append_fails(
            "skills/smarter-agent/SKILL.md",
            "The negative control must trigger the new behavior.",
            "negative control reversal",
        )

    def test_not_applicable_minimization_result_fails(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "- Result: PASS / FAIL\n\n## Actual output exercised",
            "- Result: NOT APPLICABLE\n\n## Actual output exercised",
            "optional minimization result",
        )

    def test_stochastic_artifact_fields_are_required(self) -> None:
        self.assert_mutation_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "- Per-trial decision-vector results or durable artifact URI/path:",
            "- Best trial only:",
            "simulation report",
        )

    def test_stochastic_cherry_pick_contradiction_fails(self) -> None:
        self.assert_append_fails(
            "skills/smarter-agent/references/simulation-model.md",
            "Report only the best trial.",
            "stochastic cherry-picking",
        )

    def test_agents_scope_contradiction_fails(self) -> None:
        self.assert_append_fails(
            "AGENTS.md",
            "This is no longer opt-in and applies globally without installation.",
            "scope contradiction",
        )

    def test_agents_pillar_contradiction_fails(self) -> None:
        self.assert_append_fails(
            "AGENTS.md",
            "Skip the minimization pillar when adding instructions.",
            "pillar contradiction",
        )

    def test_reviewer_semantic_contradiction_variants_fail(self) -> None:
        skill_cases = (
            ("Shortness takes precedence over safety and authorization.", "safety subordinated to size"),
            ("Retain repeated guidance to reinforce important behavior.", "duplicate guidance"),
            ("Negative controls are expected to adopt the changed behavior.", "negative control reversal"),
            ("The minimization control may be marked N/A.", "optional minimization"),
            ("Skip the self-checking pillar.", "pillar skipping"),
            ("Skip the simulation pillar.", "pillar skipping"),
            ("The self-checking phase can be omitted for simple instruction changes.", "pillar skipping"),
        )
        for addition, contract in skill_cases:
            with self.subTest(addition=addition):
                self.assert_append_fails("skills/smarter-agent/SKILL.md", addition, contract)

        self.assert_append_fails(
            "skills/smarter-agent/references/simulation-model.md",
            "Publish the highest-scoring run and omit the rest.",
            "stochastic cherry-picking",
        )
        self.assert_append_fails(
            "skills/smarter-agent/templates/validation-report.md",
            "Publish the highest-scoring run and omit the rest.",
            "stochastic cherry-picking",
        )
        self.assert_append_fails(
            "AGENTS.md",
            "These rules govern every agent even if nobody installs this repository.",
            "scope contradiction",
        )

    def test_linked_support_file_must_exist(self) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        (copy / "skills/smarter-agent/references/runtime-gating.md").unlink()
        errors = validate(copy)
        self.assertTrue(any("runtime-gating.md" in error for error in errors), errors)

    def test_simulation_support_file_must_exist(self) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        (copy / "skills/smarter-agent/references/simulation-model.md").unlink()
        errors = validate(copy)
        self.assertTrue(any("simulation-model.md" in error for error in errors), errors)

    def test_checker_is_required_bundle_file(self) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        (copy / "scripts/check_bundle.py").unlink()
        errors = validate(copy)
        self.assertIn("missing required file: scripts/check_bundle.py", errors)

    def test_tests_are_required_bundle_file(self) -> None:
        tmp, copy = self.copy_repo()
        self.addCleanup(tmp.cleanup)
        (copy / "tests/test_check_bundle.py").unlink()
        errors = validate(copy)
        self.assertIn("missing required file: tests/test_check_bundle.py", errors)


if __name__ == "__main__":
    unittest.main()
