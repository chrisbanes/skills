import contextlib
import io
import json
import unittest
from pathlib import Path

from evals.run import main


MODEL_ARGS = [
    "--model",
    "gpt-5.6-sol",
    "--reasoning",
    "medium",
    "--judge-model",
    "gpt-5.6-sol",
    "--judge-reasoning",
    "high",
]


class EvaluationCliTest(unittest.TestCase):
    def invoke(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(list(args))
        return status, output.getvalue()

    def test_full_plan_expands_38_cases_three_arms_and_three_repetitions(self):
        status, output = self.invoke("plan", *MODEL_ARGS, "--repetitions", "3", "--json")

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertEqual(38, plan["case_count"])
        self.assertEqual(342, plan["subject_calls"])
        self.assertEqual(342, plan["judge_calls"])
        self.assertEqual(684, plan["total_calls"])

    def test_filters_case_skill_and_arm_before_counting_calls(self):
        status, output = self.invoke(
            "plan",
            *MODEL_ARGS,
            "--case",
            "compose-state-authoring-direct",
            "--arm",
            "automatic",
            "--repetitions",
            "1",
            "--json",
        )

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertEqual(1, plan["case_count"])
        self.assertEqual(["automatic"], plan["arms"])
        self.assertEqual(2, plan["total_calls"])

    def test_run_without_execute_is_a_no_call_preview(self):
        status, output = self.invoke(
            "run",
            *MODEL_ARGS,
            "--case",
            "compose-state-authoring-direct",
            "--repetitions",
            "1",
            "--json",
        )

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertFalse(plan["execute"])
        self.assertIn("Pass --execute", plan["notice"])

    def test_model_and_reasoning_are_explicit_required_inputs(self):
        with self.assertRaises(SystemExit):
            main(["plan"])

    def test_repository_commands_validate_harness_without_live_model_calls(self):
        root = Path(__file__).resolve().parents[2]
        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
        workflow = (root / ".github" / "workflows" / "lint.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("evals:validate", package["scripts"])
        self.assertIn("test", package["scripts"])
        self.assertIn("npm test", workflow)
        self.assertIn("npm run evals:validate", workflow)
        self.assertNotIn("--execute", workflow)


if __name__ == "__main__":
    unittest.main()
