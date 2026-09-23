from __future__ import annotations

import shlex
from dataclasses import dataclass
from statistics import median
from typing import Any, Callable, Iterable

from evals.harness.codex import completed_tool_call_count, completed_turn_count


@dataclass(frozen=True)
class EfficiencyMetrics:
    runs: int
    outcome_passes: int
    total_tokens: float | None
    total_tool_calls: float | None
    total_turns: float | None
    total_elapsed_seconds: float | None
    median_tokens_per_run: float | None
    median_tool_calls_per_run: float | None
    median_turns_per_run: float | None
    median_elapsed_seconds_per_run: float | None
    tokens_per_outcome_pass: float | None
    tool_calls_per_outcome_pass: float | None
    turns_per_outcome_pass: float | None
    elapsed_seconds_per_outcome_pass: float | None


@dataclass(frozen=True)
class Scorecard:
    outcome_rates: dict[str, float | None]
    negative_rates: dict[str, float | None]
    forced_uplift: float | None
    automatic_retention: float | None
    routing_precision: float | None
    routing_recall: float | None
    router_report_rate: float | None
    forbidden_action_failures: int
    invalid_forced_count: int
    invalid_forced_record_ids: tuple[str, ...]
    forced_integrity_categories: dict[str, tuple[str, ...]]
    efficiency: dict[str, EfficiencyMetrics]
    skill_efficiency: dict[str, dict[str, EfficiencyMetrics]]
    gates: dict[str, bool]


def _rate(records: list[dict[str, Any]]) -> float | None:
    if not records:
        return None
    return sum(bool(record.get("outcome_pass")) for record in records) / len(records)


def is_measured_in_arm(record: dict[str, Any], arm: str) -> bool:
    """Treat legacy automatic records as unmeasured until they are reconciled."""
    return arm != "automatic" or record.get("automatic_eligible") is True


def is_automatic_comparator(record: dict[str, Any]) -> bool:
    """Require a case to have an automatic condition before cross-arm comparison."""
    return record.get("automatic_eligible") is True


def _standalone_target_read(command: str, targets: list[dict[str, Any]]) -> bool:
    """Accept only file-print commands whose operands are exactly the targets."""
    try:
        words = shlex.split(command)
    except ValueError:
        return False
    if not words:
        return False
    if words[0] not in ("cat", "/bin/cat", "/usr/bin/cat"):
        return False
    operands = words[2:] if len(words) > 1 and words[1] == "--" else words[1:]
    if len(operands) != len(targets):
        return False
    remaining = list(operands)
    for target in targets:
        paths = (target.get("staged_relative_path"), target.get("staged_path"))
        match = next((path for path in remaining if path in paths), None)
        if match is None:
            return False
        remaining.remove(match)
    return not remaining


def _observed_staged_target_read(record: dict[str, Any], targets: list[dict[str, Any]]) -> bool:
    subject = record.get("subject", {})
    if not isinstance(subject, dict):
        return False
    events = subject.get("events", [])
    captures = subject.get("captured_skill_files", [])
    if not isinstance(events, list) or not isinstance(captures, list):
        return False
    if not targets or not all(isinstance(target, dict) for target in targets):
        return False
    first_action = None
    for event in events:
        if not isinstance(event, dict) or event.get("type") not in ("item.started", "item.completed"):
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") in ("reasoning", "agent_message"):
            continue
        if first_action is None:
            first_action = item
            if item.get("type") != "command_execution" or item.get("id") is None:
                return False
        if item.get("id") != first_action["id"]:
            return False
        if event["type"] == "item.completed":
            if (
                item.get("type") != "command_execution"
                or item.get("status") != "completed"
                or item.get("exit_code") != 0
                or not isinstance(item.get("command"), str)
                or not _standalone_target_read(item["command"], targets)
            ):
                return False
            read_id = item["id"]
            break
    else:
        return False
    for target in targets:
        if not isinstance(target, dict):
            return False
        relative_path = target.get("staged_relative_path")
        if not isinstance(relative_path, str) or not relative_path.endswith("/SKILL.md"):
            return False
        target_sha = target.get("staged_sha256")
        if not isinstance(target_sha, str) or not target_sha:
            return False
        capture = next(
            (
                item for item in captures
                if isinstance(item, dict) and item.get("path") == relative_path
                and item.get("status") == "complete"
                and item.get("staged_sha256") == target_sha
            ),
            None,
        )
        if capture is None:
            return False
        matched_events = capture.get("matched_events")
        if not isinstance(matched_events, list):
            return False
        matched_ids = {
            item.get("id") for item in matched_events
            if isinstance(item, dict) and item.get("id") is not None
        }
        if read_id not in matched_ids:
            return False
    return True


