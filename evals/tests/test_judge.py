import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from evals.harness.grade import ObjectiveGrade, ValidatorResult
from evals.harness.judge import (
    JudgeConfig,
    build_judge_command,
    build_judge_packet,
    judge_covers_rubric,
    run_judge,
)
from evals.tests.test_grade import make_case, make_result


class BlindedJudgeTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for skill in (
            "compose-state-authoring",
            "compose-state-hoisting",
            "compose-side-effects",
            "compose-recomposition-performance",
            "compose-stability-diagnostics",
            "compose-state-deferred-reads",
            "compose-modifier-and-layout-style",
            "compose-slot-api-pattern",
            "compose-animations",
            "compose-focus-navigation",
            "compose-ui-testing-patterns",
            "using-chrisbanes-skills",
        ):
            (self.root / "skills" / skill).mkdir(parents=True)
        (self.root / "evals" / "schemas").mkdir(parents=True)
        (self.root / "evals" / "schemas" / "judge-output.schema.json").write_text(
            "{}\n", encoding="utf-8"
        )
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=Test", "-c", "user.email=test@localhost",
                "commit", "-qm", "baseline",
            ],
            cwd=self.root,
            check=True,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_packet_omits_arm_routing_and_deterministic_verdicts(self):
        case = make_case(self.root)
        result = make_result(
            self.root,
            events=({"type": "thread.started", "skills.config": "forced"},),
        )
        grade = ObjectiveGrade(
            objective_pass=True,
            forbidden_action_failure=False,
            objective_failures=(),
            violations=(),
            validators=(ValidatorResult(("python3", "check.py"), 0, "ok", "", False),),
        )

        packet = build_judge_packet(case, result, grade)
        rendered = json.dumps(packet, sort_keys=True)

        for secret in (
            "automatic",
            "skills_used",
            "expected_skills",
            "objective_pass",
            "forbidden_action",
            "skills.config",
        ):
            self.assertNotIn(secret, rendered)
        self.assertNotIn(case.id, packet["candidate_id"])
        self.assertEqual("done", packet["response"]["summary"])
        self.assertEqual("ok", packet["validator_evidence"][0]["stdout"])
        self.assertNotIn("check.py", rendered)

    def test_packet_contains_initial_source_for_read_only_judgment(self):
        case = make_case(self.root, task_mode="review")
        workspace = self.root / "workspace"
        workspace.mkdir()
        (workspace / "Subject.kt").write_text("val initial = true\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
        subprocess.run(["git", "add", "."], cwd=workspace, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=Test", "-c", "user.email=test@localhost",
                "commit", "-qm", "baseline",
            ],
            cwd=workspace,
            check=True,
        )
        result = make_result(workspace)
        grade = ObjectiveGrade(True, False, (), (), ())

        packet = build_judge_packet(case, result, grade)

        self.assertEqual("val initial = true\n", packet["initial_state"]["Subject.kt"])

    def test_packet_omits_evaluator_owned_project_skill_snapshot(self):
        case = make_case(self.root)
        workspace = self.root / "staged-workspace"
        skill = workspace / ".agents/skills/compose-state-authoring/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("secret skill instructions\n", encoding="utf-8")
        (workspace / "Subject.kt").write_text("val initial = true\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
        subprocess.run(["git", "add", "."], cwd=workspace, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=Test", "-c", "user.email=test@localhost",
                "commit", "-qm", "baseline",
            ],
            cwd=workspace,
            check=True,
        )

        packet = build_judge_packet(
            case, make_result(workspace), ObjectiveGrade(True, False, (), (), ())
        )

        self.assertNotIn(".agents/skills/compose-state-authoring/SKILL.md", packet["initial_state"])
        self.assertNotIn("secret skill instructions", json.dumps(packet))

    def test_judge_command_disables_every_skill_and_uses_read_only_sandbox(self):
        packet = self.root / "packet.json"
        packet.write_text("{}\n", encoding="utf-8")
        command = build_judge_command(
            packet,
            self.root,
            JudgeConfig(model="gpt-5.6-sol", reasoning="high"),
            skill_paths=tuple(
                (self.root / "skills" / skill / "SKILL.md").resolve()
                for skill in (
                    "compose-state-authoring",
                    "compose-state-hoisting",
                    "compose-side-effects",
                    "compose-recomposition-performance",
                    "compose-stability-diagnostics",
                    "compose-state-deferred-reads",
                    "compose-modifier-and-layout-style",
                    "compose-slot-api-pattern",
                    "compose-animations",
                    "compose-focus-navigation",
                    "compose-ui-testing-patterns",
                    "using-chrisbanes-skills",
                )
            ),
        )
        rendered = " ".join(command)

        self.assertEqual(12, rendered.count("path = "))
        self.assertEqual(0, rendered.count("enabled = true"))
        self.assertEqual("read-only", command[command.index("--sandbox") + 1])
        self.assertNotIn("--approve-for-me", command)
        self.assertIn('model_reasoning_effort="high"', rendered)

    def test_judge_captures_events_and_usage(self):
        packet = self.root / "packet.json"
        packet.write_text("{}\n", encoding="utf-8")
        fake = self.root / "fake-codex"
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"criteria\\\":[],\\\"overall_pass\\\":true,\\\"rationale\\\":\\\"ok\\\"}\"}}'\n"
            "printf '%s\\n' '{\"type\":\"turn.completed\",\"usage\":{\"input_tokens\":7,\"output_tokens\":3}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)

        result = run_judge(
            packet,
            self.root,
            JudgeConfig(model="gpt-5.6-sol", reasoning="high"),
            codex_executable=str(fake),
            skill_paths=(),
        )

        self.assertEqual(2, len(result.events))
        self.assertEqual({"input_tokens": 7, "output_tokens": 3}, result.usage)

    def test_judgment_must_cover_each_rubric_id_exactly_once(self):
        rubric = ({"id": "correct", "text": "Correct"},)
        base = {"overall_pass": True, "rationale": "ok"}

        self.assertFalse(judge_covers_rubric({**base, "criteria": []}, rubric))
        self.assertFalse(
            judge_covers_rubric(
                {
                    **base,
                    "criteria": [
                        {"id": "wrong", "pass": True, "evidence": "none"}
                    ],
                },
                rubric,
            )
        )
        self.assertTrue(
            judge_covers_rubric(
                {
                    **base,
                    "criteria": [
                        {"id": "correct", "pass": True, "evidence": "diff"}
                    ],
                },
                rubric,
            )
        )
        self.assertFalse(
            judge_covers_rubric(
                {
                    **base,
                    "extra": "not in schema",
                    "criteria": [
                        {"id": "correct", "pass": True, "evidence": "diff"}
                    ],
                },
                rubric,
            )
        )


if __name__ == "__main__":
    unittest.main()
