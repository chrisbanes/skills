import unittest
from pathlib import Path

from evals.harness.runner import local_markdown_targets


SKILLS = Path(__file__).resolve().parents[2] / "skills"


class PluginReferencesTest(unittest.TestCase):
    def test_links_resolve_with_only_installable_skill_directories(self):
        installed = {entry.parent for entry in SKILLS.glob("*/SKILL.md")}
        for skill in installed:
            for source in skill.rglob("*.md"):
                for target in local_markdown_targets(source):
                    with self.subTest(source=source.relative_to(SKILLS), target=target):
                        self.assertTrue(any(target.is_relative_to(owner) for owner in installed))
                        self.assertTrue(target.is_file())
