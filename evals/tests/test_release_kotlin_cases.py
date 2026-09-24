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
            '- Keep this curated entry exactly.\n'
            '- Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).\n'
            '- Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).',
        )
        return updated.replace('## Unreleased', '## 2.0.0').replace(
            '## 2.0.0-rc00', '<details>\n<summary>Prerelease history</summary>\n\n## 2.0.0-rc00',
        ).replace('## 1.4.0', '</details>\n\n## 1.4.0')

    def test_preserved_notes_and_evidenced_fix_pass(self):
        self.assertEqual(0, self.validate(self.completed_changelog()).returncode)

    def test_cancelling_wording_in_stable_summary_passes(self):
        original = self.completed_changelog()
        updated = original.replace(
            'Fix request cancellation so underlying work stops ',
            'Cancelling a public request now stops underlying work ',
        )
        self.assertNotEqual(original, updated)
        self.assertIn('Cancelling a public request now stops underlying work', updated)
        self.assertEqual(0, self.validate(updated).returncode)

    def test_missing_cancellation_concept_in_stable_summary_fails(self):
        updated = self.completed_changelog().replace(
            '- Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).\n', '',
        )
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_cancellation_only_in_prerelease_details_fails(self):
        updated = self.completed_changelog().replace(
            '- Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).\n', '',
        ).replace(
            '- Add streaming responses with unbounded buffering.',
            '- Add streaming responses with unbounded buffering.\n'
            '- Fix request cancellation so underlying work stops.',
        )
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_rewriting_previous_release_fails(self):
        updated = '## Unreleased\n- Keep this curated entry exactly.\n- Fix cancellation.\n## 1.4.0\n- Rewritten history.\n'
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_rc_delta_only_fails(self):
        updated = self.completed_changelog().replace(
            '- Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).\n', '',
        )
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_pr_links_under_older_release_fail(self):
        updated = self.completed_changelog().replace(
            ' ([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example))',
            '',
        ).replace(
            ' ([#812](https://github.com/chrisbanes/skills/pull/812))',
            '',
        ).replace(
            '- Initial stable API.',
            '- Initial stable API.\n\n'
            '- Related changes: [#812](https://github.com/chrisbanes/skills/pull/812), '
            '[#845](https://github.com/chrisbanes/skills/pull/845), '
            '[Avery Example](https://github.com/avery-example).',
        )
        self.assertIn('[#812](https://github.com/chrisbanes/skills/pull/812)', updated)
        self.assertIn('[#845](https://github.com/chrisbanes/skills/pull/845)', updated)
        self.assertIn('[Avery Example](https://github.com/avery-example)', updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_pr_links_on_separate_summary_line_fail(self):
        updated = self.completed_changelog().replace(
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example))',
            '(PR #845)',
        ).replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '(PR #812)',
        ).replace(
            '- Add streaming responses with bounded buffering (PR #812).',
            '- Add streaming responses with bounded buffering (PR #812).\n'
            '- Related links: [#812](https://github.com/chrisbanes/skills/pull/812), '
            '[#845](https://github.com/chrisbanes/skills/pull/845), '
            '[Avery Example](https://github.com/avery-example).',
        )
        self.assertIn('- Fix request cancellation so underlying work stops (PR #845).', updated)
        self.assertIn('- Add streaming responses with bounded buffering (PR #812).', updated)
        self.assertIn('- Related links: [#812]', updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_pr_links_only_in_prerelease_history_fail(self):
        updated = self.completed_changelog().replace(
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example))',
            '(PR #845)',
        ).replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '(PR #812)',
        ).replace(
            '</details>',
            '- Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).\n'
            '- Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).\n'
            '</details>',
        )
        self.assertIn('Fix request cancellation so underlying work stops (PR #845)', updated)
        self.assertIn('Add streaming responses with bounded buffering (PR #812)', updated)
        self.assertIn('<details>', updated)
        self.assertIn('[#812](https://github.com/chrisbanes/skills/pull/812)', updated)
        self.assertIn('[#845](https://github.com/chrisbanes/skills/pull/845)', updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_wrapped_pr_links_on_stable_bullets_pass(self):
        original = self.completed_changelog()
        updated = original.replace(
            'Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).',
            'Fix request cancellation so underlying work stops\n'
            '  [#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example).',
        ).replace(
            'Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).',
            'Add streaming responses with bounded buffering\n'
            '  [#812](https://github.com/chrisbanes/skills/pull/812).',
        )
        self.assertNotEqual(original, updated)
        self.assertIn(
            'Fix request cancellation so underlying work stops\n'
            '  [#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example).',
            updated,
        )
        self.assertIn(
            'Add streaming responses with bounded buffering\n'
            '  [#812](https://github.com/chrisbanes/skills/pull/812).',
            updated,
        )
        self.assertEqual(0, self.validate(updated).returncode)

    def test_release_links_cannot_replace_original_notes(self):
        updated = self.completed_changelog().replace(
            '- Add streaming responses with unbounded buffering.',
            '- See GitHub Release for details.',
        )
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_older_stable_release_must_remain_outside_details(self):
        updated = self.completed_changelog().replace('</details>\n\n', '') + '\n</details>\n'
        self.assertNotEqual(0, self.validate(updated).returncode)
