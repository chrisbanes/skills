import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.harness.cases import validate_corpus
from evals.harness.codex import (
    RunConfig,
    automatically_invokable_public_skills,
    build_subject_command,
    prepare_workspace,
)
from evals.harness.experiment import (
    evaluation_conditions,
    execute_experiment,
    filter_cases,
    reconcile_automatic_eligibility,
)
from evals.harness.judge import JudgeConfig
from evals.harness.suites import PUBLIC_SKILLS, WORKFLOWS_WRITING_SKILLS


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkflowsWritingMatrixTest(unittest.TestCase):
    def test_has_skill_triads_and_workflow_calibration_coverage_without_routing(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        benchmark = [case for case in report.cases if not case.calibration]
        calibration = [case for case in report.cases if case.calibration]
        self.assertEqual(15, len(benchmark))
        self.assertEqual(12, len(calibration))
        self.assertIn("grounded-writing", PUBLIC_SKILLS)
        self.assertNotIn("implement", PUBLIC_SKILLS)
        self.assertEqual(15, len(filter_cases(report.cases, case_ids=None, skills=None)))
        self.assertFalse(any(case.kind == "routing" for case in report.cases))
        self.assertEqual(
            {
                "implement-with-subagents-missing-provider-challenge",
                "run-github-project-missing-provider-challenge",
                "to-plan-authorized-draft-direct",
                "to-plan-prior-confirmed-novel",
                "to-plan-unresolved-choice-negative",
                "to-plan-discussion-only-negative",
                "implement-with-subagents-reuse-direct",
                "implement-with-subagents-stale-evidence-negative",
                "implement-with-subagents-missing-output-negative",
                "implement-with-subagents-post-edit-negative",
                "implement-with-subagents-failed-verification-negative",
                "implement-with-subagents-explicit-rerun-novel",
            },
            {case.id for case in calibration},
        )
        for skill in WORKFLOWS_WRITING_SKILLS:
            kinds = {case.kind for case in benchmark if skill in case.target_skills}
            with self.subTest(skill=skill):
                self.assertEqual({"direct", "novel", "negative"}, kinds)

        self.assertEqual(
            {
                "to-plan-direct",
                "to-plan-novel",
                "to-plan-negative",
            },
            {
                case.id
                for case in benchmark
                if case.target_skills == ("to-plan",)
            },
        )

        subagent_cases = [
            case for case in benchmark if case.fixture == "workflow-subagents"
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

    def test_missing_provider_challenge_omits_the_implement_dependency(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "implement-with-subagents-missing-provider-challenge"
        )

        self.assertEqual((), case.constant_skills)
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            prepare_workspace(case, REPO_ROOT, workspace, enabled_skills=())

            self.assertFalse(
                (workspace / ".agents/skills/implement/SKILL.md").exists()
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
        self.assertNotIn("paths", schema["properties"])

    def test_automatic_conditions_exclude_explicit_only_workflow_skills(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        conditions = evaluation_conditions(REPO_ROOT, report.cases, ("automatic",))

        self.assertEqual(
            {
                "grounded-writing-direct",
                "grounded-writing-novel",
                "grounded-writing-negative",
            },
            {case.id for case, _ in conditions},
        )

    def test_execution_skips_an_explicit_only_automatic_condition(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case for case in report.cases if case.id == "run-github-project-direct"
        )

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "evals.harness.experiment.preflight"
        ) as preflight:
            paths = execute_experiment(
                REPO_ROOT,
                [case],
                arms=["automatic"],
                repetitions=1,
                run_config=RunConfig("gpt-5.6-terra", "medium"),
                judge_config=JudgeConfig("gpt-5.6-sol", "high"),
                output_dir=Path(temp_dir),
            )

            self.assertEqual(
                [], json.loads(paths["results"].read_text(encoding="utf-8"))
            )

        preflight.assert_not_called()

    def test_legacy_automatic_records_are_reconciled_from_the_current_corpus(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        records = [
            {"case_id": "run-github-project-direct", "arm": "automatic"},
            {"case_id": "run-github-project-direct", "arm": "forced"},
            {"case_id": "grounded-writing-direct", "arm": "automatic"},
            {"case_id": "removed-case", "arm": "automatic"},
        ]

        reconcile_automatic_eligibility(REPO_ROOT, report.cases, records)

        self.assertFalse(records[0]["automatic_eligible"])
        self.assertFalse(records[1]["automatic_eligible"])
        self.assertTrue(records[2]["automatic_eligible"])
        self.assertEqual(["grounded-writing"], records[2]["expected_skills"])
        self.assertFalse(records[3]["automatic_eligible"])

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

    def test_plan_artifact_validator_requires_one_marked_local_draft(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            draft = workspace / ".scratch/to-plan/repair-validator-output.md"
            draft.parent.mkdir(parents=True)
            draft.write_text(
                "<!-- to-plan:conversation-plan:v1 id=123e4567-e89b-42d3-a456-426614174000 -->\n"
                "# Quote missing validator files\n\n"
                "**Planned against:** `main` at `0123456789abcdef0123456789abcdef01234567`\n\n"
                "## Implementation slices\n\n"
                "### 1. Quote missing validator files\n\n"
                "**Validate:** `python3 -B -m unittest tests.test_validator`\n\n"
                "## Final validation\n\n"
                "- `python3 -B -m unittest tests.test_validator`\n\n"
                "Update `validator.py` and `tests/test_validator.py`.\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                ["python3", str(validator), "to-plan-authorized-draft-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_plan_artifact_validator_rejects_multiple_local_drafts(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            drafts = workspace / ".scratch/to-plan"
            drafts.mkdir(parents=True)
            for name in ("first.md", "second.md"):
                (drafts / name).write_text("placeholder\n", encoding="utf-8")

            completed = subprocess.run(
                ["python3", str(validator), "to-plan-authorized-draft-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("expected 1 files, found 2", completed.stderr)


if __name__ == "__main__":
    unittest.main()
