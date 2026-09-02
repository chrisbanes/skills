from __future__ import annotations

import json
import math
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from evals.harness.codex import completed_tool_call_count
from evals.harness.score import Scorecard, is_measured_in_arm
from evals.harness.suites import SUITES


def build_audit_queue(
    records: Iterable[dict[str, Any]], *, seed: int
) -> list[dict[str, Any]]:
    records = list(records)
    reasons: dict[str, set[str]] = {}
    by_condition: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        record_id = str(record["id"])
        if record.get("objective_pass") != record.get("judge_pass"):
            reasons.setdefault(record_id, set()).add("judge-objective-disagreement")
        key = (str(record.get("case_id")), str(record.get("arm")))
        by_condition.setdefault(key, []).append(record)
    for condition in by_condition.values():
        outcomes = {bool(record.get("judge_pass")) for record in condition}
        if len(outcomes) > 1:
            for record in condition:
                reasons.setdefault(str(record["id"]), set()).add(
                    "within-condition-inconsistency"
                )

    remaining = [record for record in records if str(record["id"]) not in reasons]
    sample_size = math.ceil(len(remaining) * 0.10)
    if sample_size:
        for record in random.Random(seed).sample(remaining, sample_size):
            reasons.setdefault(str(record["id"]), set()).add("seeded-sample")

    by_id = {str(record["id"]): record for record in records}
    return [
        {
            "id": record_id,
            "case_id": by_id[record_id].get("case_id"),
            "arm": by_id[record_id].get("arm"),
            "repetition": by_id[record_id].get("repetition"),
            "reasons": sorted(record_reasons),
            "decision": None,
        }
        for record_id, record_reasons in sorted(reasons.items())
    ]


def _percent(value: float | None) -> str:
    return "not met" if value is None else f"{value * 100:.1f}%"


def _measurement(value: float | None, *, suffix: str = "") -> str:
    if value is None:
        return "unavailable"
    rendered = f"{value:.1f}"
    return f"{rendered}{suffix}"


def _count(value: float | None) -> str:
    if value is None:
        return "unavailable"
    return str(int(value)) if value.is_integer() else f"{value:.1f}"


