import json
import tempfile
import unittest
from pathlib import Path

from evals.harness.report import (
    append_audit_decision,
    build_audit_queue,
    render_scorecard,
    write_reports,
)
from evals.harness.score import compute_scorecard
from evals.tests.test_score import record


class ReportTest(unittest.TestCase):
    def test_audit_queue_includes_disagreements_inconsistency_and_seeded_sample(self):
        records = []
        for index in range(20):
            item = record(f"case-{index}:automatic", "automatic", True)
            item.update(
                {
                    "case_id": f"case-{index}",
                    "repetition": 1,
                    "objective_pass": True,
                    "judge_pass": False if index == 0 else True,
                }
            )
            records.append(item)
        repeated = record("case-1:automatic:2", "automatic", False)
        repeated.update(
            {
                "case_id": "case-1",
                "repetition": 2,
                "objective_pass": False,
                "judge_pass": False,
            }
        )
        records.append(repeated)

        queue = build_audit_queue(records, seed=7)
        reasons = {entry["id"]: set(entry["reasons"]) for entry in queue}

        self.assertIn("judge-objective-disagreement", reasons["case-0:automatic"])
        self.assertIn("within-condition-inconsistency", reasons["case-1:automatic"])
        self.assertIn("within-condition-inconsistency", reasons["case-1:automatic:2"])
        sampled = [entry for entry in queue if "seeded-sample" in entry["reasons"]]
        self.assertEqual(2, len(sampled))

    def test_writes_machine_results_and_advisory_markdown(self):
        records = [
            record(
                "one:none",
                "none",
                False,
                expected=("compose-state-and-effects",),
            ),
            record(
                "one:forced",
                "forced",
                True,
                expected=("compose-state-and-effects",),
            ),
            record(
                "one:automatic",
                "automatic",
                True,
                expected=("compose-state-and-effects",),
            ),
        ]
        for item in records:
            item.update({
                "suite": "compose",
                "target_skills": ["compose-state-and-effects"],
                "objective_pass": item["outcome_pass"],
                "judge_pass": item["outcome_pass"],
                "repetition": 1,
                "subject": {
                    "usage": {"input_tokens": 10, "output_tokens": 2},
                    "events": [{"type": "item.completed", "item": {"type": "command_execution"}}],
                    "elapsed_seconds": 1.5,
                    "retries": 1,
                    "returncode": 0,
                },
                "judge": {
                    "usage": {"input_tokens": 4, "output_tokens": 1},
                    "events": [
                        {
                            "type": "item.completed",
                            "item": {"type": "command_execution"},
                        }
                    ],
                    "elapsed_seconds": 0.5,
                    "retries": 0,
                    "returncode": 0,
                },
            })
        score = compute_scorecard(records)

        with tempfile.TemporaryDirectory() as temp_dir:
            paths = write_reports(Path(temp_dir), records, score, seed=3)

            self.assertEqual(3, len(json.loads(paths["results"].read_text())))
            markdown = paths["scorecard"].read_text()
            self.assertIn("Advisory Compose Skill Scorecard", markdown)
            self.assertIn("not a merge or release gate", markdown)
            self.assertIn("Reported automatic routing precision", markdown)
            self.assertIn("Per-skill diagnostics", markdown)
            self.assertIn("`compose-state-and-effects`", markdown)
            self.assertIn("Input tokens: 42", markdown)
            self.assertIn("Output tokens: 9", markdown)
            self.assertIn("Tool events: 6", markdown)
            self.assertIn("Retries: 3", markdown)
            self.assertEqual(markdown, render_scorecard(score, records))

    def test_per_skill_restraint_groups_negative_controls_by_target(self):
        records = [
            record(
                "negative:forced",
                "forced",
                True,
                kind="negative",
                expected=(),
            ),
            record(
                "negative:automatic",
                "automatic",
                True,
                kind="negative",
                expected=(),
            ),
        ]
        for item in records:
            item.update({
                "suite": "compose",
                "target_skills": ["compose-state-and-effects"],
            })

        markdown = render_scorecard(compute_scorecard(records), records)

        self.assertIn(
            "| `compose-state-and-effects` | 0 | not met | not met | not met | "
            "not met | 100.0% | 100.0% |",
            markdown,
        )

    def test_per_skill_count_uses_the_arms_present_in_a_partial_run(self):
        records = [
            record(
                "one:forced",
                "forced",
                True,
                expected=("compose-state-and-effects",),
            )
        ]
        records[0].update(
            {
                "suite": "compose",
                "target_skills": ["compose-state-and-effects"],
            }
        )

        markdown = render_scorecard(compute_scorecard(records), records)

        self.assertIn("| `compose-state-and-effects` | 1 |", markdown)

    def test_audit_decisions_append_without_overwriting_raw_judgments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "audit-decisions.jsonl"
            append_audit_decision(path, "case:none:1", "accept", "checks agree")
            append_audit_decision(path, "case:none:1", "reject", "manual review")

            decisions = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(["accept", "reject"], [item["decision"] for item in decisions])
            self.assertEqual("case:none:1", decisions[0]["id"])


if __name__ == "__main__":
    unittest.main()
