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


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "deliver-spec-provider-closure-direct",
    "deliver-spec-provider-closure-novel",
    "deliver-spec-provider-closure-negative",
    "jira-board-scope-direct",
    "jira-direct-closure-novel",
    "jira-transition-marker-negative",
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
                filename = "jira-binding.md" if case_id.startswith("jira-") else "github-binding.md"
                binding = workspace / ".agents/skills" / case.target_skills[0] / "references" / filename
                self.assertEqual((ROOT / "references" / filename).read_bytes(), binding.read_bytes())
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
