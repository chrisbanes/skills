from __future__ import annotations

import json
import difflib
import hashlib
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evals.harness.cases import EvalCase
from evals.harness.suites import PUBLIC_SKILLS, ROUTER_SKILL


ARMS = ("none", "forced", "automatic")
_GRADLE_OUTPUT_DIRECTORIES = (".gradle", ".kotlin", "build")
_GENERATED_SKILL_SUFFIXES = {".pyc", ".pyo"}
_TOOL_EVENT_TYPES = {
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "tool_call",
    "web_search",
}


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
    forced_target_preflight: dict[str, Any] | None = None


def completed_tool_call_count(
    events: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> int:
    return sum(
        event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") in _TOOL_EVENT_TYPES
        for event in events
    )


def completed_turn_count(
    events: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> int:
    return sum(event.get("type") == "turn.completed" for event in events)


def captured_skill_file_evidence(
    workspace: Path, events: tuple[dict[str, Any], ...]
) -> list[dict[str, Any]]:
    """Observe byte-identical staged skill text in completed command output."""
    root = workspace / ".agents" / "skills"
    outputs = []
    for event in events:
        item = event.get("item")
        if event.get("type") != "item.completed" or not isinstance(item, dict):
            continue
        if item.get("type") != "command_execution":
            continue
        output = item.get("aggregated_output")
        if isinstance(output, str):
            outputs.append((item.get("id"), output.encode("utf-8")))

    evidence = []
    for path in sorted(root.rglob("*.md")) if root.is_dir() else ():
        relative = path.relative_to(root)
        if path.name != "SKILL.md" and "references" not in relative.parts:
            continue
        try:
            staged = path.read_bytes()
        except OSError:
            staged = b""
        matched = [
            {"id": event_id, "output_sha256": hashlib.sha256(output).hexdigest()}
            for event_id, output in outputs
            if staged and staged in output
        ]
        evidence.append({
            "path": path.relative_to(workspace).as_posix(),
            "staged_bytes": len(staged),
            "staged_sha256": hashlib.sha256(staged).hexdigest() if staged else None,
            "status": (
                "complete" if matched else
                "incomplete_or_absent" if outputs and staged else "unavailable"
            ),
            "matched_events": matched,
        })
    return evidence


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


def automatically_invokable_public_skills(repo_root: Path) -> tuple[str, ...]:
    """Return public skills whose frontmatter and metadata permit invocation."""
    implicitly_invokable = []
    for skill in PUBLIC_SKILLS:
        skill_dir = repo_root / "skills" / skill
        metadata = skill_dir / "agents" / "openai.yaml"
        frontmatter = (skill_dir / "SKILL.md").read_text(encoding="utf-8").partition(
            "\n---\n"
        )[0]
        is_explicit_only = "disable-model-invocation: true" in frontmatter or (
            metadata.is_file()
            and "allow_implicit_invocation: false"
            in metadata.read_text(encoding="utf-8")
        )
        if not is_explicit_only:
            implicitly_invokable.append(skill)
    return tuple(implicitly_invokable)


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


def _enabled_skills(
    case: EvalCase, arm: str, repo_root: Path
) -> tuple[str, ...]:
    if arm == "none":
        return ()
    if arm == "forced":
        return case.target_skills
    if arm == "automatic":
        return automatically_invokable_public_skills(repo_root)
    raise ValueError(f"unknown arm: {arm}")


def _workspace_skill_path(workspace: Path, skill: str) -> Path:
    return (workspace / ".agents" / "skills" / skill / "SKILL.md").resolve()


def _canonical_skill_name(skill_path: Path) -> str | None:
    """Read an entrypoint's declared name without assuming its directory name."""
    try:
        frontmatter, marker, _ = skill_path.read_text(encoding="utf-8").partition(
            "\n---\n"
        )
    except OSError:
        return None
    if not marker:
        return None
    for line in frontmatter.splitlines():
        if line.startswith("name:"):
            value = line.removeprefix("name:").strip().strip("'\"")
            return value or None
    return None


def _configured_skill_entries(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    skill_paths: tuple[Path, ...],
) -> tuple[tuple[Path, bool], ...]:
    enabled = {
        _workspace_skill_path(workspace, skill)
        for skill in _enabled_skills(case, arm, repo_root)
    }
    enabled.update(
        _workspace_skill_path(workspace, skill) for skill in case.constant_skills
    )
    enabled_names = {
        name for path in enabled if (name := _canonical_skill_name(path)) is not None
    }
    discovered = {
        path.resolve()
        for path in skill_paths
        if _canonical_skill_name(path.resolve()) not in enabled_names
    }
    return tuple(
        (path, path in enabled)
        for path in sorted(discovered | enabled, key=str)
    )


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def forced_target_preflight(
    case: EvalCase,
    repo_root: Path,
    workspace: Path,
    skill_paths: tuple[Path, ...],
) -> dict[str, Any]:
    """Record whether each forced target is staged, identical, and uniquely enabled."""
    entries = _configured_skill_entries(case, "forced", repo_root, workspace, skill_paths)
    targets = []
    for skill in case.target_skills:
        source = (repo_root / "skills" / skill / "SKILL.md").resolve()
        staged = _workspace_skill_path(workspace, skill)
        source_sha = _sha256(source)
        staged_sha = _sha256(staged)
        same_name_entries = [
            {
                "path": str(path),
                "enabled": enabled,
                "canonical_name": _canonical_skill_name(path),
            }
            for path, enabled in entries
            if _canonical_skill_name(path) == skill
        ]
        enabled_count = sum(entry["enabled"] for entry in same_name_entries)
        if source_sha is None or staged_sha is None:
            status = "missing_target"
        elif source_sha != staged_sha:
            status = "byte_mismatch"
        elif enabled_count != 1:
            status = "not_uniquely_enabled"
        else:
            status = "valid"
        targets.append(
            {
                "skill": skill,
                "source_path": str(source),
                "source_sha256": source_sha,
                "staged_path": str(staged),
                "staged_directory": str(staged.parent),
                "staged_relative_path": f".agents/skills/{skill}/SKILL.md",
                "staged_relative_directory": f".agents/skills/{skill}",
                "staged_sha256": staged_sha,
                "exists": staged_sha is not None,
                "same_name_entries": same_name_entries,
                "enabled_count": enabled_count,
                "status": status,
            }
        )
    return {"valid": all(target["status"] == "valid" for target in targets), "targets": targets}


def _skill_config(
    case: EvalCase,
    arm: str,
    repo_root: Path,
    workspace: Path,
    skill_paths: tuple[Path, ...],
) -> str:
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    entries = []
    for skill_path, enabled in _configured_skill_entries(
        case, arm, repo_root, workspace, skill_paths
    ):
        path = json.dumps(str(skill_path.resolve()))
        value = "true" if enabled else "false"
        entries.append(f"{{ path = {path}, enabled = {value} }}")
    return "skills.config=[" + ", ".join(entries) + "]"


def _subject_prompt(case: EvalCase, arm: str) -> str:
    prompt = case.prompt.rstrip()
    prompt += (
        "\n\nIf you run Gradle, use `--offline --no-scan`. In `skills_used`, report "
        "only public repository skill entrypoints whose SKILL.md instructions you "
        "actually read and followed during this run; otherwise return an empty list."
    )
    if case.constant_skills:
        dependencies = ", ".join(case.constant_skills)
        prompt += (
            f" Evaluator-owned fixture dependencies to omit: {dependencies}. "
            "Enabled public skills are not fixture dependencies."
        )
    else:
        prompt += " This case has no evaluator-owned fixture dependencies."
    if arm == "forced":
        invocations = ", ".join(f"${skill}" for skill in case.target_skills)
        paths = ", ".join(
            f"`.agents/skills/{skill}/SKILL.md`" for skill in case.target_skills
        )
        targets = ", ".join(f"`{skill}`" for skill in case.target_skills)
        dependencies = ", ".join(f"`{skill}`" for skill in case.constant_skills)
        prompt += (
            f"\n\nUse the following skill(s) explicitly: {invocations}. "
            f"In a standalone command, use `cat` to print each of {paths} completely "
            "before any repository inspection or other action. Do not combine "
            "that read with other commands."
            "\n\nIn the final `skills_used`, include each of these exact public "
            f"targets whose entrypoint you read and followed: [{targets}]. "
            "Omit only these exact evaluator-owned dependency names: "
            f"[{dependencies}]. Exclusions are exact names, not prefixes."
        )
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
        output.write(".eval/forced-target-preflight.json\n")
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
    output = _run_git(workspace, "status", "--porcelain", "-z", "--untracked-files=all").stdout
    paths: set[str] = set()
    records = iter(output.split("\0"))
    for record in records:
        if not record:
            continue
        paths.add(record[3:])
        # Porcelain -z puts the destination first, followed by the source.
        if "R" in record[:2] or "C" in record[:2]:
            next(records)
    return tuple(sorted(paths))


def _workspace_diff(workspace: Path) -> str:
    diff = _run_git(workspace, "diff", "--no-ext-diff", "--binary", "HEAD").stdout
    tracked = set(_run_git(workspace, "ls-files", "-z").stdout.split("\0"))
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
        enabled_skills=_enabled_skills(case, arm, repo_root),
    )
    resolved_skill_paths = discover_skill_paths(repo_root) if skill_paths is None else skill_paths
    forced_preflight = (
        forced_target_preflight(case, repo_root, workspace, resolved_skill_paths)
        if arm == "forced"
        else None
    )
    if forced_preflight is not None:
        (workspace / ".eval" / "forced-target-preflight.json").write_text(
            json.dumps(forced_preflight, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    command = build_subject_command(
        case,
        arm,
        repo_root,
        workspace,
        config,
        codex_executable=codex_executable,
        skill_paths=resolved_skill_paths,
    )
    if forced_preflight is not None and not forced_preflight["valid"]:
        return SubjectResult(
            case_id=case.id,
            arm=arm,
            command=tuple(command),
            workspace=workspace,
            returncode=0,
            events=(),
            final_output={},
            usage={},
            changed_paths=(),
            diff="",
            stdout="",
            stderr="forced target preflight failed before model execution",
            elapsed_seconds=0.0,
            forced_target_preflight=forced_preflight,
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
        forced_target_preflight=forced_preflight,
    )
