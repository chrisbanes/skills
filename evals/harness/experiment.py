from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL, EvalCase
from evals.harness.codex import ARMS, RunConfig, SubjectResult, run_subject
from evals.harness.grade import ObjectiveGrade, grade_subject
from evals.harness.judge import (
    JudgeConfig,
    JudgeResult,
    build_judge_packet,
    judge_covers_rubric,
    judge_output_valid,
    run_judge,
)
from evals.harness.report import write_reports
from evals.harness.results import (
    load_result,
    result_fingerprint,
    run_with_one_retry,
    write_result,
)
from evals.harness.score import compute_scorecard


def filter_cases(
    cases: Iterable[EvalCase], *, case_ids: list[str] | None, skills: list[str] | None
) -> list[EvalCase]:
    selected = list(cases)
    if case_ids:
        requested = set(case_ids)
        selected = [case for case in selected if case.id in requested]
        missing = requested - {case.id for case in selected}
        if missing:
            raise ValueError(f"unknown cases: {sorted(missing)}")
    if skills:
        requested_skills = set(skills)
        selected = [case for case in selected if requested_skills & set(case.target_skills)]
        found = {skill for case in selected for skill in case.target_skills}
        missing_skills = requested_skills - found
        if missing_skills:
            raise ValueError(f"unknown or uncovered skills: {sorted(missing_skills)}")
    return selected


def experiment_plan(
    cases: list[EvalCase],
    *,
    arms: list[str],
    repetitions: int,
    model: str,
    reasoning: str,
    judge_model: str,
    judge_reasoning: str,
    execute: bool,
    subject_cost_per_call_usd: float | None = None,
    judge_cost_per_call_usd: float | None = None,
) -> dict[str, Any]:
    subject_calls = len(cases) * len(arms) * repetitions
    estimated_cost = (
        subject_calls * subject_cost_per_call_usd
        + subject_calls * judge_cost_per_call_usd
        if subject_cost_per_call_usd is not None
        and judge_cost_per_call_usd is not None
        else None
    )
    return {
        "case_count": len(cases),
        "case_ids": [case.id for case in cases],
        "arms": arms,
        "repetitions": repetitions,
        "subject_model": {"model": model, "reasoning": reasoning},
        "judge_model": {"model": judge_model, "reasoning": judge_reasoning},
        "subject_calls": subject_calls,
        "judge_calls": subject_calls,
        "total_calls": subject_calls * 2,
        "cost_assumptions_usd_per_call": {
            "subject": subject_cost_per_call_usd,
            "judge": judge_cost_per_call_usd,
        },
        "estimated_cost_usd": estimated_cost,
        "execute": execute,
        "notice": (
            "Live model calls are enabled."
            if execute
            else "Pass --execute to authorize the planned live model calls."
        ),
    }