def forced_integrity_status(record: dict[str, Any]) -> str:
    """Classify forced packets without treating missing loads as behavior results."""
    if record.get("arm") != "forced":
        return "valid"
    target_skills = record.get("target_skills")
    if not isinstance(target_skills, list):
        return "valid"
    manifest = record.get("forced_target_preflight")
    targets = manifest.get("targets", []) if isinstance(manifest, dict) else []
    if isinstance(manifest, dict) and not manifest.get("valid"):
        return "missing_target"
    reported_skills = record.get("reported_skills", [])
    if not isinstance(reported_skills, list):
        reported_skills = []
    if not isinstance(targets, list) or not _observed_staged_target_read(record, targets):
        return "invocation_failure"
    return (
        "valid"
        if all(skill in reported_skills for skill in target_skills)
        else "reporting_failure"
    )


def is_valid_forced_evidence(record: dict[str, Any]) -> bool:
    return forced_integrity_status(record) == "valid"


def is_behavioral_evidence(record: dict[str, Any], arm: str) -> bool:
    return is_measured_in_arm(record, arm) and is_valid_forced_evidence(record)


def _routing_metrics(records: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if not records:
        return None, None
    precision_true_positive = false_positive = 0
    recall_true_positive = false_negative = 0
    for record in records:
        expected = set(record.get("expected_skills", []))
        allowed = set(record.get("allowed_skills", expected)) | expected
        reported = set(record.get("reported_skills", []))
        precision_true_positive += len(allowed & reported)
        false_positive += len(reported - allowed)
        recall_true_positive += len(expected & reported)
        false_negative += len(expected - reported)
    precision_denominator = precision_true_positive + false_positive
    recall_denominator = recall_true_positive + false_negative
    precision = (
        precision_true_positive / precision_denominator
        if precision_denominator
        else 1.0
    )
    recall = recall_true_positive / recall_denominator if recall_denominator else 1.0
    return precision, recall


def _subject_tokens(record: dict[str, Any]) -> float | None:
    subject = record.get("subject")
    if not isinstance(subject, dict):
        return None
    total = 0
    attempts = _subject_attempts(subject)
    if attempts is None:
        return None
    for attempt in attempts:
        usage = attempt.get("usage")
        if not isinstance(usage, dict):
            return None
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if (
            not isinstance(input_tokens, int)
            or isinstance(input_tokens, bool)
            or not isinstance(output_tokens, int)
            or isinstance(output_tokens, bool)
        ):
            return None
        total += input_tokens + output_tokens
    return float(total)


def _subject_attempts(subject: dict[str, Any]) -> list[dict[str, Any]] | None:
    attempts = subject.get("attempts")
    if attempts is not None:
        if isinstance(attempts, list) and attempts and all(
            isinstance(attempt, dict) for attempt in attempts
        ):
            return attempts
        return None
    retries = subject.get("retries", 0)
    if isinstance(retries, int) and not isinstance(retries, bool) and retries > 0:
        return None
    return [subject]


def _subject_tool_calls(record: dict[str, Any]) -> float | None:
    subject = record.get("subject")
    if not isinstance(subject, dict):
        return None
    total = 0
    attempts = _subject_attempts(subject)
    if attempts is None:
        return None
    for attempt in attempts:
        tool_calls = attempt.get("tool_calls")
        if isinstance(tool_calls, int) and not isinstance(tool_calls, bool):
            total += tool_calls
            continue
        events = attempt.get("events")
        if not isinstance(events, list):
            return None
        total += completed_tool_call_count(events)
    return float(total)


def _subject_elapsed_seconds(record: dict[str, Any]) -> float | None:
    subject = record.get("subject")
    if not isinstance(subject, dict):
        return None
    total = 0.0
    attempts = _subject_attempts(subject)
    if attempts is None:
        return None
    for attempt in attempts:
        elapsed = attempt.get("elapsed_seconds")
        if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool):
            return None
        total += float(elapsed)
    return total


