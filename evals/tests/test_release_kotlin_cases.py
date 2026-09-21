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

    def completed_changelog(self):
        original = (ROOT / 'evals/cases/release-kotlin-library-direct/overlay/CHANGELOG.md').read_text()
        updated = original.replace(
            '- Keep this curated entry exactly.',
            '- Keep this curated entry exactly.\n- Fix request cancellation so underlying work stops.\n- Add streaming responses with bounded buffering.',
        )
        return updated.replace('## Unreleased', '## 2.0.0').replace(
            '## 2.0.0-rc00', '<details>\n<summary>Prerelease history</summary>\n\n## 2.0.0-rc00',
        ).replace('## 1.4.0', '</details>\n\n## 1.4.0')

    def test_preserved_notes_and_evidenced_fix_pass(self):
        self.assertEqual(0, self.validate(self.completed_changelog()).returncode)

    def test_rewriting_previous_release_fails(self):
        updated = '## Unreleased\n- Keep this curated entry exactly.\n- Fix cancellation.\n## 1.4.0\n- Rewritten history.\n'
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_rc_delta_only_fails(self):
        updated = self.completed_changelog().replace(
            '- Add streaming responses with bounded buffering.\n', '',
        )
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_release_links_cannot_replace_original_notes(self):
        updated = self.completed_changelog().replace(
            '- Add streaming responses with unbounded buffering.',
            '- See GitHub Release for details.',
        )
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_older_stable_release_must_remain_outside_details(self):
        updated = self.completed_changelog().replace('</details>\n\n', '') + '\n</details>\n'
        self.assertNotEqual(0, self.validate(updated).returncode)
