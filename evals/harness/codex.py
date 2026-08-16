from __future__ import annotations

import json
import difflib
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL, EvalCase


ARMS = ("none", "forced", "automatic")


@dataclass(frozen=True)
class RunConfig:
    model: str
    reasoning: str
    timeout_seconds: int = 900


@dataclass(frozen=True)
class SubjectResult:
    case_id: str
    arm: str
    command: tuple[str, ...]
    workspace: Path
    returncode: int
    events: tuple[dict[str, Any], ...]
    final_output: dict[str, Any]
    usage: dict[str, int]
    changed_paths: tuple[str, ...]
    diff: str
    stdout: str
    stderr: str
    elapsed_seconds: float


def _skill_config(case: EvalCase, arm: str, repo_root: Path) -> str:
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    enabled = set(case.target_skills) if arm == "forced" else set()
    if arm == "automatic":
        enabled = {*COMPOSE_SKILLS, ROUTER_SKILL}
    entries = []
    for skill in (*COMPOSE_SKILLS, ROUTER_SKILL):
        path = json.dumps(str((repo_root / "skills" / skill).resolve()))
        value = "true" if skill in enabled else "false"
        entries.append(f"{{ path = {path}, enabled = {value} }}")
    return "skills.config=[" + ", ".join(entries) + "]"


def _subject_prompt(case: EvalCase, arm: str) -> str:
    if arm != "forced":
        return case.prompt
    invocations = ", ".join(f"${skill}" for skill in case.target_skills)
    return case.prompt.rstrip() + f"\n\nUse the following skill(s) explicitly: {invocations}\n"


def build_subject_command(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    config: RunConfig,
    *,
    codex_executable: str = "codex",
) -> list[str]:
    sandbox = "read-only" if case.task_mode == "review" else "workspace-write"
    command = [
        codex_executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--json",
        "--output-schema",
        str((repo_root / "evals" / "schemas" / "subject-output.schema.json").resolve()),
        "--model",
        config.model,
        "-c",
        f'model_reasoning_effort="{config.reasoning}"',
        "-c",
        "sandbox_workspace_write.network_access=false",
        "-c",
        _skill_config(case, arm, repo_root),
        "--sandbox",
        sandbox,
    ]
    if case.task_mode == "edit":
        command.append("--approve-for-me")
    command.extend(["-C", str(workspace.resolve()), _subject_prompt(case, arm)])
    return command


def _run_git(workspace: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=workspace,
        text=True,
        capture_output=True,
        check=True,
    )


def prepare_workspace(case: EvalCase, repo_root: Path, destination: Path) -> Path:
    if destination.exists():
        raise FileExistsError(f"run workspace already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fixture = repo_root / "evals" / "fixtures" / case.fixture
    shutil.copytree(fixture, destination)
    overlay = case.directory / "overlay"
    if overlay.is_dir():
        shutil.copytree(overlay, destination, dirs_exist_ok=True)
    _run_git(destination, "init", "-q")
    _run_git(destination, "add", ".")
    _run_git(
        destination,
        "-c",
        "user.name=Skill Evaluator",
        "-c",
        "user.email=skill-evaluator@localhost",
        "commit",
        "-qm",
        "evaluation baseline",
    )
    return destination


def _parse_jsonl(stdout: str) -> tuple[tuple[dict[str, Any], ...], dict[str, Any], dict[str, int]]:
    events: list[dict[str, Any]] = []
    final_output: dict[str, Any] = {}
    usage: dict[str, int] = {}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        if event.get("type") == "item.completed":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str):
                    try:
                        value = json.loads(text)
                    except json.JSONDecodeError:
                        value = None
                    if isinstance(value, dict):
                        final_output = value
        raw_usage = event.get("usage")
        if isinstance(raw_usage, dict):
            usage = {
                str(key): int(value)
                for key, value in raw_usage.items()
                if isinstance(value, int) and not isinstance(value, bool)
            }
    return tuple(events), final_output, usage


def _changed_paths(workspace: Path) -> tuple[str, ...]:
    output = _run_git(workspace, "status", "--porcelain").stdout
    paths: set[str] = set()
    for line in output.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return tuple(sorted(paths))


def _workspace_diff(workspace: Path) -> str:
    diff = _run_git(workspace, "diff", "--no-ext-diff", "--binary", "HEAD").stdout
    tracked = set(_run_git(workspace, "ls-files").stdout.splitlines())
    for path in _changed_paths(workspace):
        if path in tracked:
            continue
        source = workspace / path
        if not source.is_file():
            continue
        try:
            lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
        except UnicodeDecodeError:
            diff += f"Binary file /dev/null and b/{path} differ\n"
            continue
        diff += "".join(
            difflib.unified_diff(
                [],
                lines,
                fromfile="/dev/null",
                tofile=f"b/{path}",
            )
        )
    return diff


def run_subject(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    config: RunConfig,
    *,
    codex_executable: str = "codex",
) -> SubjectResult:
    prepare_workspace(case, repo_root, workspace)
    command = build_subject_command(
        case,
        arm,
        repo_root,
        workspace,
        config,
        codex_executable=codex_executable,
    )
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
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
        stderr += f"\nsubject timed out after {config.timeout_seconds}s"
    elapsed = time.monotonic() - started
    events, final_output, usage = _parse_jsonl(stdout)
    diff = _workspace_diff(workspace)
    return SubjectResult(
        case_id=case.id,
        arm=arm,
        command=tuple(command),
        workspace=workspace,
        returncode=returncode,
        events=events,
        final_output=final_output,
        usage=usage,
        changed_paths=_changed_paths(workspace),
        diff=diff,
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=elapsed,
    )
