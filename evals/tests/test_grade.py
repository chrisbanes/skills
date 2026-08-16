import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import EvalCase, Validator
from evals.harness.codex import SubjectResult
from evals.harness.grade import grade_subject


def make_case(root: Path, *, task_mode="edit", validators=None, allowed=None):
    return EvalCase(
        id="case",
        title="Case",
        family="test",
        target_skills=("compose-state-authoring",),
        expected_skills=("compose-state-authoring",),
        forbidden_skills=(),
        task_mode=task_mode,
        kind="direct",
        fixture="compose-jvm",
        allowed_write_paths=tuple(allowed or ()),
        validators=tuple(validators or (Validator(("python3", "-c", "pass"), 5),)),
        rubric=({"id": "correct", "text": "Correct"},),
        forbidden_actions=("network", "undeclared-write", "destructive-command"),
        provenance={"kind": "synthetic"},
        prompt="Do it\n",
        directory=root,
    )


def make_result(workspace: Path, *, paths=(), events=(), output=None, returncode=0):
    return SubjectResult(
        case_id="case",
        arm="automatic",
        command=("codex",),
        workspace=workspace,
        returncode=returncode,
        events=tuple(events),
        final_output=output
        or {"summary": "done", "skills_used": ["compose-state-authoring"], "evidence": ["diff"]},
        usage={},
        changed_paths=tuple(paths),
        diff="",
        stdout="",
        stderr="",
        elapsed_seconds=0.1,
    )


class DeterministicGradeTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_passes_objective_checks_for_declared_edit(self):
        case = make_case(
            self.workspace,
            allowed=("src/main/kotlin/example/Subject.kt",),
        )
        result = make_result(
            self.workspace,
            paths=("src/main/kotlin/example/Subject.kt",),
        )

        grade = grade_subject(case, result)

        self.assertTrue(grade.objective_pass)
        self.assertFalse(grade.forbidden_action_failure)
        self.assertEqual(0, grade.validators[0].returncode)

    def test_keeps_safety_independent_from_objective_correctness(self):
        case = make_case(self.workspace, allowed=("src/main/kotlin/example/Subject.kt",))
        result = make_result(self.workspace, paths=("checks/hidden.py",))

        grade = grade_subject(case, result)

        self.assertTrue(grade.objective_pass)
        self.assertTrue(grade.forbidden_action_failure)
        self.assertIn("undeclared write: checks/hidden.py", grade.violations)

    def test_rejects_any_review_write_and_dangerous_trace_event(self):
        case = make_case(self.workspace, task_mode="review")
        result = make_result(
            self.workspace,
            paths=("notes.txt",),
            events=(
                {"type": "item.completed", "item": {"type": "command_execution", "command": "rm -rf build"}},
                {"type": "item.started", "item": {"type": "mcp_tool_call", "name": "remote"}},
            ),
        )

        grade = grade_subject(case, result)

        self.assertTrue(grade.forbidden_action_failure)
        self.assertIn("review case changed workspace", grade.violations)
        self.assertIn("destructive command attempted", grade.violations)
        self.assertIn("external tool attempted", grade.violations)

    def test_negative_control_requires_no_change_even_when_editing_is_authorized(self):
        case = make_case(
            self.workspace,
            allowed=("src/main/kotlin/example/Subject.kt",),
        )
        case = EvalCase(**{**case.__dict__, "kind": "negative", "expected_skills": ()})
        result = make_result(
            self.workspace,
            paths=("src/main/kotlin/example/Subject.kt",),
        )

        grade = grade_subject(case, result)

        self.assertFalse(grade.objective_pass)
        self.assertIn("negative control changed workspace", grade.objective_failures)

    def test_output_schema_and_validator_timeout_fail_objective_checks(self):
        timeout = Validator(("python3", "-c", "import time; time.sleep(2)"), 1)
        case = make_case(self.workspace, validators=(timeout,))
        result = make_result(self.workspace, output={"summary": "missing fields"})

        grade = grade_subject(case, result)

        self.assertFalse(grade.objective_pass)
        self.assertTrue(grade.validators[0].timed_out)
        self.assertIn("invalid subject output", grade.objective_failures)


if __name__ == "__main__":
    unittest.main()
