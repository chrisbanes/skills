import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import validate_corpus
from evals.harness.runner import prepare_workspace
from evals.validators.pr_review_decisions import validate_decisions


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "deliver-tasks-direct", "deliver-tasks-novel", "deliver-tasks-negative",
    "router-single-item-deliver-spec",
    "deliver-tasks-neutral-direct", "deliver-tasks-claim-marker-novel",
    "deliver-tasks-parked-negative",
)


class DeliverTasksTest(unittest.TestCase):
    def test_github_entry_loads_controller_and_both_binding_copies_resolve_core_links(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        case = corpus["run-github-project-direct"]
        with tempfile.TemporaryDirectory() as directory:
            workspace = prepare_workspace(
                case, ROOT, Path(directory) / "fixture", enabled_skills=case.target_skills,
            )
            installed = workspace / ".agents/skills"
            entry = installed / "run-github-project/SKILL.md"
            self.assertIn("../deliver-tasks/SKILL.md", entry.read_text())
            self.assertTrue((entry.parent / "../deliver-tasks/SKILL.md").is_file())
            for skill in ("deliver-tasks", "run-github-project"):
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
                                body = re.sub(r"```.*?```", "", target.read_text(), flags=re.S)
                                headings = {
                                    re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                                    for heading in re.findall(r"^#+ (.*)$", body, re.M)
                                }
                                self.assertIn(anchor, headings)
            self.assertTrue((installed / "deliver-tasks/scripts/rank_tickets.py").is_file())
            self.assertTrue((installed / "run-github-project/scripts/watch_project.py").is_file())

    def test_decision_fixtures_pass_cli_and_reject_each_wrong_decision(self):
        corpus = {case.id: case for case in validate_corpus(ROOT).cases}
        for case_id in CASES:
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
