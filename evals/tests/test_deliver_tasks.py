import copy
from dataclasses import replace
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.grade import grade_subject
from evals.harness.runner import SubjectResult, prepare_workspace
from evals.validators.pr_review_decisions import validate_decisions


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'deliver-issue-tree-direct',
    'deliver-issue-resume-novel',
    'deliver-issue-invocation-direct',
    'deliver-issue-ownership-novel',
    'deliver-tasks-migration-partial-failure-novel',
    'deliver-tasks-migration-apply-direct',
    'deliver-tasks-migration-dry-run-direct',
    'deliver-tasks-direct',
    'deliver-tasks-novel',
    'router-single-item-deliver-spec',
    'deliver-tasks-neutral-direct',
    'deliver-tasks-claim-marker-novel',
    'deliver-tasks-derived-handoff-novel',
    'deliver-tasks-default-binding-direct',
    'deliver-tasks-binding-override-novel',
    'deliver-tasks-parent-scope-direct',
    'deliver-tasks-parent-lifecycle-novel',
    'deliver-tasks-label-stop-direct',
    'deliver-tasks-label-recovery-novel',
    'run-project-drain-batched-updates-direct',
    'run-project-drain-batched-updates-novel',
)

NEGATIVE_CASES = (
    'deliver-issue-authority-negative',
    'deliver-issue-completion-negative',
    'deliver-tasks-binding-ambiguity-negative',
    'deliver-tasks-negative',
    'deliver-tasks-parent-restraint-negative',
    'deliver-tasks-parked-negative',
    'run-project-tree-restraint-negative',
    'run-project-drain-batched-updates-negative',
)

SHARED_CONFIG_CASES = (
    'run-project-shared-config-direct',
    'run-project-shared-config-retained-novel',
    'run-project-shared-config-conflict-negative',
)


def markdown_heading_ids(path):
    body = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
    return {
        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        for heading in re.findall(r"^#+ (.*)$", body, re.M)
    }


