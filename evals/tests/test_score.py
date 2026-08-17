import unittest

from evals.harness.score import compute_scorecard


def record(record_id, arm, outcome, *, kind="direct", expected=(), reported=(), safety=False):
    return {
        "id": record_id,
        "case_id": record_id.split(":", 1)[0],
        "arm": arm,
        "kind": kind,
        "outcome_pass": outcome,
        "expected_skills": list(expected),
        "reported_skills": list(reported),
        "forbidden_action_failure": safety,
    }


class ScorecardTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
