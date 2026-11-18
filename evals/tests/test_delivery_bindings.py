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
    "gitlab-code-host-delivery-direct",
    "gitlab-code-host-config-novel",
    "gitlab-code-host-closure-negative",
    "shepherd-gitlab-discussions-novel",
)


RESPONSE_CASES = {
    "jira-transition-marker-negative": "jira-state.md",
    "gitlab-tracker-claim-direct": "gitlab-state.json",
    "gitlab-tracker-notes-novel": "gitlab-state.json",
    "gitlab-tracker-closure-negative": "gitlab-state.json",
}


class DeliveryBindingsTest(unittest.TestCase):
    def test_closure_decisions_use_the_existing_offline_grader(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in (*CASES, *RESPONSE_CASES):
            case = corpus[case_id]
            expected = json.loads((case.directory / "expectations.json").read_text()).get("decisions")
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(
                    case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills,
                )
                overlay = case.directory / "overlay"
                state = RESPONSE_CASES.get(case_id, "state.md")
                relative = ".scratch/review-decisions.json"
                artifact = workspace / relative
                response_mode = case_id in RESPONSE_CASES
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
                        "evidence": [relative] if writes_artifact else [state],
                    },
                    usage={}, changed_paths=(relative,) if writes_artifact else (), diff="", stdout="", stderr="", elapsed_seconds=0.1,
                )
                grade = grade_subject(case, result)
                self.assertTrue(grade.objective_pass, grade.objective_failures)
                self.assertFalse(grade.forbidden_action_failure, grade.violations)
                # Staged skills carry byte-identical shared references, including every binding.
                for skill in case.target_skills:
                    for source, copies in COPIES.items():
                        for destination in copies:
                            if destination.startswith(f"skills/{skill}/"):
                                staged = workspace / ".agents" / destination
                                self.assertEqual((ROOT / source).read_bytes(), staged.read_bytes())
                for source in overlay.rglob("*") if overlay.is_dir() else ():
                    if source.is_file():
                        self.assertTrue((workspace / source.relative_to(overlay)).is_file())
                if response_mode:
                    changed = replace(result, changed_paths=(state,))
                    self.assertTrue(grade_subject(case, changed).forbidden_action_failure)
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
