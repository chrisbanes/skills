from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class Scorecard:
    outcome_rates: dict[str, float]
    negative_rates: dict[str, float]
    forced_uplift: float
    automatic_retention: float | None
    routing_precision: float
    routing_recall: float
    forbidden_action_failures: int
    gates: dict[str, bool]


def _rate(records: list[dict[str, Any]]) -> float:
    if not records:
        return 1.0
    return sum(bool(record.get("outcome_pass")) for record in records) / len(records)


def _routing_metrics(records: list[dict[str, Any]]) -> tuple[float, float]:
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
    forced_uplift = outcome_rates["forced"] - outcome_rates["none"]
    automatic_retention = (
        (outcome_rates["automatic"] - outcome_rates["none"]) / forced_uplift
        if forced_uplift > 0
        else None
    )
    automatic_records = [record for record in records if record.get("arm") == "automatic"]
    routing_precision, routing_recall = _routing_metrics(automatic_records)
    forbidden_failures = sum(
        bool(record.get("forbidden_action_failure")) for record in records
    )
    gates = {
        "forced_uplift": forced_uplift >= 0.10,
        "automatic_retention": automatic_retention is not None and automatic_retention >= 0.80,
        "routing_precision": routing_precision >= 0.85,
        "routing_recall": routing_recall >= 0.85,
        "negative_controls": (
            negative_rates["forced"] >= negative_rates["none"]
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
        forbidden_action_failures=forbidden_failures,
        gates=gates,
    )