def default_output_dir(repo_root: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return repo_root / ".scratch" / "skill-evals" / stamp


def next_attempt_workspace(condition_dir: Path) -> Path:
    attempt = 1
    while (condition_dir / f"attempt-{attempt}").exists():
        attempt += 1
    return condition_dir / f"attempt-{attempt}"


def _case_digest(case: EvalCase) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in case.directory.rglob("*") if path.is_file()):
        digest.update(path.relative_to(case.directory).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _command_output(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=True
    )
    return completed.stdout.strip()


def preflight(repo_root: Path, codex_executable: str) -> tuple[str, str]:
    codex_version = _command_output([codex_executable, "--version"], cwd=repo_root)
    skill_sha = _command_output(["git", "rev-parse", "HEAD"], cwd=repo_root)
    fixture = repo_root / "evals" / "fixtures" / "compose-jvm"
    _command_output(
        [str(fixture / "gradlew"), "--offline", "--no-scan", "test"], cwd=fixture
    )
    return codex_version, skill_sha


def _subject_output_valid(result: SubjectResult) -> bool:
    output = result.final_output
    skills = output.get("skills_used")
    evidence = output.get("evidence")
    return (
        result.returncode == 0
        and set(output) == {"summary", "skills_used", "evidence"}
        and isinstance(output.get("summary"), str)
        and isinstance(skills, list)
        and len(skills) == len(set(skills))
        and all(skill in {*COMPOSE_SKILLS, ROUTER_SKILL} for skill in skills)
        and isinstance(evidence, list)
        and all(isinstance(item, str) for item in evidence)
    )


def _judge_retryable(result: JudgeResult) -> bool:
    return result.returncode != 0 or not judge_output_valid(result.output)


def _validator_payload(grade: ObjectiveGrade) -> list[dict[str, Any]]:
    return [asdict(validator) for validator in grade.validators]


def _result_payload(
    case: EvalCase,
    arm: str,
    repetition: int,
    subject: SubjectResult,
    grade: ObjectiveGrade,
    judge: JudgeResult,
    *,
    subject_retries: int,
    judge_retries: int,
    codex_version: str,
    skill_sha: str,
    case_digest: str,
    fingerprint: str,
    run_config: RunConfig,
    judge_config: JudgeConfig,
) -> dict[str, Any]:
    judge_pass = (
        judge.returncode == 0
        and judge_covers_rubric(judge.output, case.rubric)
        and bool(judge.output.get("overall_pass"))
    )
    return {
        "id": f"{case.id}:{arm}:{repetition}",
        "case_id": case.id,
        "arm": arm,
        "repetition": repetition,
        "fingerprint": fingerprint,
        "case_digest": case_digest,
        "codex_version": codex_version,
        "skill_sha": skill_sha,
        "subject_model": {
            "model": run_config.model,
            "reasoning": run_config.reasoning,
        },
        "judge_model": {
            "model": judge_config.model,
            "reasoning": judge_config.reasoning,
        },
        "kind": case.kind,
        "task_mode": case.task_mode,
        "expected_skills": list(case.expected_skills),
        "reported_skills": [
            skill
            for skill in subject.final_output.get("skills_used", [])
            if skill in COMPOSE_SKILLS
        ],
        "reported_router": ROUTER_SKILL
        in subject.final_output.get("skills_used", []),
        "objective_pass": grade.objective_pass,
        "judge_pass": judge_pass,
        "outcome_pass": grade.objective_pass and judge_pass,
        "forbidden_action_failure": grade.forbidden_action_failure,
        "objective_failures": list(grade.objective_failures),
        "violations": list(grade.violations),
        "validators": _validator_payload(grade),
        "subject": {
            "command": list(subject.command),
            "events": list(subject.events),
            "returncode": subject.returncode,
            "final_output": subject.final_output,
            "usage": subject.usage,
            "changed_paths": list(subject.changed_paths),
            "diff": subject.diff,
            "elapsed_seconds": subject.elapsed_seconds,
            "stderr": subject.stderr,
            "retries": subject_retries,
        },
        "judge": {
            "returncode": judge.returncode,
            "output": judge.output,
            "elapsed_seconds": judge.elapsed_seconds,
            "stderr": judge.stderr,
            "retries": judge_retries,
        },
    }


def execute_experiment(
    repo_root: Path,
    cases: list[EvalCase],
    *,
    arms: list[str],
    repetitions: int,
    run_config: RunConfig,
    judge_config: JudgeConfig,
    output_dir: Path,
    codex_executable: str = "codex",
    audit_seed: int = 20260816,
) -> dict[str, Path]:
    codex_version, skill_sha = preflight(repo_root, codex_executable)
    records: list[dict[str, Any]] = []
    for case in cases:
        for arm in arms:
            for repetition in range(1, repetitions + 1):
                fingerprint = result_fingerprint(
                    case_digest=_case_digest(case),
                    arm=arm,
                    skill_sha=skill_sha,
                    codex_version=codex_version,
                    model=run_config.model,
                    reasoning=run_config.reasoning,
                    judge_model=judge_config.model,
                    judge_reasoning=judge_config.reasoning,
                )
                result_path = output_dir / "raw" / case.id / arm / f"{repetition}.json"
                if result_path.is_file():
                    records.append(load_result(result_path, fingerprint))
                    continue

                def run_subject_attempt() -> SubjectResult:
                    condition_dir = (
                        output_dir
                        / "workspaces"
                        / case.id
                        / arm
                        / str(repetition)
                    )
                    workspace = next_attempt_workspace(condition_dir)
                    return run_subject(
                        case,
                        arm,
                        repo_root,
                        workspace,
                        run_config,
                        codex_executable=codex_executable,
                    )

                subject, subject_retries = run_with_one_retry(
                    run_subject_attempt, lambda result: not _subject_output_valid(result)
                )
                grade = grade_subject(case, subject)
                packet = build_judge_packet(case, subject, grade)
                packet_path = (
                    output_dir
                    / "judge-packets"
                    / f"{packet['candidate_id']}-{repetition}.json"
                )
                packet_path.parent.mkdir(parents=True, exist_ok=True)
                packet_path.write_text(
                    json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )

                judge, judge_retries = run_with_one_retry(
                    lambda: run_judge(
                        packet_path,
                        repo_root,
                        judge_config,
                        codex_executable=codex_executable,
                    ),
                    lambda result: _judge_retryable(result)
                    or not judge_covers_rubric(result.output, case.rubric),
                )
                payload = _result_payload(
                    case,
                    arm,
                    repetition,
                    subject,
                    grade,
                    judge,
                    subject_retries=subject_retries,
                    judge_retries=judge_retries,
                    codex_version=codex_version,
                    skill_sha=skill_sha,
                    case_digest=_case_digest(case),
                    fingerprint=fingerprint,
                    run_config=run_config,
                    judge_config=judge_config,
                )
                write_result(result_path, fingerprint, payload)
                records.append(payload)

    return write_reports(output_dir, records, compute_scorecard(records), seed=audit_seed)


def load_raw_records(output_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((output_dir / "raw").glob("*/*/*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        payload = document.get("payload")
        if isinstance(payload, dict):
            records.append(payload)
    return records


def rejudge_packets(
    repo_root: Path,
    output_dir: Path,
    judge_config: JudgeConfig,
    *,
    execute: bool,
    codex_executable: str = "codex",
) -> dict[str, Any]:
    packets = sorted((output_dir / "judge-packets").glob("*.json"))
    plan = {"packet_count": len(packets), "judge_calls": len(packets), "execute": execute}
    if not execute:
        return plan
    completed = 0
    for packet_path in packets:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        rubric = tuple(packet.get("rubric", ()))
        fingerprint = hashlib.sha256(
            packet_path.read_bytes()
            + json.dumps(asdict(judge_config), sort_keys=True).encode()
        ).hexdigest()
        result_path = output_dir / "rejudgments" / f"{packet_path.stem}.json"
        if result_path.is_file():
            load_result(result_path, fingerprint)
            completed += 1
            continue
        judgment, retries = run_with_one_retry(
            lambda: run_judge(
                packet_path,
                repo_root,
                judge_config,
                codex_executable=codex_executable,
            ),
            lambda result: _judge_retryable(result)
            or not judge_covers_rubric(result.output, rubric),
        )
        write_result(
            result_path,
            fingerprint,
            {
                "candidate_id": packet.get("candidate_id"),
                "judge_model": {
                    "model": judge_config.model,
                    "reasoning": judge_config.reasoning,
                },
                "judge": {
                    "returncode": judgment.returncode,
                    "output": judgment.output,
                    "stderr": judgment.stderr,
                    "elapsed_seconds": judgment.elapsed_seconds,
                    "retries": retries,
                },
            },
        )
        completed += 1
    return {**plan, "completed": completed}
