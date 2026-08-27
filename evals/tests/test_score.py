import unittest

from evals.harness.score import compute_scorecard


def record(
    record_id,
    arm,
    outcome,
    *,
    kind="direct",
    expected=(),
    allowed=None,
    reported=(),
    safety=False,
):
    return {
        "id": record_id,
        "case_id": record_id.split(":", 1)[0],
        "arm": arm,
        "kind": kind,
        "outcome_pass": outcome,
        "expected_skills": list(expected),
        "allowed_skills": list(expected if allowed is None else allowed),
        "reported_skills": list(reported),
        "forbidden_action_failure": safety,
    }


class ScorecardTest(unittest.TestCase):
    def test_optional_allowed_routes_do_not_hurt_precision_or_recall(self):
        records = [
            record(
                "one:automatic",
                "automatic",
                True,
                expected=("compose-state-and-effects",),
                allowed=(
                    "compose-state-and-effects",
                    "compose-focus-navigation",
                ),
                reported=(
                    "compose-state-and-effects",
                    "compose-focus-navigation",
                ),
            ),
            record(
                "two:automatic",
                "automatic",
                True,
                expected=("compose-state-and-effects",),
                allowed=(
                    "compose-state-and-effects",
                    "compose-focus-navigation",
                ),
                reported=("compose-state-and-effects",),
            ),
        ]

        score = compute_scorecard(records)

        self.assertEqual(1.0, score.routing_precision)
        self.assertEqual(1.0, score.routing_recall)

    def test_applies_uplift_retention_routing_negative_and_safety_gates(self):
        records = []
        for index, outcomes in enumerate(((True, True, True), (False, True, True), (True, True, True), (False, False, False))):
            for arm, outcome in zip(("none", "forced", "automatic"), outcomes):
                records.append(
                    record(
                        f"positive-{index}:{arm}",
                        arm,
                        outcome,
                        expected=("compose-state-and-effects",),
                        reported=("compose-state-and-effects",) if arm == "automatic" else (),
                    )
                )
        for arm in ("none", "forced", "automatic"):
            records.append(record(f"negative:{arm}", arm, True, kind="negative"))

        score = compute_scorecard(records)

        self.assertEqual(0.5, score.outcome_rates["none"])
        self.assertEqual(0.25, score.forced_uplift)
        self.assertEqual(1.0, score.automatic_retention)
        self.assertEqual(1.0, score.routing_precision)
        self.assertEqual(1.0, score.routing_recall)
        self.assertTrue(all(score.gates.values()))

    def test_non_positive_forced_uplift_cannot_pass_retention(self):
        records = [
            record("one:none", "none", True),
            record("one:forced", "forced", True),
            record("one:automatic", "automatic", True),
        ]

        score = compute_scorecard(records)

        self.assertIsNone(score.automatic_retention)
        self.assertFalse(score.gates["forced_uplift"])
        self.assertFalse(score.gates["automatic_retention"])

    def test_missing_conditions_are_not_assessed_or_passed(self):
        records = [
            record("one:none", "none", False),
            record("one:forced", "forced", True),
        ]

        score = compute_scorecard(records)

        self.assertIsNone(score.outcome_rates["automatic"])
        self.assertIsNone(score.negative_rates["none"])
        self.assertIsNone(score.routing_precision)
        self.assertFalse(score.gates["automatic_retention"])
        self.assertFalse(score.gates["routing_precision"])
        self.assertFalse(score.gates["negative_controls"])

    def test_measures_subject_efficiency_and_charges_failures_to_each_pass(self):
        def with_telemetry(item, *, tokens, tool_calls, turns, elapsed):
            item["subject"] = {
                "usage": {"input_tokens": tokens - 2, "output_tokens": 2},
                "events": [
                    {
                        "type": "item.completed",
                        "item": {"type": "command_execution"},
                    }
                    for _ in range(tool_calls)
                ] + [{"type": "turn.completed"} for _ in range(turns)],
                "elapsed_seconds": elapsed,
            }
            return item

        records = [
            with_telemetry(
                record("one:none", "none", True),
                tokens=10,
                tool_calls=1,
                turns=1,
                elapsed=1.0,
            ),
            with_telemetry(
                record("two:none", "none", False),
                tokens=30,
                tool_calls=3,
                turns=2,
                elapsed=3.0,
            ),
            with_telemetry(
                record("one:forced", "forced", True),
                tokens=20,
                tool_calls=2,
                turns=1,
                elapsed=2.0,
            ),
            with_telemetry(
                record("two:forced", "forced", True),
                tokens=20,
                tool_calls=2,
                turns=1,
                elapsed=2.0,
            ),
        ]

        score = compute_scorecard(records)

        baseline = score.efficiency["none"]
        self.assertEqual(20.0, baseline.median_tokens_per_run)
        self.assertEqual(2.0, baseline.median_tool_calls_per_run)
        self.assertEqual(2.0, baseline.median_elapsed_seconds_per_run)
        self.assertEqual(1.5, baseline.median_turns_per_run)
        self.assertEqual(40.0, baseline.total_tokens)
        self.assertEqual(4.0, baseline.total_tool_calls)
        self.assertEqual(3.0, baseline.total_turns)
        self.assertEqual(4.0, baseline.total_elapsed_seconds)
        self.assertEqual(40.0, baseline.tokens_per_outcome_pass)
        self.assertEqual(4.0, baseline.tool_calls_per_outcome_pass)
        self.assertEqual(4.0, baseline.elapsed_seconds_per_outcome_pass)
        forced = score.efficiency["forced"]
        self.assertEqual(20.0, forced.tokens_per_outcome_pass)
        self.assertEqual(2, forced.outcome_passes)

    def test_marks_efficiency_unavailable_without_subject_telemetry(self):
        score = compute_scorecard([record("one:none", "none", True)])

        efficiency = score.efficiency["none"]
        self.assertIsNone(efficiency.median_tokens_per_run)
        self.assertIsNone(efficiency.median_tool_calls_per_run)
        self.assertIsNone(efficiency.median_elapsed_seconds_per_run)
        self.assertIsNone(efficiency.median_turns_per_run)
        self.assertIsNone(efficiency.total_turns)
        self.assertIsNone(efficiency.tokens_per_outcome_pass)

    def test_includes_retry_attempts_in_subject_efficiency(self):
        item = record("one:forced", "forced", True)
        item["subject"] = {
            "usage": {"input_tokens": 1, "output_tokens": 1},
            "events": [],
            "elapsed_seconds": 1.0,
            "attempts": [
                {
                    "usage": {"input_tokens": 8, "output_tokens": 2},
                    "tool_calls": 2,
                    "turns": 1,
                    "elapsed_seconds": 3.0,
                },
                {
                    "usage": {"input_tokens": 18, "output_tokens": 2},
                    "tool_calls": 1,
                    "turns": 2,
                    "elapsed_seconds": 4.0,
                },
            ],
        }

        efficiency = compute_scorecard([item]).efficiency["forced"]

        self.assertEqual(30.0, efficiency.median_tokens_per_run)
        self.assertEqual(3.0, efficiency.median_tool_calls_per_run)
        self.assertEqual(7.0, efficiency.median_elapsed_seconds_per_run)
        self.assertEqual(3.0, efficiency.median_turns_per_run)
        self.assertEqual(3.0, efficiency.total_turns)

    def test_does_not_undercount_historical_records_missing_retry_telemetry(self):
        item = record("one:forced", "forced", True)
        item["subject"] = {
            "usage": {"input_tokens": 8, "output_tokens": 2},
            "events": [],
            "elapsed_seconds": 1.0,
            "retries": 1,
        }

        efficiency = compute_scorecard([item]).efficiency["forced"]

        self.assertIsNone(efficiency.median_tokens_per_run)
        self.assertIsNone(efficiency.median_tool_calls_per_run)
        self.assertIsNone(efficiency.median_elapsed_seconds_per_run)
        self.assertIsNone(efficiency.median_turns_per_run)

    def test_groups_baseline_and_automatic_efficiency_by_target_skill(self):
        baseline = record("state:none", "none", False)
        baseline.update(
            {
                "target_skills": ["compose-state-and-effects"],
                "subject": {
                    "usage": {"input_tokens": 4, "output_tokens": 1},
                    "events": [{"type": "turn.completed"}],
                    "elapsed_seconds": 1.0,
                },
            }
        )
        state = record("state:automatic", "automatic", True)
        state.update(
            {
                "target_skills": ["compose-state-and-effects"],
                "subject": {
                    "usage": {"input_tokens": 8, "output_tokens": 2},
                    "events": [{"type": "turn.completed"}],
                    "elapsed_seconds": 2.0,
                },
            }
        )
        overlap = record("overlap:automatic", "automatic", False)
        overlap.update(
            {
                "target_skills": [
                    "compose-state-and-effects",
                    "compose-focus-navigation",
                ],
                "subject": {
                    "usage": {"input_tokens": 18, "output_tokens": 2},
                    "events": [
                        {"type": "item.completed", "item": {"type": "tool_call"}},
                        {"type": "turn.completed"},
                    ],
                    "elapsed_seconds": 4.0,
                },
            }
        )

        score = compute_scorecard([baseline, state, overlap])

        state_efficiency = score.skill_efficiency["compose-state-and-effects"]
        self.assertEqual(1, state_efficiency["none"].runs)
        self.assertEqual(5.0, state_efficiency["none"].total_tokens)
        self.assertEqual(2, state_efficiency["automatic"].runs)
        self.assertEqual(30.0, state_efficiency["automatic"].total_tokens)
        self.assertEqual(1.0, state_efficiency["automatic"].total_tool_calls)
        self.assertEqual(2.0, state_efficiency["automatic"].total_turns)
        focus_efficiency = score.skill_efficiency["compose-focus-navigation"]
        self.assertEqual(0, focus_efficiency["none"].runs)
        self.assertEqual(1, focus_efficiency["automatic"].runs)
        self.assertEqual(20.0, focus_efficiency["automatic"].total_tokens)


if __name__ == "__main__":
    unittest.main()
