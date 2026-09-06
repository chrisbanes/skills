import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / 'evals/validators/text_case.py'


class ReleaseChangelogCaseTest(unittest.TestCase):
    def validate(self, changelog):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'CHANGELOG.md').write_text(changelog)
            return subprocess.run(
                [sys.executable, str(VALIDATOR), 'release-kotlin-library-direct'],
                cwd=directory, capture_output=True, text=True,
            )

    def test_missing_consumer_change_fails(self):
        original = (ROOT / 'evals/cases/release-kotlin-library-direct/overlay/CHANGELOG.md').read_text()
        self.assertNotEqual(0, self.validate(original).returncode)

    def test_preserved_notes_and_evidenced_fix_pass(self):
        updated = '# Changelog\n\n## Unreleased\n\n- Keep this curated entry exactly.\n- Fix request cancellation so underlying work stops.\n\n## 1.4.0\n\n- Initial stable API.\n'
        self.assertEqual(0, self.validate(updated).returncode)

    def test_rewriting_previous_release_fails(self):
        updated = '## Unreleased\n- Keep this curated entry exactly.\n- Fix cancellation.\n## 1.4.0\n- Rewritten history.\n'
        self.assertNotEqual(0, self.validate(updated).returncode)
