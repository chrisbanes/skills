from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


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
    gates: dict[str, bool]


def _rate(records: list[dict[str, Any]]) -> float | None:
    if not records:
        return None
    return sum(bool(record.get("outcome_pass")) for record in records) / len(records)


def _routing_metrics(records: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if not records:
        return None, None
    true_positive = false_positive = false_negative = 0
    for record in records:
        expected = set(record.get("expected_skills", []))
        reported = set(record.get("reported_skills", []))
        true_positive += len(expected & reported)
        false_positive += len(reported - expected)
        false_negative += len(expected - reported)
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    precision = true_positive / precision_denominator if precision_denominator else 1.0
    recall = true_positive / recall_denominator if recall_denominator else 1.0
    return precision, recall


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
        gates=gates,
    )
