#!/usr/bin/env python3
"""Run Gradle commands with bounded diagnostics and wrapper-owned logs."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import errno
from collections import deque
from dataclasses import dataclass
import hashlib
import json
import math
import os
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
MAX_RECOVERY_REASON_BYTES = 1024
RUN_IDENTITY_FIELDS = (
    "sequence", "wrapper_pid", "child_pid", "started_at", "cwd", "scope", "question", "command", "log",
)
HEARTBEAT_DELAYS = (30.0, 60.0, 120.0, 300.0)
WORKFLOW_ID = re.compile(r"[a-z0-9]{32}\Z")
ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
FAILED_TASK = re.compile(r"^> Task (:[^\s]+) FAILED$", re.MULTILINE)
WARNING = re.compile(r"(?:\bwarning\b|\bdeprecat(?:ed|ion)\b|^w:)", re.IGNORECASE)
FAILURE = re.compile(r"(?:^FAILURE:|^\* What went wrong:|^e:|\berror:)", re.IGNORECASE)
SOURCE_FAILURE = re.compile(r"(?:^e:|\berror:)", re.IGNORECASE)
AUTHORIZATION_VALUE = re.compile(
    r"(\bauthorization\s*:\s*)(?:bearer\s+)?[^\r\n]+", re.IGNORECASE
)
SECRET_ASSIGNMENT = re.compile(
    r"(\b[\w.-]*(?:password|passwd|token|secret|credential|api[-_.]?key)"
    r"[\w.-]*\s*[:=]\s*)([^\r\n]+)",
    re.IGNORECASE,
)
URL_PASSWORD = re.compile(r"(://[^:/\s]+:)([^@\s]+)(@)")


def default_root() -> Path:
    return Path(tempfile.gettempdir()) / "gradle-run"


def normalize(text: str) -> str:
    return " ".join(ANSI_ESCAPE.sub("", text).split())


def redact(text: str) -> str:
    text = AUTHORIZATION_VALUE.sub(r"\1[REDACTED]", text)
    text = SECRET_ASSIGNMENT.sub(r"\1[REDACTED]", text)
    return URL_PASSWORD.sub(r"\1[REDACTED]\3", text)


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


def finished_path(root: Path, workflow: str) -> Path:
    directory = workflow_path(root, workflow)
    return directory.with_name(f"{workflow}.finished")


def lock_path(root: Path, workflow: str) -> Path:
    directory = workflow_path(root, workflow)
    return directory.with_name(f"{workflow}.lock")


class WorkflowBusy(ValueError):
    pass


class WorkflowLock:
    def __init__(self, path: Path, *, read_only: bool = False) -> None:
        self.path = path
        self.read_only = read_only
        self.file: Any | None = None

    def __enter__(self) -> None:
        try:
            mode = ("rb" if os.name == "posix" else "r+b") if self.read_only else "a+b"
            self.file = self.path.open(mode)
            if not self.read_only and self.file.tell() == 0:
                self.file.write(b"\0")
                self.file.flush()
            self.file.seek(0)
        except OSError as error:
            if self.file is not None:
                self.file.close()
            raise ValueError("workflow lock is unavailable") from error

        try:
            if os.name == "posix":
                import fcntl

                mode = fcntl.LOCK_SH if self.read_only else fcntl.LOCK_EX
                fcntl.flock(self.file.fileno(), mode | fcntl.LOCK_NB)
            elif os.name == "nt":
                import msvcrt

                mode = msvcrt.LK_NBRLCK if self.read_only else msvcrt.LK_NBLCK
                msvcrt.locking(self.file.fileno(), mode, 1)
            else:
                raise ValueError("workflow locking is unsupported on this platform")
        except ValueError:
            self.file.close()
            self.file = None
            raise
        except OSError as error:
            self.file.close()
            self.file = None
            if error.errno in (errno.EACCES, errno.EAGAIN):
                raise WorkflowBusy("workflow is busy") from error
            raise ValueError("workflow lock is unavailable") from error

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        if self.file is None:
            return
        try:
            if os.name == "posix":
                import fcntl

                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            elif os.name == "nt":
                import msvcrt

                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self.file.close()
            self.file = None


def read_finished(path: Path, workflow: str) -> bool:
    if path.is_symlink():
        raise ValueError("managed workflow tombstone is invalid")
    try:
        value = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    except OSError as error:
        raise ValueError("managed workflow tombstone is unavailable") from error
    if value != f"{workflow}\n":
        raise ValueError("managed workflow tombstone is invalid")
    return True


def write_finished(path: Path, workflow: str) -> None:
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(f"{workflow}\n", encoding="utf-8")
    temporary.replace(path)


def finite_json_number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite JSON number")
    return number


def read_ledger(directory: Path) -> dict[str, Any]:
    path = directory / "ledger.json"
    try:
        ledger = json.loads(
            path.read_text(encoding="utf-8"),
            parse_float=finite_json_number, parse_constant=finite_json_number,
        )
    except (OSError, ValueError) as error:
        raise ValueError("managed workflow ledger is unavailable") from error
    if (
        not isinstance(ledger, dict)
        or ledger.get("workflow") != directory.name
        or not isinstance(ledger.get("runs"), list)
    ):
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
        if finished_path(root, workflow).exists():
            continue
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            continue
        with WorkflowLock(lock_path(root, workflow)):
            pass
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
    source_failures: dict[str, dict[str, Any]] = {}
    source_failure_overflow = 0
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
            line = redact(normalize(raw_line))
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
            if SOURCE_FAILURE.search(line):
                source_failure_overflow += add_fingerprint(source_failures, line)
            elif FAILURE.search(line):
                standalone_failure_overflow += add_fingerprint(standalone_failures, line)

    finish_failure_block()
    secondary_failures = failure_blocks if saw_failure_block else standalone_failures
    failure_overflow = source_failure_overflow + (
        failure_block_overflow if saw_failure_block else standalone_failure_overflow
    )
    failures = dict(source_failures)
    for value, item in secondary_failures.items():
        if len(failures) < MAX_STORED_FINGERPRINTS:
            failures[value] = item
        else:
            failure_overflow += item["count"]
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


def prune_logs(directory: Path, ledger: dict[str, Any]) -> None:
    retained = {
        run["log"]
        for run in ledger["runs"]
        if isinstance(run, dict) and isinstance(run.get("log"), str)
    }
    for log in directory.glob("*.log"):
        if log.is_file() and log.name not in retained:
            log.unlink(missing_ok=True)
    retained_locks = {
        f"{run['sequence']:04d}.{suffix}"
        for run in ledger["runs"]
        if isinstance(run, dict)
        and type(run.get("sequence")) is int
        and run["sequence"] > 0
        for suffix in ("run.lock", "recovery.run.lock")
    }
    for run_lock in directory.glob("*.run.lock"):
        if run_lock.name not in retained_locks:
            run_lock.unlink(missing_ok=True)


def display_command(command: list[str]) -> str:
    return shortened(" ".join(redact(argument) for argument in command), 1024)


def is_gradle_launcher(command: str) -> bool:
    name = Path(command).name
    return name == "gradle" or name.startswith("gradlew")


def effective_command(command: list[str]) -> list[str]:
    """Add safe Gradle defaults without overriding an explicit scan choice."""
    if not is_gradle_launcher(command[0]):
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


def bounded_summary(summary: dict[str, Any], max_bytes: int = MAX_SUMMARY_BYTES) -> dict[str, Any]:
    summary = dict(summary)
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_limit = max_bytes - 1
    if len(encoded) > payload_limit:
        summary["excerpt"] = []
        summary["warning_fingerprints"] = summary.get("warning_fingerprints", [])[:2]
        summary["failure_fingerprints"] = summary.get("failure_fingerprints", [])[:2]
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > payload_limit:
        summary["command"] = shortened(str(summary.get("command", "")), 256)
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > payload_limit:
        fallback = {
            "command": shortened(str(summary.get("command", "")), 128),
            "exit_status": summary.get("exit_status"),
            "failed_tasks": list(summary.get("failed_tasks", []))[:2],
            "log": shortened(str(summary.get("log", "")), 256),
            "summary_truncated": True,
        }
        for key in ("interrupted_signal", "launch_error"):
            if key in summary:
                fallback[key] = summary[key]
        summary = fallback
    return summary


def emit_summary(summary: dict[str, Any]) -> None:
    print(json.dumps(bounded_summary(summary), sort_keys=True, separators=(",", ":")))


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


def process_launch_options(platform: str) -> dict[str, Any]:
    if platform == "posix":
        return {"start_new_session": True}
    if platform == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    raise ValueError("isolated process groups are unsupported on this platform")


def terminate_child(
    child: subprocess.Popen[bytes], *, isolated_process_group: bool = False
) -> None:
    def terminate_direct_child() -> None:
        if child.poll() is not None:
            return
        child.terminate()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()

    def terminate_windows_tree() -> None:
        if child.poll() is not None:
            return
        try:
            child.send_signal(signal.CTRL_BREAK_EVENT)
        except OSError:
            pass
        try:
            subprocess.run(
                ["taskkill", "/PID", str(child.pid), "/T", "/F"],
                check=False,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()

    if not isolated_process_group:
        terminate_direct_child()
        return
    if os.name == "nt":
        terminate_windows_tree()
        return
    if os.name != "posix":
        terminate_direct_child()
        return

    process_group = child.pid

    def group_exists() -> bool:
        try:
            os.killpg(process_group, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        child.wait()
        return

    deadline = time.monotonic() + 5
    while group_exists() and time.monotonic() < deadline:
        child.poll()
        time.sleep(0.05)
    if group_exists():
        try:
            os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if child.poll() is None:
        child.wait()


def run_command(root: Path, arguments: argparse.Namespace) -> int:
    with WorkflowLock(lock_path(root, arguments.workflow)):
        return run_locked(root, arguments)


def run_locked(root: Path, arguments: argparse.Namespace) -> int:
    directory = workflow_path(root, arguments.workflow)
    ledger = require_settled_ledger(directory)
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
    with WorkflowLock(directory / f"{sequence:04d}.run.lock"):
        log = directory / f"{sequence:04d}.log"
        started = time.monotonic()
        output: Any | None = None

        child: subprocess.Popen[bytes] | None = None
        interruption: ProcessInterrupted | None = None
        launch_error: OSError | None = None
        exit_status = 125
        cleanup_started = False
        pending_signal: int | None = None
        handled_signals = (signal.SIGINT, signal.SIGTERM)
        previous_handlers = {
            handled_signal: signal.getsignal(handled_signal)
            for handled_signal in handled_signals
        }

        def interrupt_child(signum: int, _frame: Any) -> None:
            nonlocal pending_signal
            if cleanup_started:
                return
            if child is None:
                pending_signal = pending_signal or signum
                return
            raise ProcessInterrupted(signum)

        for handled_signal in handled_signals:
            signal.signal(handled_signal, interrupt_child)
        try:
            try:
                active_run = {
                    "sequence": sequence,
                    "wrapper_pid": os.getpid(),
                    "child_pid": None,
                    "started_at": time.time(),
                    "cwd": shortened(os.getcwd(), 1024),
                    "scope": arguments.scope,
                    "question": shortened(redact(arguments.question), 1024),
                    "command": display_command(command),
                    "log": log.name,
                }
                ledger["active_run"] = active_run
                write_ledger(directory, ledger)
                try:
                    output = log.open("wb")
                except OSError as error:
                    launch_error = error
                else:
                    with output:
                        try:
                            child = subprocess.Popen(
                                command,
                                stdout=output,
                                stderr=subprocess.STDOUT,
                                **process_launch_options(os.name),
                            )
                        except OSError as error:
                            launch_error = error
                        else:
                            active_run["child_pid"] = child.pid
                            write_ledger(directory, ledger)
                            if pending_signal is not None:
                                raise ProcessInterrupted(pending_signal)
                            exit_status = wait_for_child(child, sequence)
                if pending_signal is not None:
                    raise ProcessInterrupted(pending_signal)
                cleanup_started = True
            except ProcessInterrupted as error:
                cleanup_started = True
                interruption = error
                if child is not None:
                    terminate_child(child, isolated_process_group=True)
            except BaseException:
                cleanup_started = True
                if child is not None:
                    terminate_child(child, isolated_process_group=True)
                raise

            elapsed = time.monotonic() - started
            diagnostics = (
                extract_diagnostics(log) if launch_error is None
                else Diagnostics([], False, {}, 0, {}, 0, [])
            )
            warning_items = diagnostics.warning_fingerprints
            failure_items = diagnostics.failure_fingerprints
            repeated_primary_failure = bool(
                failure_items and next(iter(failure_items)) in prior_failures
            )
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
            interrupted_signal = interruption.signum if interruption is not None else (
                -exit_status if exit_status < 0 else None
            )
            if interruption is not None:
                exit_status = 128 + interruption.signum
            summary = {
                "command": display_command(command),
                "elapsed_seconds": round(elapsed, 3),
                "exit_status": exit_status,
                "excerpt": diagnostics.excerpt,
                "failed_tasks": diagnostics.failed_tasks,
                "failed_tasks_truncated": diagnostics.failed_tasks_truncated,
                "failure_fingerprints": summary_fingerprints(failure_items),
                "failure_fingerprints_truncated": diagnostics.failure_fingerprints_truncated,
                "log": str(log),
                "repeated_command": repeated_command,
                "repeated_primary_failure": repeated_primary_failure,
                "scope": arguments.scope,
                "warning_fingerprints": summary_fingerprints(warning_items),
                "warning_fingerprints_truncated": diagnostics.warning_fingerprints_truncated,
            }
            if interrupted_signal is not None:
                summary["interrupted_signal"] = interrupted_signal
            if launch_error is not None:
                summary["launch_error"] = shortened(redact(str(launch_error)), 1024)
                if output is not None:
                    log.unlink(missing_ok=True)
            # Leave room for status identity within the same output bound.
            summary = bounded_summary(summary, MAX_SUMMARY_BYTES // 2)
            entry = {
                **active_run,
                "state": "interrupted" if interrupted_signal is not None else "completed",
                "elapsed_seconds": round(elapsed, 3),
                "exit_status": exit_status,
                "failure_fingerprints": list(failure_items)[:MAX_DIAGNOSTICS],
                "warning_fingerprints": list(warning_items)[:MAX_DIAGNOSTICS],
                "result": summary,
            }
            if interrupted_signal is not None:
                entry["interrupted_signal"] = interrupted_signal
            append_run(ledger, entry)
            ledger.pop("active_run", None)
            write_ledger(directory, ledger)
            prune_logs(directory, ledger)
            emit_summary(summary)
            return exit_status
        finally:
            for handled_signal, previous_handler in previous_handlers.items():
                signal.signal(handled_signal, previous_handler)


def finish_workflow(root: Path, workflow: str) -> int:
    with WorkflowLock(lock_path(root, workflow)):
        return finish_locked(root, workflow)


def valid_stored_result(result: Any) -> bool:
    if not isinstance(result, dict) or type(result.get("exit_status")) is not int:
        return False
    for key in ("excerpt", "failed_tasks", "warning_fingerprints", "failure_fingerprints"):
        values = result.get(key, [])
        if not isinstance(values, list):
            return False
        if key in ("excerpt", "failed_tasks"):
            if not all(isinstance(value, str) for value in values):
                return False
        elif not all(
            isinstance(value, dict)
            and isinstance(value.get("fingerprint"), str)
            and type(value.get("count")) is int
            and value["count"] > 0
            and isinstance(value.get("excerpt"), str)
            for value in values
        ):
            return False
    # A stored result was already bounded before its atomic write.
    return len(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")) < MAX_SUMMARY_BYTES // 2


def valid_terminal_run(ledger: dict[str, Any], latest: Any) -> bool:
    if not (
        isinstance(latest, dict)
        and type(latest.get("sequence")) is int
        and latest["sequence"] > 0
        and type(ledger.get("run_count")) is int
        and latest["sequence"] == ledger.get("run_count")
    ):
        return False
    if latest.get("state") == "abandoned":
        reason = latest.get("recovery_reason")
        return (
            latest.keys() == {*RUN_IDENTITY_FIELDS, "state", "result", "recovery_reason"}
            and valid_run_identity(latest)
            and valid_bounded_text(reason, MAX_RECOVERY_REASON_BYTES)
            and latest.get("result") == {"outcome": "unknown"}
        )
    return (
        latest.get("state") in ("completed", "interrupted")
        and valid_stored_result(latest.get("result"))
        and type(latest.get("exit_status")) is int
        and latest["result"]["exit_status"] == latest["exit_status"]
        and (
            (latest["state"] == "completed"
             and latest["exit_status"] >= 0
             and "interrupted_signal" not in latest
             and "interrupted_signal" not in latest["result"])
            or (latest["state"] == "interrupted"
                and type(latest.get("interrupted_signal")) is int
                and type(latest["result"].get("interrupted_signal")) is int
                and latest["interrupted_signal"] == latest["result"]["interrupted_signal"] > 0
                and latest["interrupted_signal"] in signal.valid_signals()
                and latest["exit_status"] in (-latest["interrupted_signal"], 128 + latest["interrupted_signal"]))
        )
    )


def settled_state(ledger: dict[str, Any]) -> str:
    if not ledger["runs"]:
        return "idle" if type(ledger.get("run_count")) is int and ledger["run_count"] == 0 else "uncertain"
    latest = ledger["runs"][-1]
    if valid_terminal_run(ledger, latest):
        return latest["state"]
    return "uncertain"


def require_settled_ledger(directory: Path) -> dict[str, Any]:
    ledger = read_ledger(directory)
    if ledger.get("active_run") is not None or settled_state(ledger) == "uncertain":
        raise ValueError("workflow has an uncertain run; inspect status before recovery")
    return ledger


def valid_pid(pid: Any) -> bool:
    maximum = 0xFFFFFFFF if os.name == "nt" else 0x7FFFFFFF
    return type(pid) is int and 0 < pid <= maximum


def valid_bounded_text(value: Any, max_bytes: int) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        return len(value.encode("utf-8")) <= max_bytes
    except UnicodeEncodeError:
        return False


def valid_run_identity(run: dict[str, Any]) -> bool:
    sequence = run.get("sequence")
    started = run.get("started_at")
    child = run.get("child_pid")
    return (
        type(sequence) is int and sequence > 0
        and valid_pid(run.get("wrapper_pid"))
        and "child_pid" in run
        and (child is None or (valid_pid(child) and child != run["wrapper_pid"]))
        and type(started) in (int, float) and 0 < started <= sys.float_info.max
        and run.get("scope") in ("targeted", "broad")
        and all(valid_bounded_text(run.get(key), 1024) for key in ("cwd", "question", "command"))
        and run.get("log") == f"{sequence:04d}.log"
    )


def valid_recovery_history(ledger: dict[str, Any]) -> bool:
    count = ledger.get("run_count")
    truncated = ledger.get("runs_truncated", 0)
    runs = ledger["runs"]
    return (
        type(ledger.get("version")) is int and ledger["version"] == 1
        and type(count) is int and type(truncated) is int and truncated >= 0
        and len(runs) == min(count, MAX_LEDGER_RUNS) and count == truncated + len(runs)
        and all(
            valid_terminal_run({"run_count": sequence}, entry)
            and entry.get("log") == f"{sequence:04d}.log"
            for sequence, entry in enumerate(runs, start=truncated + 1)
        )
    )


def windows_process_presence(pid: int) -> str:
    query_limited_information = 0x1000
    invalid_parameter = 87
    still_active = 259
    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.GetExitCodeProcess.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        handle = kernel.OpenProcess(query_limited_information, False, pid)
        if not handle:
            return "absent" if ctypes.get_last_error() == invalid_parameter else "unverifiable"
        exit_code = wintypes.DWORD()
        try:
            if kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)) and exit_code.value == still_active:
                return "live"
            # An exited handle can still refer to a process object for this PID.
            return "unverifiable"
        finally:
            kernel.CloseHandle(handle)
    except (AttributeError, OSError):
        return "unverifiable"


def process_presence(pid: int) -> str:
    if not valid_pid(pid):
        return "unverifiable"
    if os.name == "nt":
        return windows_process_presence(pid)
    if os.name != "posix":
        return "unverifiable"
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "absent"
    except OSError:
        return "unverifiable"
    return "live"


def recovery_marker(directory: Path, sequence: int) -> Path:
    return directory / f"{sequence:04d}.recovery.run.lock"


def recover_workflow(root: Path, arguments: argparse.Namespace) -> int:
    workflow = arguments.workflow
    sequence = arguments.sequence
    reason = arguments.reason.strip()
    if sequence <= 0 or not reason or not arguments.no_live_descendants:
        raise ValueError("recovery requires a positive sequence, a reason and confirmation of no live descendants")
    try:
        recovery_reason = shortened(redact(reason), MAX_RECOVERY_REASON_BYTES)
    except UnicodeEncodeError as error:
        raise ValueError("recovery reason must be valid UTF-8") from error
    directory = workflow_path(root, workflow)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("unknown or invalid workflow identifier")
    workflow_lock = lock_path(root, workflow)
    if workflow_lock.is_symlink():
        raise ValueError("workflow lock is invalid")
    with WorkflowLock(workflow_lock):
        ledger = read_ledger(directory)
        active = ledger.get("active_run")
        if (
            not isinstance(active, dict) or active.keys() != set(RUN_IDENTITY_FIELDS)
            or not valid_run_identity(active) or not valid_recovery_history(ledger)
            or active["sequence"] != sequence or sequence != ledger["run_count"] + 1
        ):
            raise ValueError("workflow does not have the expected recoverable active run")
        owner_lock = directory / f"{sequence:04d}.run.lock"
        if owner_lock.is_symlink():
            raise ValueError("run-owner lock is invalid")
        # Retain the marker through refusal and settlement so a status reader
        # can distinguish recovery even after the owner lock is released.
        try:
            with recovery_marker(directory, sequence).open("xb"):
                pass
        except FileExistsError:
            pass
        except OSError as error:
            raise ValueError("could not mark recovery ownership") from error
        with WorkflowLock(owner_lock):
            for owner in ("wrapper_pid", "child_pid"):
                pid = active[owner]
                if pid is not None:
                    presence = process_presence(pid)
                    if presence != "absent":
                        raise ValueError(f"recovery refused: {owner} {pid} is {presence}")
            result = {"outcome": "unknown"}
            append_run(ledger, {
                **active, "state": "abandoned", "result": result, "recovery_reason": recovery_reason,
            })
            del ledger["active_run"]
            write_ledger(directory, ledger)
            summary = {
                "workflow": workflow, "state": "abandoned", "result_sequence": sequence, "result": result,
            }
            try:
                prune_logs(directory, ledger)
            except OSError as error:
                summary["cleanup_error"] = shortened(redact(str(error)), 1024)
            emit_summary(summary)
            if "cleanup_error" in summary:
                return 1
    return 0


def status_identity_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return shortened(redact(value), 128)
        except UnicodeEncodeError:
            return None
    return value if type(value) in (int, float) else None


def owner_lock_proves_running(directory: Path, active: dict[str, Any]) -> bool:
    sequence = active["sequence"]
    try:
        with WorkflowLock(directory / f"{sequence:04d}.run.lock", read_only=True):
            return False
    except WorkflowBusy:
        pass
    except ValueError:
        return False
    try:
        recovery_marker(directory, sequence).lstat()
    except FileNotFoundError:
        # A marker can disappear after retention or finish. Verify the
        # observed identity is still active before classifying the held lock.
        try:
            return read_ledger(directory).get("active_run") == active
        except ValueError:
            return False
    except OSError:
        return False
    return False


def status_snapshot(directory: Path, workflow: str, *, busy: bool) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "workflow": workflow, "state": "uncertain", "run": None, "result": None
    }
    try:
        ledger = read_ledger(directory)
    except ValueError as error:
        snapshot["reason"] = str(error)
        return snapshot
    active = ledger.get("active_run")
    latest = ledger["runs"][-1] if ledger["runs"] else None
    state = settled_state(ledger)
    if state in ("completed", "interrupted"):
        snapshot["result"] = bounded_summary(latest["result"], MAX_SUMMARY_BYTES // 2)
        snapshot["result_sequence"] = latest["sequence"]
    elif state == "abandoned":
        snapshot["result"] = latest["result"]
        snapshot["result_sequence"] = latest["sequence"]
        snapshot["recovery_reason"] = redact(latest["recovery_reason"])
    run = active if active is not None else latest
    if isinstance(run, dict):
        snapshot["run"] = {
            key: status_identity_value(run.get(key)) for key in RUN_IDENTITY_FIELDS
        }
    if active is not None:
        snapshot["reason"] = "active run is incomplete or its owner lock is not held"
        if busy and isinstance(active, dict) and all(
            type(active.get(key)) is int and active[key] > 0
            for key in ("sequence", "wrapper_pid")
        ) and "child_pid" in active and (
            active["child_pid"] is None
            or type(active["child_pid"]) is int and active["child_pid"] > 0
        ) and type(active.get("started_at")) in (int, float) and owner_lock_proves_running(directory, active):
            snapshot["state"] = "running"
            snapshot.pop("reason")
    elif state == "abandoned":
        snapshot["state"] = state
    elif busy:
        snapshot["reason"] = "workflow is busy without an active run identity"
    elif state != "uncertain":
        snapshot["state"] = state
    else:
        snapshot["reason"] = "latest run has no recorded terminal result"
    return snapshot


def status_workflow(root: Path, workflow: str) -> int:
    directory = workflow_path(root, workflow)
    if not directory.exists():
        if not read_finished(finished_path(root, workflow), workflow):
            raise ValueError("unknown workflow identifier")
        emit_summary({"workflow": workflow, "state": "finished", "run": None, "result": None})
        return 0
    try:
        with WorkflowLock(lock_path(root, workflow), read_only=True):
            snapshot = status_snapshot(directory, workflow, busy=False)
    except WorkflowBusy:
        # Writers atomically replace the ledger; never wait on a running build.
        snapshot = status_snapshot(directory, workflow, busy=True)
    except ValueError:
        snapshot = {
            "workflow": workflow, "state": "uncertain", "reason": "workflow lock is unavailable",
            "run": None, "result": None,
        }
    emit_summary(snapshot)
    return 0


def finish_locked(root: Path, workflow: str) -> int:
    directory = workflow_path(root, workflow)
    tombstone = finished_path(root, workflow)
    if not directory.exists():
        if not read_finished(tombstone, workflow):
            raise ValueError("unknown workflow identifier")
        print(json.dumps({"already_finished": True, "finished": workflow}, sort_keys=True))
        return 0
    require_settled_ledger(directory)
    write_finished(tombstone, workflow)
    try:
        shutil.rmtree(directory)
    except BaseException:
        tombstone.unlink(missing_ok=True)
        raise
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
    status = commands.add_parser("status")
    status.add_argument("--workflow", required=True)
    recover = commands.add_parser("recover")
    recover.add_argument("--workflow", required=True)
    recover.add_argument("--sequence", type=int, required=True)
    recover.add_argument("--reason", required=True)
    recover.add_argument("--no-live-descendants", action="store_true", required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        if arguments.operation == "create":
            return create_workflow(arguments.root)
        if arguments.operation == "run":
            return run_command(arguments.root, arguments)
        if arguments.operation == "status":
            return status_workflow(arguments.root, arguments.workflow)
        if arguments.operation == "recover":
            return recover_workflow(arguments.root, arguments)
        return finish_workflow(arguments.root, arguments.workflow)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
