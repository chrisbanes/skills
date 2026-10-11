from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from evals.harness.cases import EvalCase
from evals.harness.suites import PUBLIC_SKILLS


ARMS = ("none", "forced", "automatic")
FIXTURE_SKILL_DIR = ".agents/skills"
_GRADLE_OUTPUT_DIRECTORIES = (".gradle", ".kotlin", "build")
_GENERATED_SKILL_SUFFIXES = {".pyc", ".pyo"}

Events = list[dict[str, Any]] | tuple[dict[str, Any], ...]


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
    runtime: str = "codex"


@dataclass(frozen=True)
class CommandRecord:
    """One attempted shell command, normalized across runtimes.

    `command` is the raw command string, or its argv as a tuple. `status` is
    `completed` for a finished command, `in_progress` for a start notice, and
    `denied` for a command the runtime refused. `sequence` is the 1-based
    position of the source event, so callers can keep event order.
    """

    id: object
    command: str | tuple[str, ...] | None
    exit_code: int | None
    output: str | None
    status: str
    sequence: int


class Runtime(Protocol):
    """Adapter that hides one agent CLI's command line and event format."""

    name: str
    skill_dir: str

    def version(self, executable: str, cwd: Path) -> str: ...

    def validate_reasoning(self, value: str) -> None: ...

    def check_workspace(self, workspace: Path) -> None:
        """Raise ValueError before staging when the workspace location is unsafe."""
        ...

    def edit_staged_skill(self, arm: str, skill_md: Path) -> None:
        """Adjust a freshly staged SKILL.md before the workspace baseline commit."""
        ...

    def forced_target_preflight(
        self,
        case: EvalCase,
        repo_root: Path,
        workspace: Path,
        skill_paths: tuple[Path, ...] | None,
    ) -> dict[str, Any]: ...

    def build_subject_command(
        self,
        case: EvalCase,
        arm: str,
        repo_root: Path,
        workspace: Path,
        config: RunConfig,
        *,
        executable: str,
        skill_paths: tuple[Path, ...] | None,
    ) -> list[str]: ...

    def execute_subject(
        self, command: list[str], workspace: Path, timeout: int
    ) -> tuple[int, str, str, dict[str, Any] | None]: ...

    def parse(
        self, stdout: str
    ) -> tuple[tuple[dict[str, Any], ...], dict[str, Any], dict[str, int]]: ...

    def commands(self, events: Events) -> tuple[CommandRecord, ...]: ...

    def file_tool_actions(self, events: Events) -> tuple[CommandRecord, ...]:
        """Return non-shell file tool calls; `command` is `(tool name, path)`."""
        ...

    def tool_call_count(self, events: Events) -> int: ...

    def turn_count(self, events: Events) -> int: ...

    def observed_skills(self, events: Events) -> list[str] | None: ...

    def skill_texts(self, events: Events) -> list[tuple[object, str]]: ...

    def skill_evidence_bytes(self, relative: Path, staged: bytes) -> bytes:
        """Return the part of a staged skill file that `skill_texts` can show."""
        ...

    def external_tool_attempts(self, events: Events) -> tuple[int, ...]:
        """Return the event sequence numbers of MCP or web tool attempts."""
        ...

    def permission_escalations(self, events: Events) -> tuple[int, ...]:
        """Return the event sequence numbers of permission escalation attempts."""
        ...

    def forced_instruction(self, case: EvalCase) -> str: ...

    def forced_target_observed(
        self, record: dict[str, Any], targets: list[dict[str, Any]]
    ) -> bool: ...

    def judge_command_prompt(self, command: list[str]) -> str:
        """Return the prompt argument of a command built by `build_judge_command`."""
        ...

    def judge_process_options(self) -> dict[str, Any]:
        """Extra `subprocess.run` keyword arguments for the judge process."""
        ...

    def build_judge_command(
        self,
        packet_path: Path,
        repo_root: Path,
        config: Any,
        *,
        executable: str,
        skill_paths: tuple[Path, ...] | None,
    ) -> list[str]: ...


def get_runtime(name: str) -> Runtime:
    if name == "codex":
        # Imported lazily: codex.py builds on this module.
        from evals.harness.codex import CodexRuntime

        return CodexRuntime()
    if name == "claude":
        from evals.harness.claude import ClaudeRuntime

        return ClaudeRuntime()
    raise ValueError(f"unknown runtime: {name}")


def record_runtime(record: dict[str, Any]) -> str:
    return record.get("runtime", "codex")


def record_judge_runtime(record: dict[str, Any]) -> str:
    return record.get("judge_runtime", "codex")


def captured_skill_file_evidence(
    workspace: Path, events: tuple[dict[str, Any], ...], *, runtime: str = "codex"
) -> list[dict[str, Any]]:
    """Observe byte-identical staged skill text in the runtime's captured text."""
    adapter = get_runtime(runtime)
    root = workspace / adapter.skill_dir
    outputs = [
        (event_id, text.encode("utf-8"))
        for event_id, text in adapter.skill_texts(events)
    ]

    evidence = []
    for path in sorted(root.rglob("*.md")) if root.is_dir() else ():
        relative = path.relative_to(root)
        if path.name != "SKILL.md" and "references" not in relative.parts:
            continue
        try:
            staged = path.read_bytes()
        except OSError:
            staged = b""
        needle = adapter.skill_evidence_bytes(relative, staged)
        matched = [
            {"id": event_id, "output_sha256": hashlib.sha256(output).hexdigest()}
            for event_id, output in outputs
            if needle and needle in output
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


def _subject_prompt(case: EvalCase, arm: str, runtime: Runtime) -> str:
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
        prompt += runtime.forced_instruction(case)
    return prompt + "\n"


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
    skill_dir: str = FIXTURE_SKILL_DIR,
    edit_skill: Callable[[Path], None] | None = None,
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
            destination / skill_dir / skill,
            ignore=_ignore_generated_skill_paths,
        )
        if edit_skill is not None:
            edit_skill(destination / skill_dir / skill / "SKILL.md")
    if skill_dir != FIXTURE_SKILL_DIR:
        # Fixtures ship their dependencies under .agents/skills; mirror them for this runtime.
        for skill in case.constant_skills:
            shutil.copytree(
                destination / FIXTURE_SKILL_DIR / skill, destination / skill_dir / skill
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
    runtime: str | Runtime = "codex",
    executable: str | None = None,
    skill_paths: tuple[Path, ...] | None = None,
) -> SubjectResult:
    adapter = get_runtime(runtime) if isinstance(runtime, str) else runtime
    executable = executable or adapter.name
    adapter.check_workspace(workspace)
    prepare_workspace(
        case,
        repo_root,
        workspace,
        enabled_skills=_enabled_skills(case, arm, repo_root),
        skill_dir=adapter.skill_dir,
        edit_skill=lambda skill_md: adapter.edit_staged_skill(arm, skill_md),
    )
    forced_preflight = (
        adapter.forced_target_preflight(case, repo_root, workspace, skill_paths)
        if arm == "forced"
        else None
    )
    if forced_preflight is not None:
        (workspace / ".eval" / "forced-target-preflight.json").write_text(
            json.dumps(forced_preflight, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    command = adapter.build_subject_command(
        case,
        arm,
        repo_root,
        workspace,
        config,
        executable=executable,
        skill_paths=skill_paths,
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
            runtime=adapter.name,
        )
    started = time.monotonic()
    returncode, stdout, stderr, isolation = adapter.execute_subject(
        command, workspace, config.timeout_seconds
    )
    elapsed = time.monotonic() - started
    if isolation is not None and not isolation.get("valid"):
        # An isolation failure invalidates the run like a failed forced preflight.
        forced_preflight = {
            **(forced_preflight or {"targets": []}),
            "valid": False,
            "isolation": isolation,
        }
    events, final_output, usage = adapter.parse(stdout)
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
        runtime=adapter.name,
    )
