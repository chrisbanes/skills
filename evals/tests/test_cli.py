import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.run import build_parser, main


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

    def test_kotlin_gradle_plan_uses_its_own_22_case_suite(self):
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
        self.assertEqual(22, plan["case_count"])
        self.assertEqual(198, plan["subject_calls"])
        self.assertEqual(198, plan["judge_calls"])
        self.assertEqual(396, plan["total_calls"])

    def test_workflows_plan_skips_explicit_only_automatic_conditions(self):
        status, output = self.invoke(
            "plan",
            *MODEL_ARGS,
            "--suite",
            "workflows-writing",
            "--repetitions",
            "3",
            "--json",
        )

        plan = json.loads(output)
        self.assertEqual(0, status)
        self.assertEqual(38, plan["case_count"])
        self.assertEqual(88, plan["condition_count"])
        self.assertEqual(264, plan["subject_calls"])
        self.assertEqual(264, plan["judge_calls"])
        self.assertEqual(528, plan["total_calls"])

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

    def test_runtimes_default_to_codex(self):
        parser = build_parser()
        run = parser.parse_args(["run", *MODEL_ARGS])
        judge = parser.parse_args(
            ["judge", "--output-dir", "x", "--judge-model", "m", "--judge-reasoning", "r"]
        )

        self.assertEqual(("codex", "codex"), (run.runtime, run.judge_runtime))
        self.assertEqual(("codex", "claude"), (run.codex_executable, run.claude_executable))
        self.assertEqual("codex", judge.judge_runtime)
        self.assertEqual("claude", judge.claude_executable)
        self.assertEqual("codex", parser.parse_args(["plan", *MODEL_ARGS]).runtime)

    def test_claude_runtime_validates_reasoning_effort(self):
        claude_args = ["--runtime", "claude", "--model", "claude-haiku-5-5",
                       "--judge-model", "gpt-6-sol", "--judge-reasoning", "high"]
        status, output = self.invoke(
            "run", *claude_args, "--reasoning", "xhigh",
            "--case", "compose-state-authoring-direct", "--repetitions", "1", "--json",
        )
        self.assertEqual(0, status)
        self.assertFalse(json.loads(output)["execute"])

        for command in ("plan", "run"):
            with self.subTest(command), self.assertRaises(SystemExit) as raised:
                with contextlib.redirect_stderr(io.StringIO()) as error:
                    main([command, *claude_args, "--reasoning", "minimal"])
            self.assertEqual(2, raised.exception.code)
            self.assertIn("claude effort must be one of", error.getvalue())

    def test_claude_judge_validates_reasoning_and_requires_an_explicit_model(self):
        subject = ["--model", "gpt-6-luna", "--reasoning", "high"]
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()) as error:
                main(["plan", *subject, "--judge-runtime", "claude", "--judge-reasoning", "high"])
        self.assertIn("--judge-model", error.getvalue())

        for command in (["plan", *subject], ["judge", "--output-dir", "x"]):
            with self.subTest(command[0]), self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()) as error:
                    main([*command, "--judge-runtime", "claude",
                          "--judge-model", "claude-haiku-5-5", "--judge-reasoning", "minimal"])
            self.assertIn("claude effort must be one of", error.getvalue())

    def test_plan_counts_do_not_depend_on_the_runtime(self):
        args = ["--case", "compose-state-authoring-direct", "--repetitions", "2", "--json"]
        _, codex = self.invoke("plan", *MODEL_ARGS, *args)
        _, claude = self.invoke(
            "plan", *MODEL_ARGS, "--runtime", "claude", "--judge-runtime", "claude", *args
        )

        for key in ("condition_count", "subject_calls", "judge_calls", "total_calls"):
            self.assertEqual(json.loads(codex)[key], json.loads(claude)[key])

    def test_run_passes_runtimes_and_executables_to_the_experiment(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "evals.run.execute_experiment", return_value={"results": "r", "scorecard": "s"}
        ) as execute:
            status, _ = self.invoke(
                "run", "--runtime", "claude", "--judge-runtime", "codex",
                "--model", "claude-haiku-5-5", "--reasoning", "high",
                "--judge-model", "gpt-6-sol", "--judge-reasoning", "high",
                "--claude-executable", "my-claude", "--codex-executable", "my-codex",
                "--case", "compose-state-authoring-direct", "--repetitions", "1",
                "--subject-cost-per-call-usd", "0.1", "--judge-cost-per-call-usd", "0.1",
                "--output-dir", temp_dir, "--execute",
            )

        self.assertEqual(0, status)
        kwargs = execute.call_args.kwargs
        self.assertEqual(("claude", "codex"), (kwargs["runtime"], kwargs["judge_runtime"]))
        self.assertEqual(("my-codex", "my-claude"),
                         (kwargs["codex_executable"], kwargs["claude_executable"]))

    def test_claude_run_refuses_an_output_directory_inside_the_repository(self):
        with patch("evals.run.execute_experiment") as execute:
            status, _, error = self.invoke_with_error(
                "run", "--runtime", "claude",
                "--model", "claude-haiku-5-5", "--reasoning", "high",
                "--judge-model", "gpt-6-sol", "--judge-reasoning", "high",
                "--case", "compose-state-authoring-direct", "--repetitions", "1",
                "--subject-cost-per-call-usd", "0.1", "--judge-cost-per-call-usd", "0.1",
                "--execute",
            )

        self.assertEqual(2, status)
        self.assertIn("--output-dir", error)
        execute.assert_not_called()

    def test_judge_passes_the_judge_runtime_to_rejudging(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir) / "raw" / "case" / "automatic" / "1.json"
            raw.parent.mkdir(parents=True)
            raw.write_text(json.dumps({"payload": {
                "id": "case:automatic:1", "case_id": "compose-state-authoring-direct",
                "arm": "automatic", "suite": "compose", "codex_version": "codex-cli 1",
                "skill_sha": "s", "skill_catalog_digest": "c",
                "subject_model": {"model": "m", "reasoning": "r"},
                "judge_model": {"model": "j", "reasoning": "r"},
                "subject": {"final_output": {"skills_used": []}},
            }}), encoding="utf-8")
            with patch("evals.run.rejudge_packets", return_value={
                "packet_count": 0, "judge_calls": 0
            }) as rejudge:
                status, _ = self.invoke(
                    "judge", "--output-dir", temp_dir, "--judge-runtime", "claude",
                    "--judge-model", "claude-haiku-5-5", "--judge-reasoning", "high",
                    "--claude-executable", "my-claude",
                )

        self.assertEqual(0, status)
        self.assertEqual("claude", rejudge.call_args.kwargs["judge_runtime"])
        self.assertEqual("my-claude", rejudge.call_args.kwargs["claude_executable"])

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
            output_dir = Path(temp_dir)
            included_fingerprint = "a" * 64
            excluded_fingerprint = "b" * 64
            packets = output_dir / "judge-packets"
            packets.mkdir()
            (packets / f"candidate-{included_fingerprint[:20]}-1.json").write_text(
                "{}\n", encoding="utf-8"
            )
            (packets / f"candidate-{excluded_fingerprint[:20]}-1.json").write_text(
                "{}\n", encoding="utf-8"
            )

            def write_raw(case_id, fingerprint):
                raw = output_dir / "raw" / case_id / "automatic" / "1.json"
                raw.parent.mkdir(parents=True)
                raw.write_text(
                    json.dumps(
                        {
                            "payload": {
                                "id": f"{case_id}:automatic:1",
                                "case_id": case_id,
                                "arm": "automatic",
                                "repetition": 1,
                                "fingerprint": fingerprint,
                                "suite": "compose",
                                "codex_version": "codex-cli 1",
                                "skill_sha": "skill-sha",
                                "skill_catalog_digest": "catalog-sha",
                                "subject_model": {
                                    "model": "gpt-5.6-terra",
                                    "reasoning": "medium",
                                },
                                "judge_model": {
                                    "model": "gpt-5.6-sol",
                                    "reasoning": "high",
                                },
                                "subject": {"final_output": {"skills_used": []}},
                            }
                        }
                    ),
                    encoding="utf-8",
                )

            write_raw("compose-state-authoring-direct", included_fingerprint)
            write_raw("implement-with-subagents-direct", excluded_fingerprint)
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
        self.assertEqual(1, json.loads(output)["skipped_packet_count"])
        self.assertFalse(json.loads(output)["execute"])


if __name__ == "__main__":
    unittest.main()
