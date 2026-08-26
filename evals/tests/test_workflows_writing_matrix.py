import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.codex import RunConfig, build_subject_command, prepare_workspace
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

                prepare_workspace(case, REPO_ROOT, workspace)
                self.assertTrue(
                    (workspace / ".agents/skills/implement/SKILL.md").is_file()
                )

    def test_workflow_prompts_do_not_disclose_the_target_skill(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)


if __name__ == "__main__":
    unittest.main()