def _tokens(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if abs(value) < 1000:
        return _count(value)
    return f"{value / 1000:.1f}k"


def _seconds(value: float | None) -> str:
    return _measurement(value, suffix="s")


def _total(value: int | None) -> str:
    return "unavailable" if value is None else str(value)


def _comparison(
    baseline: float | None,
    automatic: float | None,
    formatter: Callable[[float | None], str],
) -> str:
    if baseline is None or automatic is None or baseline == 0:
        change = "n/a"
    else:
        change = f"{(automatic - baseline) / baseline:+.0%}"
    return f"{formatter(baseline)} → {formatter(automatic)} ({change})"


def _outcome_rate(records: list[dict[str, Any]], arm: str) -> float | None:
    selected = [
        record
        for record in records
        if record.get("arm") == arm
        and is_measured_in_arm(record, arm)
    ]
    if not selected:
        return None
    return sum(bool(record.get("outcome_pass")) for record in selected) / len(selected)


def _target_skills(record: dict[str, Any]) -> list[str]:
    skills = record.get("target_skills")
    if not isinstance(skills, list):
        skills = record.get("expected_skills", [])
    return [str(skill) for skill in skills]


def _per_arm_record_count(records: list[dict[str, Any]]) -> str:
    counts = {
        arm: sum(
            record.get("arm") == arm
            and is_measured_in_arm(record, arm)
            for record in records
        )
        for arm in ("none", "forced", "automatic")
        if any(record.get("arm") == arm for record in records)
    }
    if not counts:
        return "0"
    if len(set(counts.values())) == 1:
        return str(next(iter(counts.values())))
    return ", ".join(f"{arm}={count}" for arm, count in counts.items())


def _role_attempts(
    record: dict[str, Any], role: str
) -> list[dict[str, Any]] | None:
    payload = record.get(role)
    if not isinstance(payload, dict):
        return []
    attempts = payload.get("attempts")
    if attempts is not None:
        if isinstance(attempts, list) and attempts and all(
            isinstance(attempt, dict) for attempt in attempts
        ):
            return attempts
        return None
    retries = payload.get("retries", 0)
    if isinstance(retries, int) and not isinstance(retries, bool) and retries > 0:
        return None
    return [payload]


def _tool_event_count(records: Iterable[dict[str, Any]]) -> int | None:
    count = 0
    for record in records:
        for role in ("subject", "judge"):
            attempts = _role_attempts(record, role)
            if attempts is None:
                return None
            for attempt in attempts:
                tool_calls = attempt.get("tool_calls")
                if isinstance(tool_calls, int) and not isinstance(tool_calls, bool):
                    count += tool_calls
                    continue
                events = attempt.get("events", [])
                if isinstance(events, list):
                    count += completed_tool_call_count(events)
    return count


def render_scorecard(
    score: Scorecard, records: Iterable[dict[str, Any]] = ()
) -> str:
    records = list(records)
    attempt_groups = [
        _role_attempts(record, role)
        for record in records
        for role in ("subject", "judge")
    ]
    attempts_complete = all(attempts is not None for attempts in attempt_groups)
    attempts = [
        attempt
        for group in attempt_groups
        if group is not None
        for attempt in group
    ]
    input_tokens = (
        sum(
            int(attempt.get("usage", {}).get("input_tokens", 0))
            for attempt in attempts
        )
        if attempts_complete
        else None
    )
    output_tokens = (
        sum(
            int(attempt.get("usage", {}).get("output_tokens", 0))
            for attempt in attempts
        )
        if attempts_complete
        else None
    )
    elapsed = (
        sum(float(attempt.get("elapsed_seconds", 0.0)) for attempt in attempts)
        if attempts_complete
        else None
    )
    retries = sum(
        int(record.get(role, {}).get("retries", 0))
        for record in records
        for role in ("subject", "judge")
    )
    process_failures = (
        sum(int(attempt.get("returncode", 0) != 0) for attempt in attempts)
        if attempts_complete
        else None
    )
    suites = {str(record.get("suite")) for record in records if record.get("suite")}
    suite_name = (
        SUITES[next(iter(suites))].title
        if len(suites) == 1 and next(iter(suites)) in SUITES
        else "Repository"
    )
    lines = [
        f"# Advisory {suite_name} Skill Scorecard",
        "",
        "> This experiment is not a merge or release gate.",
        "",
        "## Outcome pass rates",
        "",
        "| Arm | Positive cases | Negative controls |",
        "| --- | ---: | ---: |",
    ]
    for arm in ("none", "forced", "automatic"):
        lines.append(
            f"| {arm} | {_percent(score.outcome_rates[arm])} | {_percent(score.negative_rates[arm])} |"
        )
    skills = sorted(
        {
            str(skill)
            for record in records
            for skill in _target_skills(record)
        }
    )
    if skills:
        lines.extend(
            [
                "",
                "## Per-skill diagnostics",
                "",
                "| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for skill in skills:
            skill_records = [
                record
                for record in records
                if skill in _target_skills(record)
            ]
            positive = [
                record for record in skill_records if record.get("kind") != "negative"
            ]
            negative = [
                record for record in skill_records if record.get("kind") == "negative"
            ]
            baseline = _outcome_rate(positive, "none")
            forced = _outcome_rate(positive, "forced")
            automatic = _outcome_rate(positive, "automatic")
            uplift = (
                forced - baseline
                if forced is not None and baseline is not None
                else None
            )
            per_arm_count = _per_arm_record_count(positive)
            lines.append(
                f"| `{skill}` | {per_arm_count} | {_percent(baseline)} | "
                f"{_percent(forced)} | {_percent(automatic)} | {_percent(uplift)} | "
                f"{_percent(_outcome_rate(negative, 'forced'))} | "
                f"{_percent(_outcome_rate(negative, 'automatic'))} |"
            )
    lines.extend(
        [
            "",
            "## Effect and routing",
            "",
            f"- Forced uplift: {_percent(score.forced_uplift)}",
            f"- Automatic retention: {_percent(score.automatic_retention)}",
            f"- Reported automatic routing precision: {_percent(score.routing_precision)}",
            f"- Reported automatic routing recall: {_percent(score.routing_recall)}",
            f"- Router reported in automatic arm: {_percent(score.router_report_rate)}",
            f"- Forbidden-action failures: {score.forbidden_action_failures}",
            "",
            "## Efficiency (non-gating)",
            "",
            "Subject-only metrics. Medians describe a typical run, including any retry. "
            "Per-pass totals include failed runs, so a quick incorrect result is not rewarded.",
            "",
            "| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for arm in ("none", "forced", "automatic"):
        efficiency = score.efficiency[arm]
        lines.append(
            f"| {arm} | {efficiency.outcome_passes} / {efficiency.runs} | "
            f"{_tokens(efficiency.median_tokens_per_run)} | "
            f"{_count(efficiency.median_tool_calls_per_run)} | "
            f"{_count(efficiency.median_turns_per_run)} | "
            f"{_seconds(efficiency.median_elapsed_seconds_per_run)} | "
            f"{_tokens(efficiency.tokens_per_outcome_pass)} | "
            f"{_count(efficiency.tool_calls_per_outcome_pass)} | "
            f"{_count(efficiency.turns_per_outcome_pass)} | "
            f"{_seconds(efficiency.elapsed_seconds_per_outcome_pass)} |"
        )
    measured_skills = [
        (skill, by_arm)
        for skill, by_arm in sorted(score.skill_efficiency.items())
        if by_arm["none"].runs or by_arm["automatic"].runs
    ]
    if measured_skills:
        lines.extend(
            [
                "",
                "## Per-skill efficiency (baseline vs automatic)",
                "",
                "Subject-only per-run medians, baseline → automatic. Parentheses "
                "show the automatic change from baseline. Multi-skill scenarios "
                "contribute to every targeted skill row.",
                "",
                "| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for skill, by_arm in measured_skills:
            baseline = by_arm["none"]
            automatic = by_arm["automatic"]
            lines.append(
                f"| `{skill}` | "
                f"{_comparison(baseline.median_tokens_per_run, automatic.median_tokens_per_run, _tokens)} | "
                f"{_comparison(baseline.median_tool_calls_per_run, automatic.median_tool_calls_per_run, _count)} | "
                f"{_comparison(baseline.median_turns_per_run, automatic.median_turns_per_run, _count)} | "
                f"{_comparison(baseline.median_elapsed_seconds_per_run, automatic.median_elapsed_seconds_per_run, _seconds)} |"
            )
    lines.extend(
        [
            "",
            "Token counts are Codex input plus output tokens. Tool calls count completed "
            "command, file-change, MCP, web-search, and generic tool events. Wall-clock "
            "time is environment-sensitive.",
            "",
            "## Evaluation diagnostics (non-gating)",
            "",
            f"- Input tokens: {_total(input_tokens)}",
            f"- Output tokens: {_total(output_tokens)}",
            f"- Tool events: {_total(_tool_event_count(records))}",
            f"- Elapsed time: {_seconds(elapsed)}",
            f"- Process failures: {_total(process_failures)}",
            f"- Retries: {retries}",
            "",
            "## Gates",
            "",
        ]
    )
    for name, passed in score.gates.items():
        lines.append(f"- {name}: {'PASS' if passed else 'NOT MET'}")
    return "\n".join(lines) + "\n"


def append_audit_decision(
    path: Path, record_id: str, decision: str, rationale: str
) -> None:
    if not record_id.strip() or not decision.strip() or not rationale.strip():
        raise ValueError("audit decision fields must be non-empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": record_id,
        "decision": decision,
        "rationale": rationale,
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, sort_keys=True) + "\n")


def write_reports(
    output_dir: Path,
    records: list[dict[str, Any]],
    score: Scorecard,
    *,
    seed: int,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "results": output_dir / "results.json",
        "scorecard": output_dir / "scorecard.md",
        "audit_queue": output_dir / "audit-queue.json",
    }
    paths["results"].write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    paths["scorecard"].write_text(render_scorecard(score, records), encoding="utf-8")
    paths["audit_queue"].write_text(
        json.dumps(build_audit_queue(records, seed=seed), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths
