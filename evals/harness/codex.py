from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

from evals.harness.cases import EvalCase
from evals.harness.judge import judge_prompt
from evals.harness.runner import (
    ARMS,
    CommandRecord,
    Events,
    RunConfig,
    _enabled_skills,
    _sha256,
    _subject_prompt,
)

_TOOL_EVENT_TYPES = {
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "tool_call",
    "web_search",
}


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
    command.extend(["-C", str(workspace.resolve()), _subject_prompt(case, arm, CodexRuntime())])
    return command


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




def _forced_instruction(case: EvalCase) -> str:
    invocations = ", ".join(f"${skill}" for skill in case.target_skills)
    paths = ", ".join(
        f"`.agents/skills/{skill}/SKILL.md`" for skill in case.target_skills
    )
    targets = ", ".join(f"`{skill}`" for skill in case.target_skills)
    dependencies = ", ".join(f"`{skill}`" for skill in case.constant_skills)
    return (
        f"\n\nUse the following skill(s) explicitly: {invocations}. "
        f"In a standalone command, use `cat` to print each of {paths} completely "
        "before any repository inspection or other action. Do not combine "
        "that read with other commands."
        "\n\nIn the final `skills_used`, include each of these exact public "
        f"targets whose entrypoint you read and followed: [{targets}]. "
        "Omit only these exact evaluator-owned dependency names: "
        f"[{dependencies}]. Exclusions are exact names, not prefixes."
    )


def _disabled_skill_config(skill_paths: tuple[Path, ...]) -> str:
    entries = []
    for skill_path in sorted(set(skill_paths), key=str):
        path = json.dumps(str(skill_path.resolve()))
        entries.append(f"{{ path = {path}, enabled = false }}")
    return "skills.config=[" + ", ".join(entries) + "]"


def build_judge_command(
    packet_path: Path,
    repo_root: Path,
    config: Any,
    *,
    codex_executable: str = "codex",
    skill_paths: tuple[Path, ...] | None = None,
) -> list[str]:
    prompt = judge_prompt(packet_path)
    return [
        codex_executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
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
        'web_search="disabled"',
        "-c",
        _disabled_skill_config(
            discover_skill_paths(repo_root) if skill_paths is None else skill_paths
        ),
        "--sandbox",
        "read-only",
        "-C",
        str(packet_path.parent.resolve()),
        prompt,
    ]


def execute_subject(
    command: list[str], workspace: Path, timeout: int
) -> tuple[int, str, str, None]:
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        returncode = 124
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        stderr += f"\nsubject timed out after {timeout}s"
    return returncode, stdout, stderr, None


def command_records(events: Events) -> tuple[CommandRecord, ...]:
    records = []
    for sequence, event in enumerate(events, 1):
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        command = item.get("command")
        if isinstance(command, list):
            command = tuple(str(part) for part in command)
        elif not isinstance(command, str):
            command = None
        records.append(CommandRecord(
            id=item.get("id"),
            command=command,
            exit_code=item.get("exit_code"),
            output=item.get("aggregated_output"),
            status="completed" if event.get("type") == "item.completed" else "in_progress",
            sequence=sequence,
        ))
    return tuple(records)


def _item_type_sequences(events: Events, *markers: str) -> tuple[int, ...]:
    sequences = []
    for sequence, event in enumerate(events, 1):
        item = event.get("item")
        if not isinstance(item, dict):
            item = {}
        item_type = str(item.get("type", event.get("type", ""))).lower()
        if any(marker in item_type for marker in markers):
            sequences.append(sequence)
    return tuple(sequences)


def _standalone_target_reads(command: str, targets: list[dict[str, Any]]) -> set[str] | None:
    """Return the target paths printed by a standalone cat command."""
    try:
        words = shlex.split(command)
        if (
            len(words) == 3
            and words[0] in ("sh", "bash", "zsh", "/bin/sh", "/bin/bash", "/bin/zsh")
            and words[1] in ("-c", "-lc")
        ):
            words = shlex.split(words[2])
    except ValueError:
        return None
    if not words:
        return None
    if words[0] not in ("cat", "/bin/cat", "/usr/bin/cat"):
        return None
    operands = words[2:] if len(words) > 1 and words[1] == "--" else words[1:]
    if not operands:
        return None
    matched: set[str] = set()
    for operand in operands:
        target = next(
            (target for target in targets if operand in (
                target.get("staged_relative_path"), target.get("staged_path")
            )), None,
        )
        if target is None:
            return None
        path = target.get("staged_relative_path")
        if not isinstance(path, str) or path in matched:
            return None
        matched.add(path)
    return matched


