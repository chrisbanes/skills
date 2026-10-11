"""`claude -p` subject runtime.

Claude Code 2.1.296 findings (T1 probe, plus T3 init-only probes):
- A1: init lists staged project skills plus 22 bundled built-ins; a
  `skillOverrides: {"<name>": "off"}` setting removes each built-in, and
  `--disable-slash-commands` gives `skills: []`.
- A2: an ancestor CLAUDE.md reaches the model despite `--setting-sources
  project`; `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` blocks it. Runs also refuse
  workspaces below a CLAUDE.md or CLAUDE.local.md.
- A3: `system/init` precedes the first assistant event, but `system`
  events such as `thinking_tokens` may precede it, so init is matched on
  `subtype == "init"`. `system/task_summary` events may follow `result`.
- A4: `--json-schema` returns `result.structured_output` under stream-json;
  the inline schema must not carry a `$schema` key.
- A5: a Skill call yields a tool_result without `is_error` (success), then an
  `isSynthetic` user message: `Base directory for this skill: <dir>\n\n`
  followed by the SKILL.md body without frontmatter, leading newlines removed.
- A6: the bash sandbox works on macOS with `failIfUnavailable`; a blocked
  network call fails with `Exit code N` text and `is_error: true`.
- `claude` must run with stdin at /dev/null.
- D3: init reports `memory_paths.auto` unless `autoMemoryEnabled: false` is
  passed through `--settings`; with it, init has no `memory_paths`
  (confirmed by two init-only probes).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Iterator

from evals.harness.cases import EvalCase
from evals.harness.runner import (
    CommandRecord,
    Events,
    RunConfig,
    _enabled_skills,
    _subject_prompt,
    canonical_skill_name,
)
from evals.harness.suites import ROUTER_SKILL

REASONING_EFFORTS = ("low", "medium", "high", "xhigh", "max")
REVIEW_TOOLS = ("Read", "Grep", "Glob", "Bash", "Skill")
EDIT_TOOLS = (*REVIEW_TOOLS, "Edit", "Write")
DISALLOWED_TOOLS = ("WebFetch", "WebSearch")
SANDBOX = {
    "enabled": True,
    "failIfUnavailable": True,
    "allowUnsandboxedCommands": False,
    "autoAllowBashIfSandboxed": True,
    "network": {"allowedDomains": []},
}

_INPUT_TOKEN_FIELDS = (
    "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"
)
_EXIT_CODE = re.compile(r"Exit code (\d+)")


def parse_claude_stream(
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
        if event.get("type") != "result":
            continue
        if isinstance(event.get("structured_output"), dict):
            final_output = event["structured_output"]
        raw_usage = event.get("usage")
        if isinstance(raw_usage, dict):
            usage = {
                str(key): value
                for key, value in raw_usage.items()
                if isinstance(value, int) and not isinstance(value, bool)
            }
            # Codex input_tokens already include cached input; match that total.
            usage["input_tokens"] = sum(usage.get(key, 0) for key in _INPUT_TOKEN_FIELDS)
    return tuple(events), final_output, usage


def _blocks(event: dict[str, Any], kind: str) -> Iterator[dict[str, Any]]:
    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, list):
        yield from (
            block for block in content
            if isinstance(block, dict) and block.get("type") == kind
        )


def _tool_uses(events: Events) -> Iterator[tuple[int, dict[str, Any]]]:
    for sequence, event in enumerate(events, 1):
        if event.get("type") == "assistant":
            yield from ((sequence, block) for block in _blocks(event, "tool_use"))


def _tool_names(events: Events) -> dict[object, object]:
    return {block.get("id"): block.get("name") for _, block in _tool_uses(events)}


def _denials(event: dict[str, Any]) -> list[dict[str, Any]]:
    denials = event.get("permission_denials") if event.get("type") == "result" else None
    return [denial for denial in denials or () if isinstance(denial, dict)]


def _is_external_tool(name: object) -> bool:
    return isinstance(name, str) and (
        name.startswith("mcp__") or name in DISALLOWED_TOOLS
    )


def _init_tools(events: Events) -> set[object]:
    for event in events:
        if event.get("type") == "system" and event.get("subtype") == "init":
            return set(event.get("tools") or ())
    return {*EDIT_TOOLS, "StructuredOutput"}


def _text(content: object) -> str | None:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        )
    return None


def _exit_code(result: dict[str, Any]) -> int:
    if not result.get("is_error"):
        return 0
    match = _EXIT_CODE.match(_text(result.get("content")) or "")
    # A failed call never reports exit 0, even if its text claims it.
    return (int(match.group(1)) or 1) if match else 1


def _bash_command(tool_input: object) -> str | None:
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    return command if isinstance(command, str) else None


def command_records(events: Events) -> tuple[CommandRecord, ...]:
    pending: dict[object, tuple[int, str | None]] = {}
    records = []
    for sequence, event in enumerate(events, 1):
        if event.get("type") == "assistant":
            for block in _blocks(event, "tool_use"):
                if block.get("name") == "Bash":
                    pending[block.get("id")] = (sequence, _bash_command(block.get("input")))
        elif event.get("type") == "user":
            for block in _blocks(event, "tool_result"):
                use = pending.pop(block.get("tool_use_id"), None)
                if use is not None:
                    records.append(CommandRecord(
                        id=block.get("tool_use_id"),
                        command=use[1],
                        exit_code=_exit_code(block),
                        output=_text(block.get("content")),
                        status="completed",
                        sequence=sequence,
                    ))
        for denial in _denials(event):
            if denial.get("tool_name") == "Bash":
                records.append(CommandRecord(
                    id=denial.get("tool_use_id"),
                    command=_bash_command(denial.get("tool_input")),
                    exit_code=None,
                    output=None,
                    status="denied",
                    sequence=sequence,
                ))
    records.extend(
        CommandRecord(id=tool_id, command=command, exit_code=None, output=None,
                      status="in_progress", sequence=sequence)
        for tool_id, (sequence, command) in pending.items()
    )
    return tuple(sorted(records, key=lambda record: record.sequence))


def _json_object(line: str) -> dict[str, Any]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


class _Child:
    """One spawned `claude` process whose stdout is read until its init event."""

    def __init__(self, command: list[str], cwd: Path):
        self.process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"},
        )
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.init: dict[str, Any] | None = None
        # Set on init, on model output before init, or at end of output.
        self.init_settled = threading.Event()
        self._threads = [
            threading.Thread(target=self._read_stdout, daemon=True),
            threading.Thread(
                target=lambda: self.stderr.append(self.process.stderr.read()),
                daemon=True,
            ),
        ]
        for thread in self._threads:
            thread.start()

    def _read_stdout(self) -> None:
        for line in self.process.stdout:
            self.stdout.append(line)
            if self.init_settled.is_set():
                continue
            event = _json_object(line)
            if event.get("type") == "system" and event.get("subtype") == "init":
                self.init = event
                self.init_settled.set()
            elif event.get("type") in ("assistant", "user", "result"):
                self.init_settled.set()
        self.init_settled.set()

    def stop(self) -> None:
        """Stop only this child: terminate, then kill after 10 s."""
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()

    def output(self) -> tuple[str, str]:
        for thread in self._threads:
            # ponytail: a grandchild holding the pipes open truncates output after 5 s.
            thread.join(5)
        if not any(thread.is_alive() for thread in self._threads):
            self.process.stdout.close()
            self.process.stderr.close()
        return "".join(self.stdout), "".join(self.stderr)


def init_isolation(init: dict[str, Any] | None, expected_skills: list[str]) -> dict[str, Any]:
    """Check that init lists exactly the staged skills, no MCP servers, no auto memory."""
    problems: dict[str, Any] = {}
    if init is None:
        problems["init"] = "no system/init event before model output"
        init = {}
    skills = init.get("skills") if isinstance(init.get("skills"), list) else []
    mcp_servers = init.get("mcp_servers") if isinstance(init.get("mcp_servers"), list) else []
    memory_paths = init.get("memory_paths")
    if unexpected := sorted(set(map(str, skills)) - set(expected_skills)):
        problems["unexpected_skills"] = unexpected
    if missing := sorted(set(expected_skills) - set(map(str, skills))):
        problems["missing_skills"] = missing
    if mcp_servers:
        problems["mcp_servers"] = mcp_servers
    if isinstance(memory_paths, dict) and "auto" in memory_paths:
        problems["auto_memory"] = memory_paths["auto"]
    return {
        "valid": not problems,
        "expected_skills": expected_skills,
        "init_skills": skills,
        "problems": problems,
    }


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _captured(captures: list[Any], target: dict[str, Any], tool_id: object) -> bool:
    sha = target.get("staged_sha256")
    return isinstance(sha, str) and bool(sha) and any(
        isinstance(capture, dict)
        and capture.get("path") == target.get("staged_relative_path")
        and capture.get("status") == "complete"
        and capture.get("staged_sha256") == sha
        and isinstance(capture.get("matched_events"), list)
        and any(
            isinstance(match, dict) and match.get("id") == tool_id
            for match in capture["matched_events"]
        )
        for capture in captures
    )


def inline_schema(path: Path) -> str:
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema.pop("$schema", None)
    return json.dumps(schema, separators=(",", ":"))


def isolation_flags(model: str, effort: str, settings: dict, tools: tuple[str, ...]) -> list[str]:
    return [
        "--output-format", "stream-json", "--verbose",
        "--no-session-persistence",
        "--setting-sources", "project",
        "--strict-mcp-config",
        "--permission-mode", "dontAsk",
        "--model", model,
        "--effort", effort,
        "--settings", json.dumps(settings),
        "--tools", ",".join(tools),
        "--allowedTools", ",".join(tools),
        "--disallowedTools", ",".join(DISALLOWED_TOOLS),
    ]


def discover_builtin_skills(
    executable: str, config: RunConfig, *, timeout: int = 60
) -> tuple[str, ...]:
    """Return the skills an empty workspace loads, read from an init-only run.

    The child is stopped as soon as its init event arrives, before model output.
    """
    settings = {"sandbox": SANDBOX, "autoMemoryEnabled": False}
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=workspace, check=True, capture_output=True)
        child = _Child(
            [
                executable,
                "-p",
                "Reply with OK.",
                *isolation_flags(config.model, config.reasoning, settings, EDIT_TOOLS),
            ],
            workspace,
        )
        try:
            child.init_settled.wait(timeout)
        finally:
            child.stop()
            child.output()
    skills = child.init.get("skills") if child.init is not None else None
    if not isinstance(skills, list) or not all(isinstance(skill, str) for skill in skills):
        raise RuntimeError(
            f"{executable} gave no system/init skill list before model output"
        )
    return tuple(sorted(skills))


class ClaudeRuntime:
    name = "claude"
    skill_dir = ".claude/skills"

    def __init__(self, builtin_skills: tuple[str, ...] = ()):
        # Built-ins come from discover_builtin_skills; each unstaged one is switched off.
        self.builtin_skills = tuple(builtin_skills)

    def version(self, executable: str, cwd: Path) -> str:
        from evals.harness.experiment import _command_output

        return _command_output(
            [executable, "--version"],
            cwd=cwd,
            timeout_seconds=10,
            timeout_hint="Check the Claude Code CLI installation, then retry.",
        )

    def check_workspace(self, workspace: Path) -> None:
        """Refuse a workspace below CLAUDE.md files that would reach the subject."""
        claude_home = (Path.home() / ".claude").resolve()
        for directory in workspace.resolve().parents:
            if directory == claude_home:
                continue
            for name in ("CLAUDE.md", "CLAUDE.local.md"):
                if (directory / name).is_file():
                    raise ValueError(
                        f"{directory / name} is an ancestor of the Claude workspace "
                        f"{workspace}; pass an --output-dir outside the repository"
                    )

    def forced_target_preflight(self, case, repo_root, workspace, skill_paths):
        """Record whether each forced target is staged, identical and not shadowed."""
        targets = []
        for skill in case.target_skills:
            source = (repo_root / "skills" / skill / "SKILL.md").resolve()
            relative = f"{self.skill_dir}/{skill}/SKILL.md"
            staged = (workspace / relative).resolve()
            source_sha, staged_sha = _sha256(source), _sha256(staged)
            if source_sha is None or staged_sha is None:
                status = "missing_target"
            elif source_sha != staged_sha:
                status = "byte_mismatch"
            elif skill in self.builtin_skills:
                # A built-in of the same name cannot be switched off separately.
                status = "not_uniquely_enabled"
            else:
                status = "valid"
            targets.append({
                "skill": skill,
                "source_path": str(source),
                "source_sha256": source_sha,
                "staged_path": str(staged),
                "staged_directory": str(staged.parent),
                "staged_relative_path": relative,
                "staged_relative_directory": f"{self.skill_dir}/{skill}",
                "staged_sha256": staged_sha,
                "exists": staged_sha is not None,
                "status": status,
            })
        return {
            "valid": all(target["status"] == "valid" for target in targets),
            "targets": targets,
        }

    def validate_reasoning(self, value: str) -> None:
        if value not in REASONING_EFFORTS:
            raise ValueError(
                f"claude effort must be one of {', '.join(REASONING_EFFORTS)}: {value}"
            )

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
    ) -> list[str]:
        staged = {*_enabled_skills(case, arm, repo_root), *case.constant_skills}
        settings = {
            "sandbox": SANDBOX,
            "autoMemoryEnabled": False,
            "skillOverrides": {
                skill: "off" for skill in self.builtin_skills if skill not in staged
            },
        }
        tools = REVIEW_TOOLS if case.task_mode == "review" else EDIT_TOOLS
        # The prompt precedes the variadic tool options so they cannot swallow it.
        command = [
            executable,
            "-p",
            _subject_prompt(case, arm, self),
            "--json-schema",
            inline_schema(repo_root / "evals" / "schemas" / "subject-output.schema.json"),
            *isolation_flags(config.model, config.reasoning, settings, tools),
        ]
        if arm == "none":
            command.append("--disable-slash-commands")
        return command

    def execute_subject(self, command, workspace, timeout):
        deadline = time.monotonic() + timeout
        expected = sorted(
            path.parent.name for path in (workspace / self.skill_dir).glob("*/SKILL.md")
        )
        child = _Child(command, workspace)
        if child.init_settled.wait(timeout):
            isolation = init_isolation(child.init, expected)
        else:
            isolation = init_isolation(None, expected)
        if not isolation["valid"]:
            child.stop()
            stdout, stderr = child.output()
            stderr += "claude init isolation check failed: " + json.dumps(
                isolation["problems"], sort_keys=True
            )
            return child.process.returncode, stdout, stderr, isolation
        try:
            returncode = child.process.wait(max(0.0, deadline - time.monotonic()))
            timed_out = False
        except subprocess.TimeoutExpired:
            child.stop()
            returncode, timed_out = 124, True
        stdout, stderr = child.output()
        if timed_out:
            stderr += f"\nsubject timed out after {timeout}s"
        return returncode, stdout, stderr, isolation

    def parse(self, stdout):
        return parse_claude_stream(stdout)

    def commands(self, events):
        return command_records(events)

    def tool_call_count(self, events):
        names = _tool_names(events)
        return sum(
            names.get(block.get("tool_use_id"), "StructuredOutput") != "StructuredOutput"
            for event in events
            if event.get("type") == "user"
            for block in _blocks(event, "tool_result")
        )

    def turn_count(self, events):
        return sum(event.get("type") == "result" for event in events)

    def observed_skills(self, events):
        observed: list[str] = []
        for _, block in _tool_uses(events):
            tool_input = block.get("input")
            name = canonical_skill_name(
                tool_input.get("skill") if isinstance(tool_input, dict) else None
            )
            if block.get("name") == "Skill" and name and name != ROUTER_SKILL:
                observed.append(name)
        return list(dict.fromkeys(observed))

    def skill_texts(self, events):
        """Pair each synthetic skill body with the successful Skill call before it."""
        names = _tool_names(events)
        loaded: list[object] = []
        texts = []
        for event in events:
            if event.get("type") != "user":
                continue
            loaded.extend(
                block.get("tool_use_id")
                for block in _blocks(event, "tool_result")
                if names.get(block.get("tool_use_id")) == "Skill"
                and not block.get("is_error")
            )
            if event.get("isSynthetic") is True and loaded:
                text = _text(list(_blocks(event, "text")))
                if text:
                    texts.append((loaded.pop(0), text))
        return texts

    def skill_evidence_bytes(self, relative, staged):
        if relative.name != "SKILL.md" or not staged.startswith(b"---\n"):
            return staged
        # Claude shows the SKILL.md body without its frontmatter.
        return staged.partition(b"\n---\n")[2].lstrip(b"\n")

    def external_tool_attempts(self, events):
        return tuple(
            sequence
            for sequence, event in enumerate(events, 1)
            if any(_is_external_tool(block.get("name")) for block in _blocks(event, "tool_use"))
            or any(_is_external_tool(denial.get("tool_name")) for denial in _denials(event))
        )

    def permission_escalations(self, events):
        tools = _init_tools(events)
        return tuple(
            sequence
            for sequence, event in enumerate(events, 1)
            if any(
                denial.get("tool_name") not in tools
                and not _is_external_tool(denial.get("tool_name"))
                for denial in _denials(event)
            )
        )

    def forced_target_observed(self, record, targets):
        """Every target must load through Skill, with its body captured, before other tools."""
        subject = record.get("subject", {})
        if not isinstance(subject, dict):
            return False
        events = subject.get("events", [])
        captures = subject.get("captured_skill_files", [])
        if not isinstance(events, list) or not isinstance(captures, list):
            return False
        if not targets or not all(isinstance(target, dict) for target in targets):
            return False
        wanted = {target.get("skill"): target for target in targets}
        if None in wanted or len(wanted) != len(targets):
            return False
        remaining = set(wanted)
        skill_calls: dict[object, str] = {}
        for event in events:
            if not isinstance(event, dict):
                continue
            if event.get("type") == "assistant":
                for block in _blocks(event, "tool_use"):
                    if block.get("name") != "Skill":
                        return False
                    tool_input = block.get("input")
                    skill = tool_input.get("skill") if isinstance(tool_input, dict) else None
                    if isinstance(skill, str):
                        skill_calls[block.get("id")] = skill.removeprefix("chrisbanes-skills:")
            elif event.get("type") == "user":
                for block in _blocks(event, "tool_result"):
                    tool_id = block.get("tool_use_id")
                    skill = skill_calls.get(tool_id)
                    if (
                        skill in remaining
                        and not block.get("is_error")
                        and _captured(captures, wanted[skill], tool_id)
                    ):
                        remaining.discard(skill)
                if not remaining:
                    return True
        return False

    def forced_instruction(self, case: EvalCase) -> str:
        skills = ", ".join(f"`{skill}`" for skill in case.target_skills)
        dependencies = ", ".join(f"`{skill}`" for skill in case.constant_skills)
        return (
            f"\n\nInvoke each of the following skill(s) through the Skill tool: {skills}. "
            "Invoke every one of them before any repository inspection or other action."
            "\n\nIn the final `skills_used`, include each of these exact public "
            f"targets whose entrypoint you read and followed: [{skills}]. "
            "Omit only these exact evaluator-owned dependency names: "
            f"[{dependencies}]. Exclusions are exact names, not prefixes."
        )

    def build_judge_command(
        self, packet_path, repo_root, config, *, executable, skill_paths
    ):
        raise NotImplementedError("the Claude judge command is not implemented yet")
