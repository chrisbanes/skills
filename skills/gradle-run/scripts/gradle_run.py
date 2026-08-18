#!/usr/bin/env python3
"""Run Gradle commands with bounded diagnostics and wrapper-owned logs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


MAX_SUMMARY_BYTES = 16_384
MAX_SUMMARY_LINES = 64
MAX_DIAGNOSTICS = 8
MAX_FAILED_TASKS = 16
MAX_FAILED_TASK_BYTES = 512
MAX_EXCERPT_LINES = 12
MAX_EXCERPT_LINE_BYTES = 512
HEARTBEAT_DELAYS = (30.0, 60.0, 120.0, 300.0)
WORKFLOW_ID = re.compile(r"[a-z0-9]{32}\Z")
ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
FAILED_TASK = re.compile(r"^> Task (:[^\s]+) FAILED$", re.MULTILINE)
WARNING = re.compile(r"\bwarning\b", re.IGNORECASE)
FAILURE = re.compile(r"(?:^FAILURE:|^\* What went wrong:|^e:|\berror:)", re.IGNORECASE)


def default_root() -> Path:
    return Path(tempfile.gettempdir()) / "gradle-run"


def heartbeat_due(elapsed: float, next_index: int) -> bool:
    return next_index < len(HEARTBEAT_DELAYS) and elapsed >= HEARTBEAT_DELAYS[next_index]


def normalize(text: str) -> str:
    return " ".join(ANSI_ESCAPE.sub("", text).split())


def fingerprint(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def shortened(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[: max_bytes - 3].decode("utf-8", errors="ignore") + "..."


def managed_root(root: Path) -> Path:
    resolved_root = root.resolve(strict=False)
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved_root.relative_to(temporary_root)
    except ValueError as error:
        raise ValueError("managed root must be inside the OS temporary directory") from error
    return resolved_root


def workflow_path(root: Path, workflow: str) -> Path:
    if not WORKFLOW_ID.fullmatch(workflow):
        raise ValueError("invalid workflow identifier")
    root = managed_root(root)
    candidate = root / workflow
    if candidate.resolve(strict=False).parent != root:
        raise ValueError("invalid workflow path")
    return candidate


def read_ledger(directory: Path) -> dict[str, Any]:
    path = directory / "ledger.json"
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("managed workflow ledger is unavailable") from error
    if ledger.get("workflow") != directory.name or not isinstance(ledger.get("runs"), list):
        raise ValueError("managed workflow ledger is invalid")
    return ledger


def write_ledger(directory: Path, ledger: dict[str, Any]) -> None:
    temporary = directory / "ledger.json.tmp"
    temporary.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(directory / "ledger.json")


def create_workflow(root: Path) -> int:
    root = managed_root(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    for _ in range(10):
        workflow = secrets.token_hex(16)
        directory = root / workflow
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            continue
        write_ledger(
            directory,
            {
                "version": 1,
                "workflow": workflow,
                "runs": [],
                "failure_fingerprints": {},
                "warning_fingerprints": {},
            },
        )
        print(json.dumps({"workflow": workflow, "directory": str(directory)}, sort_keys=True))
        return 0
    print("could not create a unique workflow", file=sys.stderr)
    return 1


def extract_diagnostics(log: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    text = ANSI_ESCAPE.sub("", log.read_text(encoding="utf-8", errors="replace"))
    failed_tasks = list(dict.fromkeys(FAILED_TASK.findall(text)))
    lines = [normalize(raw_line) for raw_line in text.splitlines()]
    warnings: list[str] = []
    failures: list[str] = []
    excerpts: list[str] = []
    for line in lines:
        if not line:
            continue
        if WARNING.search(line):
            warnings.append(line)
        if (WARNING.search(line) or FAILURE.search(line) or " FAILED" in line) and len(excerpts) < MAX_EXCERPT_LINES:
            excerpts.append(shortened(line, MAX_EXCERPT_LINE_BYTES))
    if any(line.startswith("* What went wrong:") for line in lines):
        index = 0
        while index < len(lines):
            if not lines[index].startswith("* What went wrong:"):
                index += 1
                continue
            block = [lines[index]]
            index += 1
            while index < len(lines) and not lines[index].startswith("* "):
                if lines[index]:
                    block.append(lines[index])
                index += 1
            failures.append("\n".join(block))
    else:
        failures = [line for line in lines if line and FAILURE.search(line)]
    if not excerpts:
        excerpts = [
            shortened(normalize(line), MAX_EXCERPT_LINE_BYTES)
            for line in text.splitlines()[-MAX_EXCERPT_LINES:]
            if normalize(line)
        ]
    return failed_tasks, warnings, failures, excerpts[:MAX_EXCERPT_LINES]


def compact_fingerprints(lines: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for line in lines:
        value = fingerprint(line)
        item = result.setdefault(value, {"count": 0, "excerpt": shortened(normalize(line), 256)})
        item["count"] += 1
    return result


def summary_fingerprints(items: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"fingerprint": value, "count": item["count"], "excerpt": item["excerpt"]}
        for value, item in list(items.items())[:MAX_DIAGNOSTICS]
    ]


def merge_fingerprints(
    ledger: dict[str, Any], key: str, current: dict[str, dict[str, Any]]
) -> None:
    history = ledger.setdefault(key, {})
    for value, item in current.items():
        stored = history.setdefault(value, {"occurrences": 0, "excerpt": item["excerpt"]})
        stored["occurrences"] += item["count"]


def display_command(command: list[str]) -> str:
    return shortened(" ".join(command), 1024)


def summarize_failed_tasks(tasks: list[str]) -> tuple[list[str], bool]:
    summarized = [shortened(task, MAX_FAILED_TASK_BYTES) for task in tasks[:MAX_FAILED_TASKS]]
    truncated = len(tasks) > MAX_FAILED_TASKS or summarized != tasks[:MAX_FAILED_TASKS]
    return summarized, truncated


def effective_command(command: list[str]) -> list[str]:
    """Add safe Gradle defaults without overriding an explicit scan choice."""
    if Path(command[0]).name not in {"gradle", "gradlew"}:
        raise ValueError("command must start with a Gradle launcher")
    effective = list(command)
    defaults: list[str] = []
    if "--console" not in effective and not any(item.startswith("--console=") for item in effective):
        defaults.append("--console=plain")
    if "--scan" not in effective and "--no-scan" not in effective:
        defaults.append("--no-scan")
    try:
        separator = effective.index("--", 1)
    except ValueError:
        effective.extend(defaults)
    else:
        effective[separator:separator] = defaults
    return effective


def emit_summary(summary: dict[str, Any]) -> None:
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_SUMMARY_BYTES:
        summary["excerpt"] = []
        summary["warning_fingerprints"] = summary["warning_fingerprints"][:2]
        summary["failure_fingerprints"] = summary["failure_fingerprints"][:2]
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_SUMMARY_BYTES:
        summary["command"] = shortened(summary["command"], 256)
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_SUMMARY_BYTES:
        summary = {
            "command": shortened(str(summary.get("command", "")), 128),
            "exit_status": summary.get("exit_status"),
            "failed_tasks": list(summary.get("failed_tasks", []))[:2],
            "log": shortened(str(summary.get("log", "")), 256),
            "summary_truncated": True,
        }
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    print(encoded.decode("utf-8"))


def run_command(root: Path, arguments: argparse.Namespace) -> int:
    directory = workflow_path(root, arguments.workflow)
    ledger = read_ledger(directory)
    command = list(arguments.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        raise ValueError("missing command; refusing direct Gradle fallback")
    if not arguments.question.strip():
        raise ValueError("verification question must be non-empty")
    command = effective_command(command)
    if "/" not in command[0] and shutil.which(command[0]) is None:
        emit_summary({"launch_error": "command not found", "command": display_command(command)})
        return 127

    prior_failures = set(ledger.get("failure_fingerprints", {}))
    repeated_command = any(entry.get("command") == command for entry in ledger["runs"])
    sequence = len(ledger["runs"]) + 1
    log = directory / f"{sequence:04d}.log"
    started = time.monotonic()
    try:
        with log.open("wb") as output:
            child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
            next_heartbeat_index = 0
            while child.poll() is None:
                now = time.monotonic()
                elapsed = now - started
                if heartbeat_due(elapsed, next_heartbeat_index):
                    print(
                        f"gradle-run: still running {sequence:04d} ({elapsed:.0f}s); output is in managed log",
                        file=sys.stderr,
                        flush=True,
                    )
                    next_heartbeat_index += 1
                time.sleep(0.05)
            exit_status = child.returncode
    except OSError as error:
        log.unlink(missing_ok=True)
        emit_summary({"launch_error": str(error), "command": display_command(command)})
        return 125

    elapsed = time.monotonic() - started
    failed_tasks, warnings, failures, excerpt = extract_diagnostics(log)
    summarized_failed_tasks, failed_tasks_truncated = summarize_failed_tasks(failed_tasks)
    warning_items = compact_fingerprints(warnings)
    failure_items = compact_fingerprints(failures)
    repeated_primary_failure = bool(failure_items and next(iter(failure_items)) in prior_failures)
    merge_fingerprints(ledger, "warning_fingerprints", warning_items)
    merge_fingerprints(ledger, "failure_fingerprints", failure_items)
    ledger["runs"].append(
        {
            "sequence": sequence,
            "scope": arguments.scope,
            "question": arguments.question,
            "command": command,
            "elapsed_seconds": round(elapsed, 3),
            "exit_status": exit_status,
            "log": log.name,
            "failure_fingerprints": list(failure_items),
            "warning_fingerprints": list(warning_items),
        }
    )
    write_ledger(directory, ledger)
    emit_summary(
        {
            "command": display_command(command),
            "elapsed_seconds": round(elapsed, 3),
            "exit_status": exit_status,
            "excerpt": excerpt,
            "failed_tasks": summarized_failed_tasks,
            "failed_tasks_truncated": failed_tasks_truncated,
            "failure_fingerprints": summary_fingerprints(failure_items),
            "log": str(log),
            "repeated_command": repeated_command,
            "repeated_primary_failure": repeated_primary_failure,
            "scope": arguments.scope,
            "warning_fingerprints": summary_fingerprints(warning_items),
        }
    )
    return exit_status


def finish_workflow(root: Path, workflow: str) -> int:
    directory = workflow_path(root, workflow)
    if not directory.exists():
        print(json.dumps({"already_finished": True, "finished": workflow}, sort_keys=True))
        return 0
    read_ledger(directory)
    shutil.rmtree(directory)
    print(json.dumps({"finished": workflow}, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=default_root())
    commands = result.add_subparsers(dest="operation", required=True)
    commands.add_parser("create")
    run = commands.add_parser("run")
    run.add_argument("--workflow", required=True)
    run.add_argument("--scope", choices=("broad", "targeted"), required=True)
    run.add_argument("--question", required=True)
    run.add_argument("command", nargs=argparse.REMAINDER)
    finish = commands.add_parser("finish")
    finish.add_argument("--workflow", required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        if arguments.operation == "create":
            return create_workflow(arguments.root)
        if arguments.operation == "run":
            return run_command(arguments.root, arguments)
        return finish_workflow(arguments.root, arguments.workflow)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
