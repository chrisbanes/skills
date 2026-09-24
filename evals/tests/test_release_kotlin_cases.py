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

    def test_pr_links_after_thematic_break_fail(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example))',
            '(PR #845)\n---\n'
            '[#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)',
        ).replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '(PR #812)\n---\n'
            '[#812](https://github.com/chrisbanes/skills/pull/812)',
        )
        self.assertNotEqual(original, updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern', result.stderr)

    def test_release_bullets_only_in_fenced_code_fail(self):
        original = self.completed_changelog()
        first_bullet = original.index('- Fix request cancellation so underlying work stops')
        summary_end = original.index('\n\n<details>', first_bullet)
        updated = (
            original[:first_bullet]
            + '```md\n'
            + original[first_bullet:summary_end]
            + '\n```'
            + original[summary_end:]
        )
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern in a release bullet', result.stderr)

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

    def test_wrapped_credit_before_pr_link_passes(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example))',
            '\n  [Avery Example](https://github.com/avery-example); '
            '[#845](https://github.com/chrisbanes/skills/pull/845)',
        )
        self.assertNotEqual(original, updated)
        self.assertLess(
            updated.index('[Avery Example](https://github.com/avery-example)'),
            updated.index('[#845](https://github.com/chrisbanes/skills/pull/845)'),
        )
        self.assertEqual(0, self.validate(updated).returncode)

    def test_lazy_continuation_links_on_stable_bullets_pass(self):
        original = self.completed_changelog()
        updated = original.replace(
            'Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).',
            'Fix request cancellation so underlying work stops\n'
            '[Avery Example](https://github.com/avery-example); '
            '[#845](https://github.com/chrisbanes/skills/pull/845).',
        ).replace(
            'Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).',
            'Add streaming responses with bounded buffering\n'
            '[#812](https://github.com/chrisbanes/skills/pull/812).',
        )
        self.assertNotEqual(original, updated)
        self.assertIn(
            'Fix request cancellation so underlying work stops\n'
            '[Avery Example](https://github.com/avery-example); '
            '[#845](https://github.com/chrisbanes/skills/pull/845).',
            updated,
        )
        self.assertIn(
            'Add streaming responses with bounded buffering\n'
            '[#812](https://github.com/chrisbanes/skills/pull/812).',
            updated,
        )
        self.assertEqual(0, self.validate(updated).returncode)

    def test_wrapped_description_terms_on_stable_bullets_pass(self):
        original = self.completed_changelog()
        updated = original.replace(
            'Fix request cancellation so underlying work stops '
            '([#845](https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example)).',
            'Fix request behavior\n'
            'so cancellation stops underlying work [#845]'
            '(https://github.com/chrisbanes/skills/pull/845); '
            '[Avery Example](https://github.com/avery-example).',
        ).replace(
            'Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).',
            'Add response support\n'
            'for streaming traffic with bounded buffering [#812]'
            '(https://github.com/chrisbanes/skills/pull/812).',
        )
        self.assertNotEqual(original, updated)
        self.assertIn(
            'Fix request behavior\nso cancellation stops underlying work [#845]',
            updated,
        )
        self.assertIn(
            'Add response support\nfor streaming traffic with bounded buffering [#812]',
            updated,
        )
        self.assertEqual(0, self.validate(updated).returncode)

    def test_fenced_example_with_later_description_and_link_passes(self):
        original = self.completed_changelog()
        updated = original.replace(
            '- Add streaming responses with bounded buffering '
            '([#812](https://github.com/chrisbanes/skills/pull/812)).',
            '- Add response support:\n\n'
            '  ```kotlin\n'
            '  streamResponses()\n'
            '  ```\n\n'
            '  Streaming responses use bounded buffering '
            '[#812](https://github.com/chrisbanes/skills/pull/812).',
        )
        self.assertNotEqual(original, updated)
        self.assertEqual(0, self.validate(updated).returncode)

    def test_loose_list_continuation_link_passes(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '\n\n  [#812](https://github.com/chrisbanes/skills/pull/812)',
        )
        self.assertNotEqual(original, updated)
        self.assertEqual(0, self.validate(updated).returncode)

    def test_link_only_inside_fenced_example_fails(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '\n  ```md\n'
            '  [#812](https://github.com/chrisbanes/skills/pull/812)\n'
            '  ```',
        )
        self.assertNotEqual(original, updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern in a release bullet', result.stderr)

    def test_plus_marked_release_bullets_pass(self):
        original = self.completed_changelog()
        updated = original.replace(
            '- Fix request cancellation so underlying work stops ',
            '+ Fix request cancellation so underlying work stops ',
        ).replace(
            '- Add streaming responses with bounded buffering ',
            '+ Add streaming responses with bounded buffering ',
        )
        self.assertNotEqual(original, updated)
        self.assertEqual(0, self.validate(updated).returncode)

    def test_links_in_adjacent_mixed_marker_items_fail(self):
        original = self.completed_changelog()
        for marker in ('+', '1.'):
            with self.subTest(marker=marker):
                updated = original.replace(
                    '([#812](https://github.com/chrisbanes/skills/pull/812))',
                    '(PR #812)\n'
                    f'{marker} Related: '
                    '[#812](https://github.com/chrisbanes/skills/pull/812)',
                )
                self.assertNotEqual(original, updated)
                result = self.validate(updated)
                self.assertEqual(1, result.returncode)
                self.assertIn('missing required pattern in a release bullet', result.stderr)

    def test_pr_link_only_in_html_comment_fails(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '<!-- [#812](https://github.com/chrisbanes/skills/pull/812) -->',
        )
        self.assertNotEqual(original, updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern in a release bullet', result.stderr)

    def test_pr_link_only_in_inline_code_fails(self):
        original = self.completed_changelog()
        updated = original.replace(
            '[#812](https://github.com/chrisbanes/skills/pull/812)',
            '`[#812](https://github.com/chrisbanes/skills/pull/812)`',
        )
        self.assertNotEqual(original, updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern in a release bullet', result.stderr)

    def test_link_in_indented_sibling_item_fails(self):
        original = self.completed_changelog()
        updated = original.replace(
            '([#812](https://github.com/chrisbanes/skills/pull/812))',
            '(PR #812)\n'
            ' - Related: [#812](https://github.com/chrisbanes/skills/pull/812)',
        )
        self.assertNotEqual(original, updated)
        result = self.validate(updated)
        self.assertEqual(1, result.returncode)
        self.assertIn('missing required pattern in a release bullet', result.stderr)

    def test_release_links_cannot_replace_original_notes(self):
        updated = self.completed_changelog().replace(
            '- Add streaming responses with unbounded buffering.',
            '- See GitHub Release for details.',
        )
        self.assertNotEqual(0, self.validate(updated).returncode)

    def test_older_stable_release_must_remain_outside_details(self):
        updated = self.completed_changelog().replace('</details>\n\n', '') + '\n</details>\n'
        self.assertNotEqual(0, self.validate(updated).returncode)
