import unittest

from evals.harness.score import compute_scorecard, forced_integrity_status


def record(
    record_id,
    arm,
    outcome,
    *,
    kind="direct",
    expected=(),
    allowed=None,
    reported=(),
    target=None,
    preflight=None,
    safety=False,
    automatic_eligible=True,
):
    item = {
        "id": record_id,
        "case_id": record_id.split(":", 1)[0],
        "arm": arm,
        "kind": kind,
        "outcome_pass": outcome,
        "expected_skills": list(expected),
        "allowed_skills": list(expected if allowed is None else allowed),
        "reported_skills": list(reported),
        "automatic_eligible": automatic_eligible,
        "forbidden_action_failure": safety,
    }
    if target is not None:
        item["target_skills"] = list(target)
    if preflight is not None:
        item["forced_target_preflight"] = preflight
    return item


def complete_read_evidence(item):
    target = item["forced_target_preflight"]["targets"][0]
    target["staged_sha256"] = "entrypoint-sha"
    event = item["subject"]["events"][0]["item"]
    event["id"] = "read"
    item["subject"]["captured_skill_files"] = [{
        "path": target["staged_relative_path"],
        "staged_sha256": "entrypoint-sha",
        "status": "complete",
        "matched_events": [{"id": "read", "output_sha256": "output-sha"}],
    }]


