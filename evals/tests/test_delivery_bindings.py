import copy
from dataclasses import replace
import json
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.grade import grade_subject
from evals.harness.runner import SubjectResult, prepare_workspace
from evals.validators.pr_review_decisions import validate_decisions
from scripts.sync_references import COPIES


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "deliver-spec-provider-closure-direct",
    "deliver-spec-provider-closure-novel",
    "deliver-spec-provider-closure-negative",
    "jira-board-scope-direct",
    "jira-direct-closure-novel",
    "jira-transition-marker-negative",
    "gitlab-code-host-delivery-direct",
    "gitlab-code-host-config-novel",
    "gitlab-code-host-closure-negative",
    "shepherd-gitlab-discussions-novel",
)


class DeliveryBindingsTest(unittest.TestCase):
    def test_closure_decisions_use_the_existing_offline_grader(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in CASES:
            case = corpus[case_id]
            expected = json.loads((case.directory / "expectations.json").read_text()).get("decisions")
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(
                    case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills,
                )
                relative = ".scratch/review-decisions.json"
                artifact = workspace / relative
                response_mode = case_id == "jira-transition-marker-negative"
                writes_artifact = expected is not None and not response_mode
                if writes_artifact:
                    artifact.parent.mkdir()
                    artifact.write_text(json.dumps(expected))
                result = SubjectResult(
                    case_id=case_id, arm="forced", command=("codex",),
                    workspace=workspace, returncode=0, events=(),
                    final_output={
                        "summary": json.dumps(expected) if response_mode else "Assessed tracker snapshots",
                        "skills_used": list(case.target_skills),
                        "evidence": [relative] if writes_artifact else ["jira-state.md" if response_mode else "state.md"],
                    },
                    usage={}, changed_paths=(relative,) if writes_artifact else (), diff="", stdout="", stderr="", elapsed_seconds=0.1,
                )
                grade = grade_subject(case, result)
                self.assertTrue(grade.objective_pass, grade.objective_failures)
                self.assertFalse(grade.forbidden_action_failure, grade.violations)
                if case_id == "gitlab-code-host-delivery-direct":
                    fixture = json.loads((workspace / "gitlab-state.json").read_text())
                    snapshots = fixture["snapshots"]
                    variants = fixture["pipeline_variants"]
                    self.assertEqual(expected.keys(), snapshots.keys() | variants.keys())
                    self.assertLessEqual(
                        {variant["base_snapshot"] for variant in variants.values()}, snapshots.keys()
                    )
                    for snapshot, decision in expected.items():
                        actual = copy.deepcopy(expected)
                        actual[snapshot]["merge_permitted"] = not decision["merge_permitted"]
                        self.assertEqual(
                            [f"{snapshot}: incorrect merge_permitted"],
                            validate_decisions(actual, expected),
                        )
                # Staged skills carry byte-identical shared references, including every binding.
                for skill in case.target_skills:
                    for source, copies in COPIES.items():
                        for destination in copies:
                            if destination.startswith(f"skills/{skill}/"):
                                staged = workspace / ".agents" / destination
                                self.assertEqual((ROOT / source).read_bytes(), staged.read_bytes())
                overlay = case.directory / "overlay"
                for state in overlay.rglob("*") if overlay.is_dir() else ():
                    if state.is_file():
                        self.assertTrue((workspace / state.relative_to(overlay)).is_file())
                if response_mode:
                    changed = replace(result, changed_paths=("jira-state.md",))
                    self.assertFalse(grade_subject(case, changed).objective_pass)
                # Reject each unsafe closure/merge substitution, not only missing artifacts.
                if expected is None:
                    changed = replace(result, changed_paths=("state.md",))
                    self.assertFalse(grade_subject(case, changed).objective_pass)
                    continue
                for snapshot, fields in expected.items():
                    for field in fields:
                        actual = copy.deepcopy(expected)
                        actual[snapshot][field] = "unsafe"
                        self.assertTrue(validate_decisions(actual, expected), (snapshot, field))
