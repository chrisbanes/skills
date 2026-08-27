from __future__ import annotations

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
    efficiency: dict[str, EfficiencyMetrics]
    skill_efficiency: dict[str, dict[str, EfficiencyMetrics]]
    gates: dict[str, bool]


def _rate(records: list[dict[str, Any]]) -> float | None:
    if not records:
        return None
    return sum(bool(record.get("outcome_pass")) for record in records) / len(records)


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
    positive = [record for record in records if record.get("kind") != "negative"]
    negative = [record for record in records if record.get("kind") == "negative"]
    outcome_rates = {
        arm: _rate([record for record in positive if record.get("arm") == arm])
        for arm in arms
    }
    negative_rates = {
        arm: _rate([record for record in negative if record.get("arm") == arm])
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
    automatic_records = [record for record in records if record.get("arm") == "automatic"]
    routing_precision, routing_recall = _routing_metrics(automatic_records)
    router_report_rate = (
        sum(bool(record.get("reported_router")) for record in automatic_records)
        / len(automatic_records)
        if automatic_records
        else None
    )
    forbidden_failures = sum(
        bool(record.get("forbidden_action_failure")) for record in records
    )
    efficiency = {
        arm: _efficiency_metrics(
            [record for record in records if record.get("arm") == arm]
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
                    if record.get("arm") == arm and skill in _target_skills(record)
                ]
            )
            for arm in ("none", "automatic")
        }
        for skill in target_skills
    }
    gates = {
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
        efficiency=efficiency,
        skill_efficiency=skill_efficiency,
        gates=gates,
    )
