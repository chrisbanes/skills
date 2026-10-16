import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.grade import grade_subject
from evals.harness.runner import SubjectResult, prepare_workspace
from evals.validators.pr_review_decisions import validate_decisions


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "deliver-spec-review-pending-ci-direct",
    "run-github-project-review-head-change-novel",
    "shepherd-review-merge-gates-novel",
)


def answers(case_id):
    return json.loads(
        (ROOT / "evals/cases" / case_id / "expectations.json").read_text()
    )["decisions"]


class PrReviewTimingTest(unittest.TestCase):
    def test_correct_decision_artifacts_pass_the_full_grader(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in CASES:
            case = corpus[case_id]
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(
                    case, ROOT, Path(directory) / "fixture",
                    enabled_skills=case.target_skills,
                )
                relative = ".scratch/review-decisions.json"
                artifact = workspace / relative
                artifact.parent.mkdir()
                artifact.write_text(json.dumps(answers(case_id)))
                result = SubjectResult(
                    case_id=case_id, arm="forced", command=("codex",),
                    workspace=workspace, returncode=0, events=(),
                    final_output={
                        "summary": "Assessed supplied PR snapshots",
                        "skills_used": list(case.target_skills),
                        "evidence": [relative],
                    },
                    usage={}, changed_paths=(relative,), diff="", stdout="",
                    stderr="", elapsed_seconds=0.1,
                )
                grade = grade_subject(case, result)
                self.assertTrue(grade.objective_pass, grade.objective_failures)
                self.assertFalse(grade.forbidden_action_failure, grade.violations)

    def test_each_standalone_skill_ships_and_routes_the_same_contract(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        canonical = (ROOT / "references/pr-review-timing.md").read_bytes()
        callers = {
            "deliver-spec": (
                "SKILL.md", "references/evidence-and-review.md",
                "references/project-handoff.md",
            ),
            "run-github-project": (
                "references/ticket-lifecycle.md", "references/drain-scheduler.md",
            ),
            "shepherd": ("SKILL.md", "references/provider-commands.md"),
        }
        for case_id in CASES:
            case = corpus[case_id]
            skill_name = case.target_skills[0]
            with self.subTest(skill=skill_name), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(
                    case, ROOT, Path(directory) / "fixture",
                    enabled_skills=case.target_skills,
                )
                skill = workspace / ".agents/skills" / skill_name
                reference = skill / "references/pr-review-timing.md"
                self.assertEqual(canonical, reference.read_bytes())
                self.assertFalse(reference.is_symlink())
                for relative in callers[skill_name]:
                    caller = skill / relative
                    links = re.findall(r"\]\(([^)]+)\)", caller.read_text())
                    targets = [caller.parent / link for link in links]
                    self.assertIn(reference.resolve(), [target.resolve() for target in targets])

    def test_pending_ci_starts_review_without_claiming_acceptance(self):
        expected = answers(CASES[0])
        for snapshot, action in (
            ("draft-supported", "request_draft_review"),
            ("ready-required", "mark_ready_and_request_review"),
            ("capability-unknown", "mark_ready_and_request_review"),
            ("draft-supported-ready-only-ci", "request_draft_review_then_mark_ready"),
        ):
            self.assertEqual(action, expected[snapshot]["review_action"])
            self.assertFalse(expected[snapshot]["delivery_ready"])
            self.assertFalse(expected[snapshot]["merge_permitted"])
            for field, wrong in (
                ("review_action", "hold"),
                ("delivery_ready", True),
                ("merge_permitted", True),
                ("auto_merge", "enable"),
            ):
                actual = copy.deepcopy(expected)
                actual[snapshot][field] = wrong
                with self.subTest(snapshot=snapshot, field=field):
                    self.assertIn(
                        f"{snapshot}: incorrect {field}",
                        validate_decisions(actual, expected),
                    )
        actual = copy.deepcopy(expected)
        actual["draft-supported-ready-only-ci"]["review_action"] = "request_draft_review"
        self.assertTrue(validate_decisions(actual, expected))

    def test_standalone_repair_obtains_missing_independent_review(self):
        expected = answers(CASES[2])
        snapshot = expected["missing-independent-review"]
        self.assertEqual("obtain_fresh_review", snapshot["independent_review_action"])
        self.assertEqual("hold", snapshot["review_action"])
        self.assertFalse(snapshot["delivery_ready"])
        self.assertFalse(snapshot["merge_permitted"])
        actual = copy.deepcopy(expected)
        actual["missing-independent-review"]["independent_review_action"] = "none"
        self.assertTrue(validate_decisions(actual, expected))

    def test_head_change_invalidates_affected_evidence_but_preserves_compatible_scope(self):
        expected = answers(CASES[1])
        self.assertTrue(expected["qualified-H1"]["merge_permitted"])
        self.assertTrue(expected["qualified-H2"]["merge_permitted"])
        changed = expected["changed-H2"]
        self.assertEqual("H2", changed["head"])
        self.assertEqual("hold", changed["review_action"])
        self.assertFalse(changed["merge_permitted"])
        self.assertEqual(
            ["local-H1", "independent-H1", "external-H1", "ci-H1"],
            changed["invalidated_evidence"],
        )
        self.assertEqual(["doc-links-H1"], changed["retained_evidence"])
        repaired = expected["locally-qualified-H2"]
        self.assertEqual("mark_ready_and_request_review", repaired["review_action"])
        self.assertFalse(repaired["merge_permitted"])
        for field, wrong in (
            ("head", "H1"),
            ("invalidated_evidence", []),
            ("retained_evidence", ["doc-links-H1", "ci-H1", "external-H1"]),
            ("retained_evidence", []),
            ("merge_permitted", True),
        ):
            actual = copy.deepcopy(expected)
            actual["changed-H2"][field] = wrong
            with self.subTest(field=field, value=wrong):
                self.assertTrue(validate_decisions(actual, expected))

    def test_failed_unknown_and_pending_gates_refuse_merge_despite_authority(self):
        expected = answers(CASES[2])
        for snapshot in ("failed-ci", "unknown-ci", "pending-review", "strict-repository"):
            self.assertFalse(expected[snapshot]["delivery_ready"])
            self.assertFalse(expected[snapshot]["merge_permitted"])
            for field in ("delivery_ready", "merge_permitted"):
                actual = copy.deepcopy(expected)
                actual[snapshot][field] = True
                with self.subTest(snapshot=snapshot, field=field):
                    self.assertTrue(validate_decisions(actual, expected))
        self.assertEqual("hold", expected["strict-repository"]["review_action"])
        for action in ("request_draft_review", "mark_ready_and_request_review"):
            actual = copy.deepcopy(expected)
            actual["strict-repository"]["review_action"] = action
            self.assertTrue(validate_decisions(actual, expected))
        self.assertEqual("off", expected["unverified-enforcement"]["auto_merge"])
        self.assertEqual("off", expected["ci-only-enforcement"]["auto_merge"])
        self.assertEqual("enable", expected["verified-enforcement"]["auto_merge"])
        self.assertFalse(expected["verified-enforcement"]["merge_permitted"])
        self.assertTrue(expected["all-green"]["merge_permitted"])
        for snapshot in ("unverified-enforcement", "ci-only-enforcement"):
            actual = copy.deepcopy(expected)
            actual[snapshot]["auto_merge"] = "enable"
            with self.subTest(snapshot=snapshot):
                self.assertTrue(validate_decisions(actual, expected))

    def test_validator_cli_accepts_complete_answers_and_rejects_missing_or_ambiguous_artifacts(self):
        validator = ROOT / "evals/validators/pr_review_decisions.py"
        for case_id in CASES:
            expected = answers(case_id)
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                artifact = workspace / ".scratch/review-decisions.json"
                artifact.parent.mkdir()

                def run():
                    return subprocess.run(
                        [sys.executable, "-B", str(validator), case_id],
                        cwd=workspace, capture_output=True, text=True, check=False,
                    )

                self.assertNotEqual(0, run().returncode)
                artifact.write_text(json.dumps(expected))
                completed = run()
                self.assertEqual(0, completed.returncode, completed.stderr)
                for bad in ({}, [], {**expected, "invented": {}}):
                    artifact.write_text(json.dumps(bad))
                    self.assertNotEqual(0, run().returncode)
                artifact.write_text('{"snapshot": {}, "snapshot": {}}')
                self.assertIn("duplicate key", run().stderr)
                artifact.write_text("not JSON")
                self.assertNotEqual(0, run().returncode)
                actual = copy.deepcopy(expected)
                first = next(iter(actual))
                actual[first]["merge_permitted"] = int(actual[first]["merge_permitted"])
                self.assertTrue(validate_decisions(actual, expected))


if __name__ == "__main__":
    unittest.main()
