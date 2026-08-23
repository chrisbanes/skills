from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from evals.harness.cases import EvalCase
from evals.harness.codex import (
    ARMS,
    RunConfig,
    SubjectResult,
    discover_skill_paths,
    is_generated_skill_path,
    reported_skill_names,
    run_subject,
    subject_output_valid,
)
from evals.harness.grade import ObjectiveGrade, grade_subject
from evals.harness.judge import (
    JudgeConfig,
    JudgeResult,
    build_judge_packet,
    judge_covers_rubric,
    judge_output_valid,
    judge_passes_rubric,
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
from evals.harness.suites import PUBLIC_SKILLS, ROUTER_SKILL, suite_for_skills


RUN_CONTROL_FIELDS = (
    "suite",
    "codex_version",
    "skill_sha",
    "skill_catalog_digest",
    "subject_model",
    "judge_model",
)


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
    else:
        selected = [case for case in selected if not case.calibration]
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


def _judge_packet_path(
    output_dir: Path, candidate_id: str, fingerprint: str, repetition: int
) -> Path:
    return (
        output_dir
        / "judge-packets"
        / f"{candidate_id}-{fingerprint[:20]}-{repetition}.json"
    )


def _case_digest(case: EvalCase) -> str:
    digest = hashlib.sha256()
    repo_root = case.directory.parents[2]
    roots = (
        ("case", case.directory),
        ("fixture", repo_root / "evals" / "fixtures" / case.fixture),
    )
    for label, root in roots:
        for path in sorted(path for path in root.rglob("*") if path.is_file()):
            relative = path.relative_to(root)
            if label == "fixture" and {".gradle", "build"} & set(relative.parts):
                continue
            digest.update(label.encode())
            digest.update(b"\0")
            digest.update(relative.as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def _skill_catalog_digest(skill_paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in skill_paths:
        digest.update(str(path).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _skill_source_paths(repo_root: Path) -> tuple[Path, ...]:
    skill_dirs = (repo_root / "skills" / skill for skill in PUBLIC_SKILLS)
    return tuple(
        sorted(
            (
                path.resolve()
                for skill_dir in skill_dirs
                for path in skill_dir.rglob("*")
                if path.is_file()
                and not is_generated_skill_path(path, skill_dir)
            ),
            key=str,
        )
    )


def _command_output(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=True
    )
    return completed.stdout.strip()


def preflight(
    repo_root: Path, codex_executable: str, cases: Iterable[EvalCase]
) -> tuple[str, str]:
    codex_version = _command_output([codex_executable, "--version"], cwd=repo_root)
    skill_sha = _command_output(["git", "rev-parse", "HEAD"], cwd=repo_root)
    for fixture_name in sorted({case.fixture for case in cases}):
        fixture = repo_root / "evals" / "fixtures" / fixture_name
        wrapper = fixture / "gradlew"
        if wrapper.is_file():
            _command_output(
                [str(wrapper), "--offline", "--no-scan", "test"], cwd=fixture
            )
    return codex_version, skill_sha


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
    skill_paths: tuple[Path, ...],
    skill_sources: tuple[Path, ...],
    skill_catalog_digest: str,
) -> dict[str, Any]:
    reported = reported_skill_names(subject.final_output)
    judge_pass = judge.returncode == 0 and judge_passes_rubric(
        judge.output, case.rubric
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
        "skill_catalog": [str(path) for path in skill_paths],
        "skill_sources": [str(path) for path in skill_sources],
        "skill_catalog_digest": skill_catalog_digest,
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
        "suite": suite_for_skills(case.target_skills).id,
        "target_skills": list(case.target_skills),
        "expected_skills": list(case.expected_skills),
        "reported_skills": [skill for skill in reported if skill != ROUTER_SKILL],
        "reported_router": ROUTER_SKILL in reported,
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
            "events": list(judge.events),
            "output": judge.output,
            "usage": judge.usage,
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
    codex_version, skill_sha = preflight(repo_root, codex_executable, cases)
    skill_paths = discover_skill_paths(repo_root)
    skill_sources = _skill_source_paths(repo_root)
    skill_catalog_digest = _skill_catalog_digest(
        tuple(sorted({*skill_paths, *skill_sources}, key=str))
    )
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
                    skill_catalog_digest=skill_catalog_digest,
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
                        skill_paths=skill_paths,
                    )

                subject, subject_retries = run_with_one_retry(
                    run_subject_attempt,
                    lambda result: result.returncode != 0
                    or not subject_output_valid(result.final_output),
                )
                grade = grade_subject(case, subject)
                packet = build_judge_packet(case, subject, grade)
                packet_path = _judge_packet_path(
                    output_dir,
                    str(packet["candidate_id"]),
                    fingerprint,
                    repetition,
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
                        skill_paths=skill_paths,
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
                    skill_paths=skill_paths,
                    skill_sources=skill_sources,
                    skill_catalog_digest=skill_catalog_digest,
                )
                write_result(result_path, fingerprint, payload)
                records.append(payload)

    return write_reports(output_dir, records, compute_scorecard(records), seed=audit_seed)


def load_raw_records(output_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    baseline_controls: dict[str, Any] | None = None
    baseline_id: str | None = None
    for path in sorted((output_dir / "raw").glob("*/*/*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or not isinstance(
            document.get("payload"), dict
        ):
            raise ValueError(f"raw result must contain an object payload: {path}")
        payload = document["payload"]
        record_id = str(payload.get("id", path))
        payload.setdefault("suite", "compose")
        missing_controls = [
            field for field in RUN_CONTROL_FIELDS if field not in payload
        ]
        if missing_controls:
            raise ValueError(
                f"raw record {record_id} is missing run controls: "
                f"{', '.join(missing_controls)}"
            )
        controls = {field: payload[field] for field in RUN_CONTROL_FIELDS}
        if baseline_controls is None:
            baseline_controls = controls
            baseline_id = record_id
        else:
            differing_controls = [
                field
                for field in RUN_CONTROL_FIELDS
                if controls[field] != baseline_controls[field]
            ]
            if differing_controls:
                raise ValueError(
                    f"raw record {record_id} is incomparable with {baseline_id}; "
                    "different run controls: "
                    f"{', '.join(differing_controls)}"
                )
        subject_output = payload.get("subject", {}).get("final_output", {})
        if isinstance(subject_output, dict):
            reported = reported_skill_names(subject_output)
            payload["reported_skills"] = [
                skill for skill in reported if skill != ROUTER_SKILL
            ]
            payload["reported_router"] = ROUTER_SKILL in reported
        records.append(payload)
    return records


def _subject_result_from_record(
    record: dict[str, Any], output_dir: Path
) -> SubjectResult:
    subject = record.get("subject", {})
    command = subject.get("command", [])
    if not isinstance(command, list) or "-C" not in command:
        raise ValueError(f"record has no subject workspace: {record.get('id')}")
    workspace = Path(command[command.index("-C") + 1]).resolve()
    workspaces_root = (output_dir / "workspaces").resolve()
    if not workspace.is_relative_to(workspaces_root):
        raise ValueError(f"subject workspace escapes run directory: {workspace}")
    return SubjectResult(
        case_id=str(record["case_id"]),
        arm=str(record["arm"]),
        command=tuple(str(value) for value in command),
        workspace=workspace,
        returncode=int(subject.get("returncode", 1)),
        events=tuple(subject.get("events", ())),
        final_output=dict(subject.get("final_output", {})),
        usage=dict(subject.get("usage", {})),
        changed_paths=tuple(subject.get("changed_paths", ())),
        diff=str(subject.get("diff", "")),
        stdout="",
        stderr=str(subject.get("stderr", "")),
        elapsed_seconds=float(subject.get("elapsed_seconds", 0.0)),
    )


def regrade_records(
    repo_root: Path,
    cases: list[EvalCase],
    output_dir: Path,
    records: list[dict[str, Any]],
    *,
    audit_seed: int,
) -> dict[str, Path]:
    by_id = {case.id: case for case in cases}
    regraded: list[dict[str, Any]] = []
    for original in records:
        record = deepcopy(original)
        case_id = str(record.get("case_id"))
        if case_id not in by_id:
            raise ValueError(f"unknown case in raw record: {case_id}")
        case = by_id[case_id]
        grade = grade_subject(case, _subject_result_from_record(record, output_dir))
        record["objective_pass"] = grade.objective_pass
        record["forbidden_action_failure"] = grade.forbidden_action_failure
        record["objective_failures"] = list(grade.objective_failures)
        record["violations"] = list(grade.violations)
        record["validators"] = _validator_payload(grade)
        record["outcome_pass"] = grade.objective_pass and bool(record.get("judge_pass"))
        record["regraded_case_digest"] = _case_digest(case)
        regraded.append(record)
    destination = output_dir / "regraded"
    return write_reports(
        destination,
        regraded,
        compute_scorecard(regraded),
        seed=audit_seed,
    )


def write_rejudged_reports(
    output_dir: Path,
    records: list[dict[str, Any]],
    *,
    audit_seed: int,
) -> dict[str, Path]:
    packets: dict[tuple[str, int], tuple[str, dict[str, Any]]] = {}
    for packet_path in sorted((output_dir / "judge-packets").glob("*.json")):
        try:
            candidate_id, fingerprint_prefix, repetition = packet_path.stem.rsplit(
                "-", 2
            )
            key = (fingerprint_prefix, int(repetition))
        except ValueError as error:
            raise ValueError(f"invalid judge packet filename: {packet_path}") from error
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet.get("candidate_id") != candidate_id:
            raise ValueError(f"judge packet candidate mismatch: {packet_path}")
        if key in packets:
            raise ValueError(f"duplicate judge packet for fingerprint: {packet_path}")
        packets[key] = (packet_path.stem, packet)

    judgments: dict[str, tuple[str, dict[str, Any]]] = {}
    for result_path in sorted((output_dir / "rejudgments").glob("*/*.json")):
        document = json.loads(result_path.read_text(encoding="utf-8"))
        fingerprint = document.get("fingerprint")
        payload = document.get("payload")
        if not isinstance(fingerprint, str) or not isinstance(payload, dict):
            raise ValueError(f"invalid rejudgment result: {result_path}")
        candidate_id = payload.get("candidate_id")
        if not isinstance(candidate_id, str) or not isinstance(
            payload.get("judge"), dict
        ):
            raise ValueError(f"invalid rejudgment payload: {result_path}")
        packet_name = result_path.parent.name
        if packet_name in judgments:
            raise ValueError(f"ambiguous rejudgments for packet: {packet_name}")
        judgments[packet_name] = (fingerprint, payload)

    rejudged: list[dict[str, Any]] = []
    for original in records:
        fingerprint = original.get("fingerprint")
        repetition = original.get("repetition")
        if not isinstance(fingerprint, str) or not isinstance(repetition, int):
            raise ValueError(
                f"record lacks fingerprint or repetition: {original.get('id')}"
            )
        packet_record = packets.get((fingerprint[:20], repetition))
        if packet_record is None:
            raise ValueError(f"missing judge packet for record: {original.get('id')}")
        packet_name, packet = packet_record
        candidate_id = packet["candidate_id"]
        rejudgment = judgments.get(packet_name)
        if rejudgment is None:
            raise ValueError(f"missing rejudgment for packet: {packet_name}")
        rejudgment_fingerprint, judgment = rejudgment
        if judgment["candidate_id"] != candidate_id:
            raise ValueError(f"rejudgment candidate mismatch: {packet_name}")
        judge = judgment["judge"]
        rubric = tuple(packet.get("rubric", ()))
        judge_pass = int(judge.get("returncode", 1)) == 0 and judge_passes_rubric(
            judge.get("output", {}), rubric
        )
        record = deepcopy(original)
        record["original_judge"] = record["judge"]
        record["judge"] = judge
        record["judge_model"] = judgment.get("judge_model", record["judge_model"])
        record["judge_pass"] = judge_pass
        record["outcome_pass"] = bool(record.get("objective_pass")) and judge_pass
        record["rejudgment"] = {
            "candidate_id": candidate_id,
            "fingerprint": rejudgment_fingerprint,
        }
        rejudged.append(record)

    destination = output_dir / "rejudged"
    return write_reports(
        destination,
        rejudged,
        compute_scorecard(rejudged),
        seed=audit_seed,
    )


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
    codex_version = _command_output([codex_executable, "--version"], cwd=repo_root)
    skill_paths = discover_skill_paths(repo_root)
    skill_catalog_digest = _skill_catalog_digest(skill_paths)
    completed = 0
    for packet_path in packets:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        rubric = tuple(packet.get("rubric", ()))
        fingerprint = _rejudgment_fingerprint(
            packet_path,
            judge_config,
            skill_catalog_digest=skill_catalog_digest,
            codex_version=codex_version,
        )
        result_path = _rejudgment_result_path(output_dir, packet_path, fingerprint)
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
                skill_paths=skill_paths,
            ),
            lambda result: _judge_retryable(result)
            or not judge_covers_rubric(result.output, rubric),
        )
        write_result(
            result_path,
            fingerprint,
            {
                "candidate_id": packet.get("candidate_id"),
                "codex_version": codex_version,
                "judge_model": {
                    "model": judge_config.model,
                    "reasoning": judge_config.reasoning,
                },
                "judge": {
                    "returncode": judgment.returncode,
                    "events": list(judgment.events),
                    "output": judgment.output,
                    "usage": judgment.usage,
                    "stderr": judgment.stderr,
                    "elapsed_seconds": judgment.elapsed_seconds,
                    "retries": retries,
                },
            },
        )
        completed += 1
    return {**plan, "completed": completed}


def _rejudgment_fingerprint(
    packet_path: Path,
    judge_config: JudgeConfig,
    *,
    skill_catalog_digest: str,
    codex_version: str,
) -> str:
    identity = {
        "packet_digest": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "judge_config": asdict(judge_config),
        "skill_catalog_digest": skill_catalog_digest,
        "codex_version": codex_version,
    }
    return hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rejudgment_result_path(
    output_dir: Path, packet_path: Path, fingerprint: str
) -> Path:
    return output_dir / "rejudgments" / packet_path.stem / f"{fingerprint}.json"