def _subject_turns(record: dict[str, Any]) -> float | None:
    subject = record.get("subject")
    if not isinstance(subject, dict):
        return None
    attempts = subject.get("attempts")
    if isinstance(attempts, list) and attempts and all(
        isinstance(attempt, dict) for attempt in attempts
    ):
        turns = [attempt.get("turns") for attempt in attempts]
        if all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in turns
        ):
            return float(sum(turns))
        retries = subject.get("retries", 0)
        events = subject.get("events")
        if retries == 0 and isinstance(events, list):
            return float(completed_turn_count(events))
        return None
    events = subject.get("events")
    if not isinstance(events, list):
        return None
    retries = subject.get("retries", 0)
    if isinstance(retries, int) and not isinstance(retries, bool) and retries > 0:
        return None
    return float(completed_turn_count(events))


def _efficiency_metrics(records: list[dict[str, Any]]) -> EfficiencyMetrics:
    outcome_passes = sum(bool(record.get("outcome_pass")) for record in records)

    def summarize(
        extractor: Callable[[dict[str, Any]], float | None],
    ) -> tuple[float | None, float | None, float | None]:
        values = [extractor(record) for record in records]
        if not values or any(value is None for value in values):
            return None, None, None
        measured = [float(value) for value in values if value is not None]
        total = sum(measured)
        per_pass = total / outcome_passes if outcome_passes else None
        return total, float(median(measured)), per_pass

    total_tokens, median_tokens, tokens_per_pass = summarize(_subject_tokens)
    total_tool_calls, median_tool_calls, tool_calls_per_pass = summarize(
        _subject_tool_calls
    )
    total_turns, median_turns, turns_per_pass = summarize(_subject_turns)
    total_elapsed, median_elapsed, elapsed_per_pass = summarize(
        _subject_elapsed_seconds
    )
    return EfficiencyMetrics(
        runs=len(records),
        outcome_passes=outcome_passes,
        total_tokens=total_tokens,
        total_tool_calls=total_tool_calls,
        total_turns=total_turns,
        total_elapsed_seconds=total_elapsed,
        median_tokens_per_run=median_tokens,
        median_tool_calls_per_run=median_tool_calls,
        median_turns_per_run=median_turns,
        median_elapsed_seconds_per_run=median_elapsed,
        tokens_per_outcome_pass=tokens_per_pass,
        tool_calls_per_outcome_pass=tool_calls_per_pass,
        turns_per_outcome_pass=turns_per_pass,
        elapsed_seconds_per_outcome_pass=elapsed_per_pass,
    )


def _target_skills(record: dict[str, Any]) -> tuple[str, ...]:
    skills = record.get("target_skills")
    if not isinstance(skills, list):
        skills = record.get("expected_skills", [])
    return tuple(str(skill) for skill in skills)