def _observed_staged_target_read(record: dict[str, Any], targets: list[dict[str, Any]]) -> bool:
    subject = record.get("subject", {})
    if not isinstance(subject, dict):
        return False
    events = subject.get("events", [])
    captures = subject.get("captured_skill_files", [])
    if not isinstance(events, list) or not isinstance(captures, list):
        return False
    if not targets or not all(isinstance(target, dict) for target in targets):
        return False
    remaining = {target.get("staged_relative_path") for target in targets}
    if (
        None in remaining or len(remaining) != len(targets)
        or any(not isinstance(path, str) or not path.endswith("/SKILL.md") for path in remaining)
    ):
        return False
    active_id = None
    for event in events:
        if not isinstance(event, dict) or event.get("type") not in ("item.started", "item.completed"):
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") in ("reasoning", "agent_message"):
            continue
        if item.get("type") != "command_execution" or item.get("id") is None:
            return False
        if event["type"] == "item.started":
            if active_id is not None:
                return False
            active_id = item["id"]
            continue
        if active_id is not None and item["id"] != active_id:
            return False
        active_id = None
        if (
            item.get("status") != "completed"
            or item.get("exit_code") != 0
            or not isinstance(item.get("command"), str)
        ):
            return False
        reads = _standalone_target_reads(item["command"], targets)
        if reads is None or not reads <= remaining:
            return False
        for path in reads:
            target = next(target for target in targets if target["staged_relative_path"] == path)
            target_sha = target.get("staged_sha256")
            capture = next(
                (
                    captured for captured in captures
                    if isinstance(captured, dict) and captured.get("path") == path
                    and captured.get("status") == "complete"
                    and captured.get("staged_sha256") == target_sha
                ), None,
            )
            if not isinstance(target_sha, str) or not target_sha or capture is None:
                return False
            matched_events = capture.get("matched_events")
            if not isinstance(matched_events, list) or not any(
                isinstance(match, dict) and match.get("id") == item["id"]
                for match in matched_events
            ):
                return False
        remaining -= reads
        if not remaining:
            return True
    return False


class CodexRuntime:
    """`codex exec` adapter; every member keeps the pre-seam Codex behaviour."""

    name = "codex"
    skill_dir = ".agents/skills"

    def version(self, executable: str, cwd: Path) -> str:
        # experiment owns the bounded CLI call and its tested timeout guidance.
        from evals.harness.experiment import _codex_version

        return _codex_version(cwd, executable)

    def validate_reasoning(self, value: str) -> None:
        """Codex accepts any reasoning effort string."""

    def check_workspace(self, workspace: Path) -> None:
        """Codex has no workspace location requirement."""

    def edit_staged_skill(self, arm: str, skill_md: Path) -> None:
        """Codex stages skills byte-identical to their source."""

    def forced_target_preflight(self, case, repo_root, workspace, skill_paths):
        return forced_target_preflight(
            case,
            repo_root,
            workspace,
            discover_skill_paths(repo_root) if skill_paths is None else skill_paths,
        )

    def build_subject_command(
        self, case, arm, repo_root, workspace, config, *, executable, skill_paths
    ):
        return build_subject_command(
            case,
            arm,
            repo_root,
            workspace,
            config,
            codex_executable=executable,
            skill_paths=skill_paths,
        )

    def execute_subject(self, command, workspace, timeout):
        return execute_subject(command, workspace, timeout)

    def parse(self, stdout):
        return parse_codex_jsonl(stdout)

    def commands(self, events):
        return command_records(events)

    def file_tool_actions(self, events):
        return ()

    def tool_call_count(self, events):
        return completed_tool_call_count(events)

    def turn_count(self, events):
        return completed_turn_count(events)

    def observed_skills(self, events):
        return None

    def skill_texts(self, events):
        return [
            (command.id, command.output)
            for command in command_records(events)
            if command.status == "completed" and isinstance(command.output, str)
        ]

    def skill_evidence_bytes(self, relative, staged):
        return staged

    def external_tool_attempts(self, events):
        return _item_type_sequences(events, "mcp", "web_search")

    def permission_escalations(self, events):
        return _item_type_sequences(events, "approval")

    def forced_instruction(self, case):
        return _forced_instruction(case)

    def forced_target_observed(self, record, targets):
        return _observed_staged_target_read(record, targets)

    def judge_process_options(self):
        return {}

    def build_judge_command(
        self, packet_path, repo_root, config, *, executable, skill_paths
    ):
        return build_judge_command(
            packet_path,
            repo_root,
            config,
            codex_executable=executable,
            skill_paths=skill_paths,
        )