class DeliverTasksTest(unittest.TestCase):
    def test_read_only_delivery_assessments_pass_only_without_workspace_writes(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in NEGATIVE_CASES + SHARED_CONFIG_CASES:
            case = corpus[case_id]
            expected = json.loads((case.directory / "expectations.json").read_text())["decisions"]
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills)
                subject = SubjectResult(
                    case_id=case_id, arm="forced", command=("codex",), workspace=workspace,
                    returncode=0, events=(), usage={}, changed_paths=(), diff="", stdout="", stderr="", elapsed_seconds=0.1,
                    final_output={"summary": json.dumps(expected), "skills_used": list(case.target_skills), "evidence": ["state.md"]},
                )
                grade = grade_subject(case, subject)
                self.assertTrue(grade.objective_pass, grade.objective_failures)
                self.assertFalse(grade.forbidden_action_failure)
                for scenario, fields in expected.items():
                    for field, value in fields.items():
                        wrong = copy.deepcopy(expected)
                        wrong[scenario][field] = not value if isinstance(value, bool) else "wrong"
                        unsafe = replace(subject, final_output={**subject.final_output, "summary": json.dumps(wrong)})
                        with self.subTest(scenario=scenario, field=field):
                            self.assertFalse(grade_subject(case, unsafe).objective_pass)
                for summary in ("not JSON", "{}"):
                    invalid = replace(subject, final_output={**subject.final_output, "summary": summary})
                    self.assertFalse(grade_subject(case, invalid).objective_pass)
                for path in ("state.md", ".scratch/review-decisions.json", "docs/agents/deliver-tasks.md"):
                    changed = grade_subject(case, replace(subject, changed_paths=(path,)))
                    self.assertTrue(changed.forbidden_action_failure)
                    if case.kind == "negative":
                        self.assertFalse(changed.objective_pass)

    def test_two_delivery_entrypoints_install_without_removed_skills(self):
        from evals.harness.suites import PUBLIC_SKILLS
        for removed in ("deliver-tasks", "deliver-spec", "run-github-project"):
            self.assertNotIn(removed, PUBLIC_SKILLS)
            self.assertFalse((ROOT / "skills" / removed / "SKILL.md").exists())
        corpus = validate_corpus(ROOT).cases
        for skill in ("run-project", "deliver-issue"):
            case = next(c for c in corpus if c.target_skills == (skill,))
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(case, ROOT, Path(directory) / "fixture", enabled_skills=(skill,))
                entry = workspace / ".agents/skills" / skill
                self.assertTrue((entry / "SKILL.md").is_file())
                if skill == "deliver-issue":
                    for board_procedure in ("drain-scheduler", "todo-lane", "ticket-lifecycle", "github-binding"):
                        self.assertFalse((entry / f"references/{board_procedure}.md").exists())
                for source in entry.rglob("*.md"):
                    for link in re.findall(r"\]\(([^)]+)\)", source.read_text()):
                        path, _, anchor = link.partition("#")
                        if ":" in path or path.startswith("../../to-plan/") or (path and not path.endswith(".md")):
                            continue
                        target = source.parent / path if path else source
                        with self.subTest(skill=skill, source=source.name, link=link):
                            self.assertTrue(target.is_file())
                            if skill == "deliver-issue" and anchor:
                                self.assertIn(anchor, markdown_heading_ids(target))

    def test_github_entry_loads_controller_and_both_binding_copies_resolve_core_links(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        case = corpus["run-github-project-direct"]
        with tempfile.TemporaryDirectory() as directory:
            workspace = prepare_workspace(
                case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills,
            )
            installed = workspace / ".agents/skills"
            entry = installed / "run-project/SKILL.md"
            self.assertIn("references/execution-controller.md", entry.read_text())
            for skill in ("run-project",):
                binding = installed / skill / "references/github-binding.md"
                self.assertEqual((ROOT / "references/github-binding.md").read_bytes(), binding.read_bytes())
                for link in re.findall(r"\]\(([^)]+)\)", binding.read_text()):
                    path = link.split("#")[0]
                    if path.endswith(".md") and not path.startswith(("https:", "../../to-plan/")):
                        with self.subTest(skill=skill, link=link):
                            target = binding.parent / path
                            self.assertTrue(target.is_file())
                            anchor = link.partition("#")[2]
                            if anchor:
                                self.assertIn(anchor, markdown_heading_ids(target))
            self.assertTrue((installed / "run-project/scripts/rank_tickets.py").is_file())
            self.assertTrue((installed / "run-project/scripts/watch_project.py").is_file())

    def test_declined_migration_leaves_immutable_fixture_unchanged(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        case = corpus["deliver-tasks-migration-decline-negative"]
        with tempfile.TemporaryDirectory() as directory:
            workspace = prepare_workspace(case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills)
            subject = SubjectResult(
                case_id=case.id, arm="forced", command=("codex",), workspace=workspace,
                returncode=0, events=(), usage={}, changed_paths=(), diff="", stdout="", stderr="", elapsed_seconds=0.1,
                final_output={"summary": "Migration declined; all state preserved", "skills_used": ["run-project"], "evidence": ["state.md"]},
            )
            self.assertTrue(grade_subject(case, subject).objective_pass)
            for path in ("migration-journal.json", "docs/agents/deliver-tasks.md", "AGENTS.md"):
                mutated = replace(subject, changed_paths=(path,))
                grade = grade_subject(case, mutated)
                self.assertFalse(grade.objective_pass)
                self.assertTrue(grade.forbidden_action_failure)

    def test_decision_fixtures_pass_cli_and_reject_each_wrong_decision(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in CASES + NEGATIVE_CASES:
            case = corpus[case_id]
            expected = json.loads((case.directory / "expectations.json").read_text())["decisions"]
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                workspace = prepare_workspace(
                    case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills,
                )
                artifact = workspace / ".scratch/review-decisions.json"
                artifact.parent.mkdir()
                artifact.write_text(json.dumps(expected))
                result = subprocess.run(
                    [sys.executable, str(ROOT / "evals/validators/pr_review_decisions.py"), case_id],
                    cwd=workspace, capture_output=True, text=True,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                if case_id not in NEGATIVE_CASES and ("migration-" in case_id or case_id.startswith("deliver-issue-")):
                    subject = SubjectResult(
                        case_id=case_id, arm="forced", command=("codex",),
                        workspace=workspace, returncode=0, events=(),
                        final_output={"summary": "Assessed immutable migration state", "skills_used": list(case.target_skills), "evidence": [".scratch/review-decisions.json"]},
                        usage={}, changed_paths=(".scratch/review-decisions.json",),
                        diff="", stdout="", stderr="", elapsed_seconds=0.1,
                    )
                    grade = grade_subject(case, subject)
                    self.assertTrue(grade.objective_pass, grade.objective_failures)
                    self.assertFalse(grade.forbidden_action_failure, grade.violations)
                    mutation = replace(subject, changed_paths=("docs/agents/deliver-tasks.md",))
                    self.assertTrue(grade_subject(case, mutation).forbidden_action_failure)
                for scenario, fields in expected.items():
                    for field, value in fields.items():
                        wrong = copy.deepcopy(expected)
                        wrong[scenario][field] = not value if isinstance(value, bool) else "wrong"
                        with self.subTest(scenario=scenario, field=field):
                            self.assertTrue(validate_decisions(wrong, expected))
                artifact.write_text("{}")
                invalid = subprocess.run(
                    [sys.executable, str(ROOT / "evals/validators/pr_review_decisions.py"), case_id],
                    cwd=workspace, capture_output=True, text=True,
                )
                self.assertEqual(1, invalid.returncode)