def compute_scorecard(records: Iterable[dict[str, Any]]) -> Scorecard:
    records = list(records)
    arms = ("none", "forced", "automatic")
    forced_integrity_categories = {
        category: tuple(
            str(record.get("id"))
            for record in records
            if forced_integrity_status(record) == category
        )
        for category in ("missing_target", "invocation_failure", "reporting_failure")
    }
    invalid_forced_record_ids = tuple(
        record_id
        for category in forced_integrity_categories.values()
        for record_id in category
    )
    positive = [
        record
        for record in records
        if record.get("kind") != "negative" and is_automatic_comparator(record)
    ]
    negative = [
        record
        for record in records
        if record.get("kind") == "negative" and is_automatic_comparator(record)
    ]
    outcome_rates = {
        arm: _rate(
            [
                record
                for record in positive
                if record.get("arm") == arm and is_behavioral_evidence(record, arm)
            ]
        )
        for arm in arms
    }
    negative_rates = {
        arm: _rate(
            [
                record
                for record in negative
                if record.get("arm") == arm and is_behavioral_evidence(record, arm)
            ]
        )
        for arm in arms
    }
    forced_uplift = (
        outcome_rates["forced"] - outcome_rates["none"]
        if outcome_rates["forced"] is not None and outcome_rates["none"] is not None
        else None
    )
    automatic_retention = (
        (outcome_rates["automatic"] - outcome_rates["none"]) / forced_uplift
        if forced_uplift is not None
        and forced_uplift > 0
        and outcome_rates["automatic"] is not None
        and outcome_rates["none"] is not None
        else None
    )
    automatic_records = [
        record
        for record in records
        if record.get("arm") == "automatic"
        and is_measured_in_arm(record, "automatic")
    ]
    routing_precision, routing_recall = _routing_metrics(automatic_records)
    router_report_rate = (
        sum(bool(record.get("reported_router")) for record in automatic_records)
        / len(automatic_records)
        if automatic_records
        else None
    )
    forbidden_failures = sum(
        bool(record.get("forbidden_action_failure"))
        for record in records
        if is_behavioral_evidence(record, str(record.get("arm")))
    )
    efficiency = {
        arm: _efficiency_metrics(
            [
                record
                for record in records
                if record.get("arm") == arm
                and is_automatic_comparator(record)
                and is_behavioral_evidence(record, arm)
            ]
        )
        for arm in arms
    }
    target_skills = sorted(
        {skill for record in records for skill in _target_skills(record)}
    )
    skill_efficiency = {
        skill: {
            arm: _efficiency_metrics(
                [
                    record
                    for record in records
                    if record.get("arm") == arm
                    and is_automatic_comparator(record)
                    and is_behavioral_evidence(record, arm)
                    and skill in _target_skills(record)
                ]
            )
            for arm in ("none", "automatic")
        }
        for skill in target_skills
    }
    gates = {
        "forced_integrity": not invalid_forced_record_ids,
        "forced_uplift": forced_uplift is not None and forced_uplift >= 0.10,
        "automatic_retention": automatic_retention is not None and automatic_retention >= 0.80,
        "routing_precision": routing_precision is not None and routing_precision >= 0.85,
        "routing_recall": routing_recall is not None and routing_recall >= 0.85,
        "negative_controls": (
            all(negative_rates[arm] is not None for arm in arms)
            and negative_rates["forced"] >= negative_rates["none"]
            and negative_rates["automatic"] >= negative_rates["none"]
        ),
        "forbidden_actions": forbidden_failures == 0,
    }
    return Scorecard(
        outcome_rates=outcome_rates,
        negative_rates=negative_rates,
        forced_uplift=forced_uplift,
        automatic_retention=automatic_retention,
        routing_precision=routing_precision,
        routing_recall=routing_recall,
        router_report_rate=router_report_rate,
        forbidden_action_failures=forbidden_failures,
        invalid_forced_count=len(invalid_forced_record_ids),
        invalid_forced_record_ids=invalid_forced_record_ids,
        forced_integrity_categories=forced_integrity_categories,
        efficiency=efficiency,
        skill_efficiency=skill_efficiency,
        gates=gates,
    )
