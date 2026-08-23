from __future__ import annotations

import json
import difflib
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evals.harness.cases import EvalCase
from evals.harness.suites import PUBLIC_SKILLS, ROUTER_SKILL


ARMS = ("none", "forced", "automatic")
_GRADLE_OUTPUT_DIRECTORIES = (".gradle", "build")
_GENERATED_SKILL_SUFFIXES = {".pyc", ".pyo"}


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


def canonical_skill_name(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    name = value.removeprefix("chrisbanes-skills:")
    return name if name in PUBLIC_SKILLS else None


def reported_skill_names(output: dict[str, Any]) -> list[str]:
    values = output.get("skills_used", [])
    if not isinstance(values, list):
        return []
    return [name for value in values if (name := canonical_skill_name(value))]


def subject_output_valid(output: dict[str, Any]) -> bool:
    skills = output.get("skills_used")
    evidence = output.get("evidence")
    canonical_skills = reported_skill_names(output)
    return (
        set(output) == {"summary", "skills_used", "evidence"}
        and isinstance(output.get("summary"), str)
        and isinstance(skills, list)
        and len(canonical_skills) == len(skills)
        and len(canonical_skills) == len(set(canonical_skills))
        and isinstance(evidence, list)
        and all(isinstance(item, str) for item in evidence)
    )


def discover_skill_paths(
    repo_root: Path, *, roots: tuple[Path, ...] | None = None
) -> tuple[Path, ...]:
    """Return every discoverable skill file that must be explicitly configured."""
    if roots is None:
        user_root = Path.home()
        roots = (
            user_root / ".codex" / "skills",
            user_root / ".agents" / "skills",
            user_root / ".codex" / "plugins" / "cache",
        )
    candidates: set[Path] = set()
    for root in roots:
        if root.is_dir():
            candidates.update(path.resolve() for path in root.rglob("SKILL.md"))
    return tuple(sorted(candidates, key=str))


def is_generated_skill_path(path: Path, skill_root: Path) -> bool:
    relative = path.relative_to(skill_root)
    return "__pycache__" in relative.parts or (
        path.is_file() and path.suffix in _GENERATED_SKILL_SUFFIXES
    )


def _ignore_generated_skill_paths(directory: str, names: list[str]) -> list[str]:
    root = Path(directory)
    return [
        name
        for name in names
        if is_generated_skill_path(root / name, root)
    ]


def _enabled_skills(case: EvalCase, arm: str) -> tuple[str, ...]:
    if arm == "none":
        return ()
    if arm == "forced":
        return case.target_skills
    if arm == "automatic":
        return PUBLIC_SKILLS
    raise ValueError(f"unknown arm: {arm}")


def _workspace_skill_path(workspace: Path, skill: str) -> Path:
    return (workspace / ".agents" / "skills" / skill / "SKILL.md").resolve()


def _skill_config(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    skill_paths: tuple[Path, ...],
) -> str:
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    enabled = {
        _workspace_skill_path(workspace, skill)
        for skill in _enabled_skills(case, arm)
    }
    entries = []
    configured_paths = set(skill_paths) | enabled
    for skill_path in sorted(configured_paths, key=str):
        path = json.dumps(str(skill_path.resolve()))
        value = "true" if skill_path.resolve() in enabled else "false"
        entries.append(f"{{ path = {path}, enabled = {value} }}")
    return "skills.config=[" + ", ".join(entries) + "]"


def _subject_prompt(case: EvalCase, arm: str) -> str:
    prompt = case.prompt.rstrip()
    prompt += (
        "\n\nIf you run Gradle, use `--offline --no-scan`. In `skills_used`, report "
        "only skills whose SKILL.md instructions you actually read and followed during "
        "this run; otherwise return an empty list."
    )
    if arm == "forced":
        invocations = ", ".join(f"${skill}" for skill in case.target_skills)
        prompt += f"\n\nUse the following skill(s) explicitly: {invocations}"
    return prompt + "\n"


def build_subject_command(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    config: RunConfig,
    *,
    codex_executable: str = "codex",
    skill_paths: tuple[Path, ...] | None = None,
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
        str((workspace / ".eval" / "subject-output.schema.json").resolve()),
        "--model",
        config.model,
        "-c",
        f'model_reasoning_effort="{config.reasoning}"',
        "-c",
        "sandbox_workspace_write.network_access=false",
        "-c",
        'web_search="disabled"',
        "-c",
        _skill_config(
            case,
            arm,
            repo_root,
            workspace,
            discover_skill_paths(repo_root) if skill_paths is None else skill_paths,
        ),
    ]
    command.extend(["--sandbox", sandbox])
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


def prepare_workspace(
    case: EvalCase,
    repo_root: Path,
    destination: Path,
    *,
    enabled_skills: tuple[str, ...] = (),
) -> Path:
    if destination.exists():
        raise FileExistsError(f"run workspace already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fixture = repo_root / "evals" / "fixtures" / case.fixture
    shutil.copytree(
        fixture,
        destination,
        ignore=shutil.ignore_patterns(*_GRADLE_OUTPUT_DIRECTORIES),
    )
    subject_gradlew = destination / "subject-gradlew"
    if subject_gradlew.is_file():
        shutil.copy2(destination / "gradlew", destination / "gradlew-real")
        shutil.copy2(subject_gradlew, destination / "gradlew")
        subject_gradlew.unlink()
    overlay = case.directory / "overlay"
    if overlay.is_dir():
        shutil.copytree(overlay, destination, dirs_exist_ok=True)
    schema_dir = destination / ".eval"
    schema_dir.mkdir()
    shutil.copy2(
        repo_root / "evals" / "schemas" / "subject-output.schema.json",
        schema_dir / "subject-output.schema.json",
    )
    for skill in enabled_skills:
        shutil.copytree(
            repo_root / "skills" / skill,
            destination / ".agents" / "skills" / skill,
            ignore=_ignore_generated_skill_paths,
        )
    _run_git(destination, "init", "-q")
    exclude = destination / ".git" / "info" / "exclude"
    with exclude.open("a", encoding="utf-8") as output:
        output.write("\n# Evaluator-sanctioned Gradle outputs\n")
        output.writelines(
            f"{directory}/\n" for directory in _GRADLE_OUTPUT_DIRECTORIES
        )
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


def parse_codex_jsonl(
    stdout: str,
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any], dict[str, int]]:
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
    skill_paths: tuple[Path, ...] | None = None,
) -> SubjectResult:
    prepare_workspace(
        case,
        repo_root,
        workspace,
        enabled_skills=_enabled_skills(case, arm),
    )
    command = build_subject_command(
        case,
        arm,
        repo_root,
        workspace,
        config,
        codex_executable=codex_executable,
        skill_paths=skill_paths,
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
    events, final_output, usage = parse_codex_jsonl(stdout)
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
