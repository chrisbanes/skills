import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL, EvalCase, Validator
from evals.harness.codex import RunConfig, build_subject_command, prepare_workspace, run_subject


def sample_case(root: Path, *, task_mode: str = "edit") -> EvalCase:
    case_dir = root / "evals" / "cases" / "sample"
    case_dir.mkdir(parents=True, exist_ok=True)
    overlay = case_dir / "overlay" / "src" / "main" / "kotlin" / "example"
    overlay.mkdir(parents=True, exist_ok=True)
    (overlay / "Subject.kt").write_text("package example\n", encoding="utf-8")
    return EvalCase(
        id="sample",
        title="Sample",
        family="state-effects",
        target_skills=("compose-state-authoring",),
        expected_skills=("compose-state-authoring",),
        forbidden_skills=(),
        task_mode=task_mode,
        kind="direct",
        fixture="compose-jvm",
        allowed_write_paths=("src/main/kotlin/example/Subject.kt",) if task_mode == "edit" else (),
        validators=(Validator(("python3", "checks/check.py"), 30),),
        rubric=({"id": "correct", "text": "The result is correct"},),
        forbidden_actions=("network", "undeclared-write"),
        provenance={"kind": "synthetic"},
        prompt="Improve the subject without mentioning a skill.\n",
        directory=case_dir,
    )


class CodexRunnerTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        fixture = self.root / "evals" / "fixtures" / "compose-jvm"
        (fixture / "src" / "main" / "kotlin" / "example").mkdir(parents=True)
        (fixture / "src" / "main" / "kotlin" / "example" / "Base.kt").write_text(
            "package example\n", encoding="utf-8"
        )
        for skill in (*COMPOSE_SKILLS, ROUTER_SKILL):
            skill_dir = self.root / "skills" / skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"---\nname: {skill}\n---\n", encoding="utf-8")
        schemas = self.root / "evals" / "schemas"
        schemas.mkdir(parents=True)
        (schemas / "subject-output.schema.json").write_text("{}\n", encoding="utf-8")
        self.config = RunConfig(model="gpt-5.6-sol", reasoning="medium")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_builds_three_explicit_and_isolated_skill_arms(self):
        case = sample_case(self.root)
        workspace = self.root / "workspace"

        none = build_subject_command(case, "none", self.root, workspace, self.config)
        forced = build_subject_command(case, "forced", self.root, workspace, self.config)
        automatic = build_subject_command(case, "automatic", self.root, workspace, self.config)

        for command in (none, forced, automatic):
            rendered = " ".join(command)
            self.assertIn("--ephemeral", command)
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ignore-rules", command)
            self.assertIn("--strict-config", command)
            self.assertIn("--json", command)
            self.assertIn('model_reasoning_effort="medium"', rendered)
            self.assertIn("sandbox_workspace_write.network_access=false", rendered)
            self.assertEqual(12, rendered.count("path = "))
        self.assertEqual(0, " ".join(none).count("enabled = true"))
        self.assertEqual(1, " ".join(forced).count("enabled = true"))
        self.assertEqual(12, " ".join(automatic).count("enabled = true"))
        self.assertIn("$compose-state-authoring", forced[-1])
        self.assertNotIn("$compose-state-authoring", automatic[-1])
        self.assertEqual(case.prompt, automatic[-1])

    def test_selects_read_only_or_workspace_write_from_the_case_contract(self):
        workspace = self.root / "workspace"
        edit = build_subject_command(sample_case(self.root), "none", self.root, workspace, self.config)
        review = build_subject_command(
            sample_case(self.root, task_mode="review"), "none", self.root, workspace, self.config
        )

        self.assertEqual("workspace-write", edit[edit.index("--sandbox") + 1])
        self.assertIn("--approve-for-me", edit)
        self.assertEqual("read-only", review[review.index("--sandbox") + 1])
        self.assertNotIn("--approve-for-me", review)

    def test_forced_negative_control_invokes_target_without_claiming_expected_routing(self):
        case = replace(sample_case(self.root), kind="negative", expected_skills=())

        command = build_subject_command(
            case, "forced", self.root, self.root / "workspace", self.config
        )

        self.assertEqual(1, " ".join(command).count("enabled = true"))
        self.assertIn("$compose-state-authoring", command[-1])

    def test_prepares_independent_fixture_and_overlay_copies(self):
        case = sample_case(self.root)
        first = prepare_workspace(case, self.root, self.root / "runs" / "first")
        second = prepare_workspace(case, self.root, self.root / "runs" / "second")

        subject = first / "src" / "main" / "kotlin" / "example" / "Subject.kt"
        subject.write_text("changed\n", encoding="utf-8")

        self.assertTrue((first / ".git").is_dir())
        self.assertEqual("package example\n", (second / subject.relative_to(first)).read_text())

    def test_captures_jsonl_final_output_and_workspace_diff(self):
        case = sample_case(self.root)
        fake = self.root / "fake-codex"
        fake.write_text(
            "#!/bin/sh\n"
            "workspace=''\n"
            "previous=''\n"
            "for arg in \"$@\"; do\n"
            "  if [ \"$previous\" = '-C' ]; then workspace=$arg; fi\n"
            "  previous=$arg\n"
            "done\n"
            "printf '// changed\\n' >> \"$workspace/src/main/kotlin/example/Subject.kt\"\n"
            "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"summary\\\":\\\"done\\\",\\\"skills_used\\\":[\\\"compose-state-authoring\\\"],\\\"evidence\\\":[\\\"diff\\\"]}\"}}'\n"
            "printf '%s\\n' '{\"type\":\"turn.completed\",\"usage\":{\"input_tokens\":10,\"output_tokens\":5}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)

        result = run_subject(
            case,
            "forced",
            self.root,
            self.root / "runs" / "subject",
            self.config,
            codex_executable=str(fake),
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("done", result.final_output["summary"])
        self.assertEqual({"input_tokens": 10, "output_tokens": 5}, result.usage)
        self.assertEqual(("src/main/kotlin/example/Subject.kt",), result.changed_paths)
        self.assertIn("// changed", result.diff)

    def test_captures_untracked_files_in_workspace_diff(self):
        case = sample_case(self.root)
        fake = self.root / "fake-codex-untracked"
        fake.write_text(
            "#!/bin/sh\n"
            "workspace=''\n"
            "previous=''\n"
            "for arg in \"$@\"; do\n"
            "  if [ \"$previous\" = '-C' ]; then workspace=$arg; fi\n"
            "  previous=$arg\n"
            "done\n"
            "printf 'new evidence\\n' > \"$workspace/notes.txt\"\n"
            "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"summary\\\":\\\"done\\\",\\\"skills_used\\\":[],\\\"evidence\\\":[]}\"}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)

        result = run_subject(
            case,
            "none",
            self.root,
            self.root / "runs" / "untracked",
            self.config,
            codex_executable=str(fake),
        )

        self.assertEqual(("notes.txt",), result.changed_paths)
        self.assertIn("+++ b/notes.txt", result.diff)
        self.assertIn("+new evidence", result.diff)


if __name__ == "__main__":
    unittest.main()
