#!/usr/bin/env python3
"""Run Gradle commands with bounded diagnostics and wrapper-owned logs."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


MAX_SUMMARY_BYTES = 16_384
MAX_DIAGNOSTICS = 8
MAX_STORED_FINGERPRINTS = 256
MAX_LEDGER_RUNS = 64
MAX_FAILED_TASKS = 16
MAX_FAILED_TASK_BYTES = 512
MAX_EXCERPT_LINES = 12
MAX_EXCERPT_LINE_BYTES = 512
MAX_FAILURE_BLOCK_LINES = 64
HEARTBEAT_DELAYS = (30.0, 60.0, 120.0, 300.0)
WORKFLOW_ID = re.compile(r"[a-z0-9]{32}\Z")
ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
FAILED_TASK = re.compile(r"^> Task (:[^\s]+) FAILED$", re.MULTILINE)
WARNING = re.compile(r"\bwarning\b", re.IGNORECASE)
FAILURE = re.compile(r"(?:^FAILURE:|^\* What went wrong:|^e:|\berror:)", re.IGNORECASE)


def default_root() -> Path:
    return Path(tempfile.gettempdir()) / "gradle-run"


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
                "run_count": 0,
                "command_fingerprints": {},
                "failure_fingerprints": {},
                "warning_fingerprints": {},
            },
        )
        print(json.dumps({"workflow": workflow, "directory": str(directory)}, sort_keys=True))
        return 0
    print("could not create a unique workflow", file=sys.stderr)
    return 1


@dataclass
class Diagnostics:
    failed_tasks: list[str]
    failed_tasks_truncated: bool
    warning_fingerprints: dict[str, dict[str, Any]]
    warning_fingerprints_truncated: int
    failure_fingerprints: dict[str, dict[str, Any]]
    failure_fingerprints_truncated: int
    excerpt: list[str]


class ProcessInterrupted(Exception):
    def __init__(self, signum: int) -> None:
        super().__init__(f"received signal {signum}")
        self.signum = signum


def add_fingerprint(items: dict[str, dict[str, Any]], text: str) -> int:
    value = fingerprint(text)
    if value in items:
        items[value]["count"] += 1
        return 0
    if len(items) >= MAX_STORED_FINGERPRINTS:
        return 1
    items[value] = {"count": 1, "excerpt": shortened(normalize(text), 256)}
    return 0


def extract_diagnostics(log: Path) -> Diagnostics:
    failed_tasks: list[str] = []
    failed_task_values: set[str] = set()
    failed_tasks_truncated = False
    warnings: dict[str, dict[str, Any]] = {}
    warning_overflow = 0
    standalone_failures: dict[str, dict[str, Any]] = {}
    standalone_failure_overflow = 0
    failure_blocks: dict[str, dict[str, Any]] = {}
    failure_block_overflow = 0
    saw_failure_block = False
    failure_block: list[str] | None = None
    failure_block_truncated = False
    excerpts: list[str] = []
    tail: deque[str] = deque(maxlen=MAX_EXCERPT_LINES)

    def finish_failure_block() -> None:
        nonlocal failure_block, failure_block_overflow, failure_block_truncated
        if failure_block is None:
            return
        if failure_block_truncated:
            failure_block.append("... diagnostic block truncated ...")
        failure_block_overflow += add_fingerprint(failure_blocks, "\n".join(failure_block))
        failure_block = None
        failure_block_truncated = False

    with log.open(encoding="utf-8", errors="replace") as lines:
        for raw_line in lines:
            line = normalize(raw_line)
            if not line:
                continue
            bounded_line = shortened(line, MAX_EXCERPT_LINE_BYTES)
            tail.append(bounded_line)

            task = FAILED_TASK.fullmatch(line)
            if task and task.group(1) not in failed_task_values:
                if len(failed_tasks) < MAX_FAILED_TASKS:
                    value = task.group(1)
                    failed_task_values.add(value)
                    shortened_value = shortened(value, MAX_FAILED_TASK_BYTES)
                    failed_tasks.append(shortened_value)
                    failed_tasks_truncated |= shortened_value != value
                else:
                    failed_tasks_truncated = True

            is_warning = bool(WARNING.search(line))
            is_failure = bool(FAILURE.search(line) or " FAILED" in line)
            if is_warning:
                warning_overflow += add_fingerprint(warnings, line)
            if (is_warning or is_failure) and len(excerpts) < MAX_EXCERPT_LINES:
                excerpts.append(bounded_line)

            if line.startswith("* What went wrong:"):
                finish_failure_block()
                saw_failure_block = True
                failure_block = [line]
                continue
            if failure_block is not None:
                if line.startswith("* "):
                    finish_failure_block()
                else:
                    if len(failure_block) < MAX_FAILURE_BLOCK_LINES:
                        failure_block.append(bounded_line)
                    else:
                        failure_block_truncated = True
                    continue
            if FAILURE.search(line):
                standalone_failure_overflow += add_fingerprint(standalone_failures, line)

    finish_failure_block()
    failures = failure_blocks if saw_failure_block else standalone_failures
    failure_overflow = (
        failure_block_overflow if saw_failure_block else standalone_failure_overflow
    )
    return Diagnostics(
        failed_tasks=failed_tasks,
        failed_tasks_truncated=failed_tasks_truncated,
        warning_fingerprints=warnings,
        warning_fingerprints_truncated=warning_overflow,
        failure_fingerprints=failures,
        failure_fingerprints_truncated=failure_overflow,
        excerpt=excerpts or list(tail),
    )


def summary_fingerprints(items: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"fingerprint": value, "count": item["count"], "excerpt": item["excerpt"]}
        for value, item in list(items.items())[:MAX_DIAGNOSTICS]
    ]


def merge_fingerprints(
    ledger: dict[str, Any],
    key: str,
    current: dict[str, dict[str, Any]],
    truncated_occurrences: int,
) -> None:
    history = ledger.setdefault(key, {})
    for value, item in current.items():
        if value in history:
            history[value]["occurrences"] += item["count"]
        elif len(history) < MAX_STORED_FINGERPRINTS:
            history[value] = {"occurrences": item["count"], "excerpt": item["excerpt"]}
        else:
            truncated_occurrences += item["count"]
    ledger[f"{key}_truncated_occurrences"] = (
        ledger.get(f"{key}_truncated_occurrences", 0) + truncated_occurrences
    )


def record_command(ledger: dict[str, Any], command: list[str]) -> bool:
    value = hashlib.sha256(
        json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    history = ledger.setdefault("command_fingerprints", {})
    if value in history:
        history[value] += 1
        return True
    if len(history) < MAX_STORED_FINGERPRINTS:
        history[value] = 1
    else:
        ledger["command_fingerprints_truncated"] = (
            ledger.get("command_fingerprints_truncated", 0) + 1
        )
    return False


def append_run(ledger: dict[str, Any], entry: dict[str, Any]) -> None:
    ledger["run_count"] = entry["sequence"]
    ledger["runs"].append(entry)
    overflow = len(ledger["runs"]) - MAX_LEDGER_RUNS
    if overflow > 0:
        del ledger["runs"][:overflow]
        ledger["runs_truncated"] = ledger.get("runs_truncated", 0) + overflow


def display_command(command: list[str]) -> str:
    return shortened(" ".join(command), 1024)


def effective_command(command: list[str]) -> list[str]:
    """Add safe Gradle defaults without overriding an explicit scan choice."""
    if Path(command[0]).name not in {"gradle", "gradlew"}:
        raise ValueError("command must start with a Gradle launcher")
    effective = list(command)
    try:
        separator = effective.index("--", 1)
    except ValueError:
        separator = len(effective)
    gradle_arguments = effective[:separator]
    defaults: list[str] = []
    if "--console" not in gradle_arguments and not any(
        item.startswith("--console=") for item in gradle_arguments
    ):
        defaults.append("--console=plain")
    if "--scan" not in gradle_arguments and "--no-scan" not in gradle_arguments:
        defaults.append("--no-scan")
    effective[separator:separator] = defaults
    return effective


def emit_summary(summary: dict[str, Any]) -> None:
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_limit = MAX_SUMMARY_BYTES - 1
    if len(encoded) > payload_limit:
        summary["excerpt"] = []
        summary["warning_fingerprints"] = summary.get("warning_fingerprints", [])[:2]
        summary["failure_fingerprints"] = summary.get("failure_fingerprints", [])[:2]
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > payload_limit:
        summary["command"] = shortened(str(summary.get("command", "")), 256)
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > payload_limit:
        summary = {
            "command": shortened(str(summary.get("command", "")), 128),
            "exit_status": summary.get("exit_status"),
            "failed_tasks": list(summary.get("failed_tasks", []))[:2],
            "log": shortened(str(summary.get("log", "")), 256),
            "summary_truncated": True,
        }
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    print(encoded.decode("utf-8"))


def emit_heartbeat(child: subprocess.Popen[bytes], sequence: int, delay: float) -> None:
    if child.poll() is None:
        print(
            f"gradle-run: still running {sequence:04d} ({delay:.0f}s); output is in managed log",
            file=sys.stderr,
            flush=True,
        )


def wait_for_child(child: subprocess.Popen[bytes], sequence: int) -> int:
    timers = [
        threading.Timer(delay, emit_heartbeat, args=(child, sequence, delay))
        for delay in HEARTBEAT_DELAYS
    ]
    for timer in timers:
        timer.daemon = True
        timer.start()
    try:
        return child.wait()
    finally:
        for timer in timers:
            timer.cancel()
        for timer in timers:
            timer.join()


def terminate_child(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


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
    prior_failures = set(ledger.get("failure_fingerprints", {}))
    repeated_command = record_command(ledger, command)
    sequence = ledger.get("run_count", len(ledger["runs"])) + 1
    log = directory / f"{sequence:04d}.log"
    started = time.monotonic()
    try:
        output = log.open("wb")
    except OSError as error:
        emit_summary({"launch_error": str(error), "command": display_command(command)})
        return 125

    child: subprocess.Popen[bytes] | None = None
    interruption: ProcessInterrupted | None = None
    launch_error: OSError | None = None
    exit_status = 125
    with output:
        previous_sigterm = signal.getsignal(signal.SIGTERM)

        def interrupt_child(signum: int, _frame: Any) -> None:
            raise ProcessInterrupted(signum)

        signal.signal(signal.SIGTERM, interrupt_child)
        try:
            try:
                child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
            except OSError as error:
                launch_error = error
            else:
                exit_status = wait_for_child(child, sequence)
        except ProcessInterrupted as error:
            interruption = error
            if child is not None:
                terminate_child(child)
        except BaseException:
            if child is not None:
                terminate_child(child)
            raise
        finally:
            signal.signal(signal.SIGTERM, previous_sigterm)

    if launch_error is not None:
        log.unlink(missing_ok=True)
        emit_summary(
            {"launch_error": str(launch_error), "command": display_command(command)}
        )
        return 125

    elapsed = time.monotonic() - started
    if interruption is not None:
        exit_status = 128 + interruption.signum
        append_run(
            ledger,
            {
                "sequence": sequence,
                "scope": arguments.scope,
                "question": shortened(arguments.question, 1024),
                "command": display_command(command),
                "elapsed_seconds": round(elapsed, 3),
                "exit_status": exit_status,
                "interrupted_signal": interruption.signum,
                "log": log.name,
                "failure_fingerprints": [],
                "warning_fingerprints": [],
            },
        )
        write_ledger(directory, ledger)
        emit_summary(
            {
                "command": display_command(command),
                "elapsed_seconds": round(elapsed, 3),
                "exit_status": exit_status,
                "interrupted_signal": interruption.signum,
                "log": str(log),
                "repeated_command": repeated_command,
                "scope": arguments.scope,
            }
        )
        return exit_status

    diagnostics = extract_diagnostics(log)
    warning_items = diagnostics.warning_fingerprints
    failure_items = diagnostics.failure_fingerprints
    repeated_primary_failure = bool(failure_items and next(iter(failure_items)) in prior_failures)
    merge_fingerprints(
        ledger,
        "warning_fingerprints",
        warning_items,
        diagnostics.warning_fingerprints_truncated,
    )
    merge_fingerprints(
        ledger,
        "failure_fingerprints",
        failure_items,
        diagnostics.failure_fingerprints_truncated,
    )
    append_run(
        ledger,
        {
            "sequence": sequence,
            "scope": arguments.scope,
            "question": shortened(arguments.question, 1024),
            "command": display_command(command),
            "elapsed_seconds": round(elapsed, 3),
            "exit_status": exit_status,
            "log": log.name,
            "failure_fingerprints": list(failure_items)[:MAX_DIAGNOSTICS],
            "warning_fingerprints": list(warning_items)[:MAX_DIAGNOSTICS],
        },
    )
    write_ledger(directory, ledger)
    emit_summary(
        {
            "command": display_command(command),
            "elapsed_seconds": round(elapsed, 3),
            "exit_status": exit_status,
            "excerpt": diagnostics.excerpt,
            "failed_tasks": diagnostics.failed_tasks,
            "failed_tasks_truncated": diagnostics.failed_tasks_truncated,
            "failure_fingerprints": summary_fingerprints(failure_items),
            "log": str(log),
            "repeated_command": repeated_command,
            "repeated_primary_failure": repeated_primary_failure,
            "scope": arguments.scope,
            "warning_fingerprints": summary_fingerprints(warning_items),
            "warning_fingerprints_truncated": diagnostics.warning_fingerprints_truncated,
            "failure_fingerprints_truncated": diagnostics.failure_fingerprints_truncated,
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
