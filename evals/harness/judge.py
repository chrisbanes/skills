from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL, EvalCase
from evals.harness.codex import SubjectResult
from evals.harness.grade import ObjectiveGrade


@dataclass(frozen=True)
class JudgeConfig:
    model: str
    reasoning: str
    timeout_seconds: int = 300


@dataclass(frozen=True)
class JudgeResult:
    returncode: int
    output: dict[str, Any]
    stdout: str
    stderr: str
    elapsed_seconds: float


def _initial_state(workspace: Path) -> dict[str, str]:
    paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        cwd=workspace,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    state: dict[str, str] = {}
    for path in paths:
        completed = subprocess.run(
            ["git", "show", f"HEAD:{path}"],
            cwd=workspace,
            capture_output=True,
            check=True,
        )
        try:
            state[path] = completed.stdout.decode("utf-8")
        except UnicodeDecodeError:
            state[path] = "<binary>"
    return state


def build_judge_packet(
    case: EvalCase, result: SubjectResult, grade: ObjectiveGrade
) -> dict[str, Any]:
    response = {
        "summary": result.final_output.get("summary", ""),
        "evidence": result.final_output.get("evidence", []),
    }
    initial_state = _initial_state(result.workspace)
    identity_source = json.dumps(
        {
            "task": case.prompt,
            "rubric": case.rubric,
            "initial_state": initial_state,
            "diff": result.diff,
            "response": response,
        },
        sort_keys=True,
    ).encode()
    candidate_id = hashlib.sha256(identity_source).hexdigest()[:20]
    return {
        "candidate_id": candidate_id,
        "task": case.prompt,
        "task_mode": case.task_mode,
        "rubric": list(case.rubric),
        "initial_state": initial_state,
        "workspace_diff": result.diff,
        "response": response,
        "validator_evidence": [
            {
                "validator_index": index,
                "returncode": validator.returncode,
                "stdout": validator.stdout,
                "stderr": validator.stderr,
                "timed_out": validator.timed_out,
            }
            for index, validator in enumerate(grade.validators, start=1)
        ],
    }


def _disabled_skill_config(repo_root: Path) -> str:
    entries = []
    for skill in (*COMPOSE_SKILLS, ROUTER_SKILL):
        path = json.dumps(str((repo_root / "skills" / skill).resolve()))
        entries.append(f"{{ path = {path}, enabled = false }}")
    return "skills.config=[" + ", ".join(entries) + "]"


def build_judge_command(
    packet_path: Path,
    repo_root: Path,
    config: JudgeConfig,
    *,
    codex_executable: str = "codex",
) -> list[str]:
    prompt = (
        f"Read {packet_path.name}. Judge only the supplied rubric and evidence. "
        "Return the required structured judgment without guessing experiment metadata."
    )
    return [
        codex_executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--json",
        "--output-schema",
        str((repo_root / "evals" / "schemas" / "judge-output.schema.json").resolve()),
        "--model",
        config.model,
        "-c",
        f'model_reasoning_effort="{config.reasoning}"',
        "-c",
        "sandbox_workspace_write.network_access=false",
        "-c",
        _disabled_skill_config(repo_root),
        "--sandbox",
        "read-only",
        "-C",
        str(packet_path.parent.resolve()),
        prompt,
    ]


def _judge_output(stdout: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "agent_message":
            continue
        text = item.get("text")
        if not isinstance(text, str):
            continue
        try:
            candidate = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            output = candidate
    return output


def judge_output_valid(output: dict[str, Any]) -> bool:
    criteria = output.get("criteria")
    return (
        isinstance(criteria, list)
        and all(
            isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and isinstance(item.get("pass"), bool)
            and isinstance(item.get("evidence"), str)
            for item in criteria
        )
        and isinstance(output.get("overall_pass"), bool)
        and isinstance(output.get("rationale"), str)
    )


def judge_covers_rubric(
    output: dict[str, Any], rubric: tuple[dict[str, str], ...]
) -> bool:
    if not judge_output_valid(output):
        return False
    actual = [item["id"] for item in output["criteria"]]
    expected = [item["id"] for item in rubric]
    return len(actual) == len(set(actual)) and set(actual) == set(expected)


def run_judge(
    packet_path: Path,
    repo_root: Path,
    config: JudgeConfig,
    *,
    codex_executable: str = "codex",
) -> JudgeResult:
    command = build_judge_command(
        packet_path, repo_root, config, codex_executable=codex_executable
    )
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=packet_path.parent,
            text=True,
            capture_output=True,
            timeout=config.timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        returncode = 124
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
    return JudgeResult(
        returncode=returncode,
        output=_judge_output(stdout),
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=time.monotonic() - started,
    )
