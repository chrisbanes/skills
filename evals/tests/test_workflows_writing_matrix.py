import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.codex import (
    RunConfig,
    automatically_invokable_public_skills,
    build_subject_command,
    prepare_workspace,
)
from evals.harness.experiment import filter_cases
from evals.harness.suites import PUBLIC_SKILLS, WORKFLOWS_WRITING_SKILLS


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkflowsWritingMatrixTest(unittest.TestCase):
    def test_has_exact_skill_triads_without_routing_or_to_plan(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        self.assertEqual(12, report.case_count)
        self.assertIn("grounded-writing", PUBLIC_SKILLS)
        self.assertNotIn("implement", PUBLIC_SKILLS)
        self.assertEqual(12, len(filter_cases(report.cases, case_ids=None, skills=None)))
        self.assertFalse(any(case.kind == "routing" for case in report.cases))
        self.assertFalse(any(case.calibration for case in report.cases))
        self.assertFalse(any("to-plan" in case.target_skills for case in report.cases))
        for skill in WORKFLOWS_WRITING_SKILLS:
            kinds = {case.kind for case in report.cases if skill in case.target_skills}
            with self.subTest(skill=skill):
                self.assertEqual({"direct", "novel", "negative"}, kinds)

        subagent_cases = [
            case for case in report.cases if case.fixture == "workflow-subagents"
        ]
        self.assertEqual(3, len(subagent_cases))
        self.assertTrue(
            all(
                case.target_skills == ("implement-with-subagents",)
                and case.constant_skills == ("implement",)
                for case in subagent_cases
            )
        )
        self.assertTrue(
            all(
                not case.constant_skills
                for case in report.cases
                if case.fixture == "workflow"
            )
        )

    def test_workflow_fixture_supplies_the_implement_dependency_in_every_arm(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "implement-with-subagents-direct"
        )
        config = RunConfig(model="gpt-5.6-terra", reasoning="medium")

        for arm in ("none", "forced", "automatic"):
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as temp_dir:
                workspace = Path(temp_dir) / "workspace"
                command = build_subject_command(
                    case, arm, REPO_ROOT, workspace, config, skill_paths=()
                )
                rendered = " ".join(command)
                self.assertIn(
                    str(workspace / ".agents/skills/implement/SKILL.md"), rendered
                )
                self.assertIn("enabled = true", rendered)
                self.assertIn(
                    "Evaluator-owned fixture dependencies to omit: implement",
                    rendered,
                )
                self.assertIn(
                    "Enabled public skills are not fixture dependencies", rendered
                )

                prepare_workspace(
                    case,
                    REPO_ROOT,
                    workspace,
                    enabled_skills=automatically_invokable_public_skills(REPO_ROOT),
                )
                self.assertTrue(
                    (workspace / ".agents/skills/implement/SKILL.md").is_file()
                )
                if arm == "automatic":
                    self.assertNotIn(
                        str(
                            workspace
                            / ".agents"
                            / "skills"
                            / "implement-with-subagents"
                            / "SKILL.md"
                        ),
                        rendered,
                    )
                    self.assertFalse(
                        (
                            workspace
                            / ".agents"
                            / "skills"
                            / "implement-with-subagents"
                        ).exists()
                    )

    def test_advanced_workflow_skills_require_explicit_invocation(self):
        explicit_only = (
            "implement-with-subagents",
            "run-github-project",
            "shepherd",
            "to-plan",
        )
        for skill in explicit_only:
            config = REPO_ROOT / "skills" / skill / "agents" / "openai.yaml"
            entrypoint = REPO_ROOT / "skills" / skill / "SKILL.md"
            with self.subTest(skill=skill):
                self.assertIn(
                    "allow_implicit_invocation: false",
                    config.read_text(encoding="utf-8"),
                )
                self.assertIn(
                    "disable-model-invocation: true",
                    entrypoint.read_text(encoding="utf-8"),
                )

        self.assertEqual(
            set(PUBLIC_SKILLS) - set(explicit_only),
            set(automatically_invokable_public_skills(REPO_ROOT)),
        )
        schema = json.loads((REPO_ROOT / "skills.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            "boolean",
            schema["properties"]["disable-model-invocation"]["type"],
        )

    def test_behavioral_expectations_do_not_assert_fixture_prose(self):
        expectations = json.loads(
            (
                REPO_ROOT
                / "evals/cases/implement-with-subagents-novel/expectations.json"
            ).read_text(encoding="utf-8")
        )

        self.assertNotIn(
            "minimal `implement` dependency", expectations.get("must_contain", [])
        )

    def test_workflow_prompts_do_not_disclose_the_target_skill(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)

    def test_review_prompts_allow_skill_instruction_reads(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        for case in report.cases:
            with self.subTest(case=case.id):
                self.assertNotIn("do not run agents, commands", case.prompt.lower())

    def test_grounded_writing_validator_accepts_qualified_every_project_language(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "draft.md").write_text(
                "Imports avoid a duplicate parse. In the release benchmark, p95 "
                "fell from 1.8 seconds to 1.1 seconds. Production evidence is still "
                "needed before claiming the same improvement for every project.\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                ["python3", str(validator), "grounded-writing-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)


if __name__ == "__main__":
    unittest.main()
