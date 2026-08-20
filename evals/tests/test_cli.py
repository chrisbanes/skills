import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.run import main


MODEL_ARGS = [
    "--model",
    "gpt-5.6-terra",
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

    def invoke_with_error(self, *args):
        output = io.StringIO()
        error = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = main(list(args))
        return status, output.getvalue(), error.getvalue()

    def test_full_plan_expands_38_cases_three_arms_and_three_repetitions(self):
        status, output = self.invoke("plan", *MODEL_ARGS, "--repetitions", "3", "--json")

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertEqual(38, plan["case_count"])
        self.assertEqual(342, plan["subject_calls"])
        self.assertEqual(342, plan["judge_calls"])
        self.assertEqual(684, plan["total_calls"])

    def test_kotlin_gradle_plan_uses_its_own_19_case_suite(self):
        status, output = self.invoke(
            "plan",
            *MODEL_ARGS,
            "--suite",
            "kotlin-gradle",
            "--repetitions",
            "3",
            "--json",
        )

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertEqual(19, plan["case_count"])
        self.assertEqual(171, plan["subject_calls"])
        self.assertEqual(171, plan["judge_calls"])
        self.assertEqual(342, plan["total_calls"])

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

    def test_cost_preview_uses_explicit_per_call_assumptions(self):
        status, output = self.invoke(
            "plan",
            *MODEL_ARGS,
            "--case",
            "compose-state-authoring-direct",
            "--repetitions",
            "1",
            "--subject-cost-per-call-usd",
            "0.10",
            "--judge-cost-per-call-usd",
            "0.04",
            "--json",
        )

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertAlmostEqual(0.42, plan["estimated_cost_usd"])

    def test_live_run_requires_explicit_cost_assumptions(self):
        status, _ = self.invoke(
            "run",
            *MODEL_ARGS,
            "--case",
            "compose-state-authoring-direct",
            "--execute",
        )

        self.assertEqual(2, status)

    def test_model_and_reasoning_are_explicit_required_inputs(self):
        with self.assertRaises(SystemExit):
            main(["plan"])

    def test_report_and_regrade_reject_incomparable_raw_results_cleanly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            controls = {
                "suite": "compose",
                "codex_version": "codex-cli 1",
                "skill_sha": "skill-sha",
                "skill_catalog_digest": "catalog-sha",
                "subject_model": {"model": "gpt-5.6-terra", "reasoning": "medium"},
                "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
            }
            for case, model in (("first", "gpt-5.6-terra"), ("second", "gpt-5.6-sol")):
                path = output_dir / "raw" / case / "automatic" / "1.json"
                path.parent.mkdir(parents=True)
                payload = {
                    **controls,
                    "id": f"{case}:automatic:1",
                    "subject_model": {"model": model, "reasoning": "medium"},
                }
                path.write_text(json.dumps({"payload": payload}), encoding="utf-8")

            for command in ("report", "regrade"):
                with self.subTest(command=command):
                    status, output, error = self.invoke_with_error(
                        command, "--output-dir", temp_dir
                    )
                    self.assertEqual(1, status)
                    self.assertEqual("", output)
                    self.assertIn("different run controls: subject_model", error)

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

    def test_subject_schema_uses_supported_structured_output_keywords(self):
        root = Path(__file__).resolve().parents[2]
        schema = json.loads(
            (root / "evals" / "schemas" / "subject-output.schema.json").read_text()
        )

        self.assertNotIn("uniqueItems", schema["properties"]["skills_used"])

    def test_judge_defaults_to_a_no_call_packet_preview(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packets = Path(temp_dir) / "judge-packets"
            packets.mkdir()
            (packets / "one.json").write_text("{}\n", encoding="utf-8")
            status, output = self.invoke(
                "judge",
                "--output-dir",
                temp_dir,
                "--judge-model",
                "gpt-5.6-sol",
                "--judge-reasoning",
                "high",
                "--json",
            )

        self.assertEqual(0, status)
        self.assertEqual(1, json.loads(output)["judge_calls"])
        self.assertFalse(json.loads(output)["execute"])


if __name__ == "__main__":
    unittest.main()