class ScorecardTest(unittest.TestCase):
    def test_forced_integrity_requires_complete_captured_entrypoint_for_same_read(self):
        path = ".agents/skills/to-plan/SKILL.md"
        preflight = {"valid": True, "targets": [{
            "skill": "to-plan", "staged_path": f"/workspace/{path}",
            "staged_relative_path": path, "staged_sha256": "entrypoint-sha",
            "status": "valid",
        }]}

        def packet(command, output, status, matched_id="read"):
            item = record(
                "case:forced", "forced", True, target=("to-plan",),
                reported=("to-plan",), preflight=preflight,
            )
            item["subject"] = {
                "events": [{"type": "item.completed", "item": {
                    "id": "read", "type": "command_execution", "status": "completed",
                    "exit_code": 0, "command": command,
                    "aggregated_output": output,
                }}],
                "captured_skill_files": [{
                    "path": path, "staged_sha256": "entrypoint-sha",
                    "status": status,
                    "matched_events": (
                        [{"id": matched_id, "output_sha256": "output-sha"}]
                        if status == "complete" else []
                    ),
                }],
            }
            return item

        reference_only = packet(
            "cat .agents/skills/to-plan/references/workflow.md",
            "full reference text", "incomplete_or_absent",
        )
        warnings_only = packet(f"cat {path}", "warnings only", "incomplete_or_absent")
        path_only = packet(f"cat {path}", "warnings only", "incomplete_or_absent")
        del path_only["subject"]["captured_skill_files"]
        unrelated_capture = packet(f"cat {path}", "warnings only", "complete", "other")
        full_entrypoint = packet(f"cat {path}", "full entrypoint text", "complete")

        for item in (reference_only, warnings_only, path_only, unrelated_capture):
            self.assertEqual("invocation_failure", forced_integrity_status(item))
        self.assertEqual("valid", forced_integrity_status(full_entrypoint))
        self.assertFalse(compute_scorecard([reference_only]).gates["forced_integrity"])

        late_read = packet(f"cat {path}", "full entrypoint text", "complete")
        late_read["subject"]["events"].insert(0, {
            "type": "item.completed", "item": {
                "id": "earlier", "type": "command_execution", "status": "completed",
                "exit_code": 0, "command": "git status",
            },
        })
        compound_read = packet(
            f"git status && cat {path}", "full entrypoint text", "complete"
        )
        additional_file = packet(
            f"cat {path} README.md", "full entrypoint text", "complete"
        )
        overlapping_action = packet(f"cat {path}", "full entrypoint text", "complete")
        overlapping_action["subject"]["events"][:0] = [
            {"type": "item.started", "item": {"id": "read", "type": "command_execution"}},
            {"type": "item.started", "item": {"id": "other", "type": "web_search"}},
        ]
        for item in (late_read, compound_read, additional_file, overlapping_action):
            self.assertEqual("invocation_failure", forced_integrity_status(item))
        self.assertEqual("invocation_failure", forced_integrity_status(packet(
            f"sed -n '1,$p' {path}", "full entrypoint text", "complete"
        )))
        self.assertEqual("valid", forced_integrity_status(packet(
            f"/usr/bin/cat {path}", "full entrypoint text", "complete"
        )))
        self.assertEqual("invocation_failure", forced_integrity_status(packet(
            f"/bin/sed -n '1,$p' {path}", "full entrypoint text", "complete"
        )))

    def test_forced_read_requires_all_targets_in_the_first_standalone_action(self):
        paths = (
            ".agents/skills/to-plan/SKILL.md",
            ".agents/skills/run-github-project/SKILL.md",
        )
        preflight = {"valid": True, "targets": [{
            "skill": path.split("/")[2],
            "staged_relative_path": path,
            "staged_path": f"/workspace/{path}",
            "staged_sha256": path,
        } for path in paths]}
        item = record(
            "case:forced", "forced", True,
            target=("to-plan", "run-github-project"),
            reported=("to-plan", "run-github-project"), preflight=preflight,
        )
        item["subject"] = {
            "events": [
                {"type": "item.started", "item": {
                    "id": "read", "type": "command_execution",
                }},
                {"type": "item.completed", "item": {
                    "id": "read", "type": "command_execution", "status": "completed",
                    "exit_code": 0, "command": f"cat {paths[0]} {paths[1]}",
                }},
            ],
            "captured_skill_files": [{
                "path": path, "status": "complete", "staged_sha256": path,
                "matched_events": [{"id": "read"}],
            } for path in paths],
        }
        self.assertEqual("valid", forced_integrity_status(item))
        item["subject"]["events"][1]["item"]["command"] = f"cat {paths[0]}"
        self.assertEqual("invocation_failure", forced_integrity_status(item))

    def test_classifies_forced_integrity_from_preflight_reports_and_observed_reads(self):
        preflight = {
            "valid": True,
            "targets": [
                {
                    "skill": "to-plan",
                    "staged_path": "/workspace/.agents/skills/to-plan/SKILL.md",
                    "staged_relative_path": ".agents/skills/to-plan/SKILL.md",
                    "status": "valid",
                }
            ],
        }
        missing = record(
            "missing:forced", "forced", False, target=("to-plan",),
            preflight={"valid": False, "targets": [{"status": "missing_target"}]},
        )
        invocation = record(
            "invoke:forced", "forced", False, target=("to-plan",), preflight=preflight
        )
        reporting = record(
            "report:forced", "forced", False, target=("to-plan",), preflight=preflight
        )
        reporting["subject"] = {"events": [
            {"type": "item.completed", "item": {"type": "command_execution", "status": "completed", "exit_code": 0, "command": "cat .agents/skills/to-plan/SKILL.md"}}
        ]}
        complete_read_evidence(reporting)
        valid = record(
            "valid:forced", "forced", True, target=("to-plan",),
            reported=("to-plan",), preflight=preflight,
        )
        valid["subject"] = reporting["subject"]

        self.assertEqual("missing_target", forced_integrity_status(missing))
        self.assertEqual("invocation_failure", forced_integrity_status(invocation))
        self.assertEqual("reporting_failure", forced_integrity_status(reporting))
        self.assertEqual("valid", forced_integrity_status(valid))

    def test_requires_completed_successful_read_and_report_for_forced_validity(self):
        preflight = {"valid": True, "targets": [{
            "skill": "to-plan",
            "staged_path": "/workspace/.agents/skills/to-plan/SKILL.md",
            "staged_relative_path": ".agents/skills/to-plan/SKILL.md",
            "status": "valid",
        }]}
        def item(event_type, status, exit_code):
            result = record("case:forced", "forced", True, target=("to-plan",), reported=("to-plan",), preflight=preflight)
            result["subject"] = {"events": [{"type": event_type, "item": {"type": "command_execution", "status": status, "exit_code": exit_code, "command": "cat .agents/skills/to-plan/SKILL.md"}}]}
            complete_read_evidence(result)
            return result

        self.assertEqual("invocation_failure", forced_integrity_status(item("item.started", "in_progress", None)))
        self.assertEqual("invocation_failure", forced_integrity_status(item("item.completed", "failed", 1)))
        successful_unreported = item("item.completed", "completed", 0)
        successful_unreported["reported_skills"] = []
        self.assertEqual("reporting_failure", forced_integrity_status(successful_unreported))
        self.assertEqual("valid", forced_integrity_status(item("item.completed", "completed", 0)))

    def test_excludes_unloaded_forced_targets_from_behavioral_evidence(self):
        records = [
            record("one:none", "none", False),
            record(
                "one:forced",
                "forced",
                True,
                target=("to-plan",),
            ),
            record("one:automatic", "automatic", True),
        ]

        score = compute_scorecard(records)

        self.assertIsNone(score.outcome_rates["forced"])
        self.assertIsNone(score.forced_uplift)
        self.assertIsNone(score.automatic_retention)
        self.assertEqual(1, score.invalid_forced_count)
        self.assertEqual(("one:forced",), score.invalid_forced_record_ids)
        self.assertEqual(0, score.efficiency["forced"].runs)
        self.assertFalse(score.gates["forced_integrity"])

    def test_counts_forced_negative_control_when_it_reports_its_target(self):
        preflight = {"valid": True, "targets": [{
            "skill": "to-plan",
            "staged_path": "/workspace/.agents/skills/to-plan/SKILL.md",
            "staged_relative_path": ".agents/skills/to-plan/SKILL.md",
            "status": "valid",
        }]}
        forced = record(
            "negative:forced", "forced", True, kind="negative",
            target=("to-plan",), reported=("to-plan",), preflight=preflight,
        )
        forced["subject"] = {"events": [{
            "type": "item.completed",
            "item": {
                "type": "command_execution", "status": "completed",
                "exit_code": 0,
                "command": "cat .agents/skills/to-plan/SKILL.md",
            },
        }]}
        complete_read_evidence(forced)
        score = compute_scorecard([forced])

        self.assertEqual(0, score.invalid_forced_count)
        self.assertEqual(1.0, score.negative_rates["forced"])
        self.assertTrue(score.gates["forced_integrity"])

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

    def test_explicit_only_skills_are_excluded_from_automatic_metrics(self):
        score = compute_scorecard(
            [
                record("one:none", "none", False),
                record("one:forced", "forced", True),
                record(
                    "one:automatic",
                    "automatic",
                    True,
                    safety=True,
                    automatic_eligible=False,
                ),
            ]
        )

        self.assertIsNone(score.outcome_rates["automatic"])
        self.assertIsNone(score.routing_precision)
        self.assertIsNone(score.automatic_retention)
        self.assertEqual(0, score.forbidden_action_failures)
        self.assertTrue(score.gates["forbidden_actions"])

    def test_legacy_automatic_records_fail_closed_until_reconciled(self):
        legacy = record("one:automatic", "automatic", True)
        del legacy["automatic_eligible"]

        score = compute_scorecard([legacy])

        self.assertIsNone(score.outcome_rates["automatic"])
        self.assertIsNone(score.routing_precision)

    def test_automatic_comparators_exclude_explicit_only_cases(self):
        records = [
            record(
                "automatic-positive:none",
                "none",
                False,
                automatic_eligible=True,
            ),
            record(
                "automatic-positive:forced",
                "forced",
                True,
                automatic_eligible=True,
            ),
            record(
                "automatic-positive:automatic",
                "automatic",
                True,
                automatic_eligible=True,
            ),
            record(
                "explicit-positive:none",
                "none",
                True,
                automatic_eligible=False,
            ),
            record(
                "explicit-positive:forced",
                "forced",
                False,
                automatic_eligible=False,
            ),
            record(
                "automatic-negative:none",
                "none",
                True,
                kind="negative",
                automatic_eligible=True,
            ),
            record(
                "automatic-negative:forced",
                "forced",
                True,
                kind="negative",
                automatic_eligible=True,
            ),
            record(
                "automatic-negative:automatic",
                "automatic",
                True,
                kind="negative",
                automatic_eligible=True,
            ),
            record(
                "explicit-negative:none",
                "none",
                True,
                kind="negative",
                automatic_eligible=False,
            ),
            record(
                "explicit-negative:forced",
                "forced",
                False,
                kind="negative",
                automatic_eligible=False,
            ),
        ]

        score = compute_scorecard(records)

        self.assertEqual(0.0, score.outcome_rates["none"])
        self.assertEqual(1.0, score.outcome_rates["forced"])
        self.assertEqual(1.0, score.automatic_retention)
        self.assertEqual(1.0, score.negative_rates["none"])
        self.assertEqual(1.0, score.negative_rates["forced"])
        self.assertTrue(score.gates["negative_controls"])

    def test_automatic_efficiency_comparators_exclude_explicit_only_cases(self):
        def with_telemetry(item, tokens):
            item["subject"] = {
                "usage": {"input_tokens": tokens - 1, "output_tokens": 1},
                "events": [{"type": "turn.completed"}],
                "elapsed_seconds": 1.0,
            }
            return item

        records = [
            with_telemetry(
                record(
                    "automatic:none",
                    "none",
                    True,
                    automatic_eligible=True,
                ),
                10,
            ),
            with_telemetry(
                record(
                    "automatic:forced",
                    "forced",
                    True,
                    automatic_eligible=True,
                ),
                20,
            ),
            with_telemetry(
                record(
                    "automatic:automatic",
                    "automatic",
                    True,
                    automatic_eligible=True,
                ),
                30,
            ),
            with_telemetry(
                record(
                    "explicit:none",
                    "none",
                    True,
                    expected=("implement-with-subagents",),
                    automatic_eligible=False,
                ),
                100,
            ),
            with_telemetry(
                record(
                    "explicit:forced",
                    "forced",
                    True,
                    expected=("implement-with-subagents",),
                    automatic_eligible=False,
                ),
                200,
            ),
        ]

        score = compute_scorecard(records)

        self.assertEqual(1, score.efficiency["none"].runs)
        self.assertEqual(10.0, score.efficiency["none"].total_tokens)
        self.assertEqual(1, score.efficiency["forced"].runs)
        self.assertEqual(20.0, score.efficiency["forced"].total_tokens)
        self.assertEqual(1, score.efficiency["automatic"].runs)
        self.assertEqual(30.0, score.efficiency["automatic"].total_tokens)
        explicit = score.skill_efficiency["implement-with-subagents"]
        self.assertEqual(0, explicit["none"].runs)
        self.assertEqual(0, explicit["automatic"].runs)

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
