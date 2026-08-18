"""Tests for the compact-output Gradle wrapper."""

from __future__ import annotations

import json
import importlib.util
import io
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("gradle_run.py")
SPEC = importlib.util.spec_from_file_location("gradle_run", SCRIPT)
assert SPEC and SPEC.loader
GRADLE_RUN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GRADLE_RUN
SPEC.loader.exec_module(GRADLE_RUN)


def process_is_running(pid: int) -> bool:
    try:
        stat = (Path("/proc") / str(pid) / "stat").read_text()
    except OSError:
        pass
    else:
        _prefix, separator, fields = stat.rpartition(") ")
        if separator and fields.split()[:1] == ["Z"]:
            return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class ProcessAssertionTest(unittest.TestCase):
    @unittest.skipUnless(
        hasattr(os, "fork") and Path("/proc").is_dir(),
        "requires a procfs-backed POSIX process table",
    )
    def test_zombie_is_not_reported_as_running(self) -> None:
        pid = os.fork()
        if pid == 0:
            os._exit(0)

        try:
            status = Path("/proc") / str(pid) / "stat"
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                if status.read_text().rpartition(") ")[2].split()[:1] == ["Z"]:
                    break
                time.sleep(0.01)
            else:
                self.fail(f"process {pid} did not become a zombie")

            self.assertFalse(process_is_running(pid))
        finally:
            os.waitpid(pid, 0)


class GradleRunTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "managed-root"
        self.gradle = self.root.parent / "gradlew"
        self.gradle.write_text(
            "#!/bin/sh\n"
            "while [ \"$1\" != \"--\" ]; do shift; done\n"
            "shift\n"
            "exec \"$@\"\n"
        )
        self.gradle.chmod(0o700)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def invoke(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def create_workflow(self) -> str:
        result = self.invoke("create")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["workflow"]

    def assert_process_gone(self, pid: int) -> None:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if not process_is_running(pid):
                return
            time.sleep(0.01)
        self.fail(f"process {pid} is still running")

    def run_gradle(
        self, workflow: str, scope: str, question: str, command: str
    ) -> subprocess.CompletedProcess[str]:
        return self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            scope,
            "--question",
            question,
            "--",
            str(self.gradle),
            "--",
            sys.executable,
            "-c",
            command,
        )


class GradleRunProcessTest(GradleRunTestCase):
    def test_large_output_is_saved_but_stdout_is_bounded(self) -> None:
        workflow = self.create_workflow()
        payload = "x" * 200_000

        result = self.run_gradle(
            workflow, "targeted", "Does the focused task pass?", "print('x' * 200_000)"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout.encode("utf-8")), 16_384)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        summary = json.loads(result.stdout)
        log = Path(summary["log"])
        self.assertTrue(log.is_file())
        self.assertGreater(log.stat().st_size, 100_000)
        self.assertNotIn(payload, result.stdout)

    def test_many_failed_tasks_do_not_exceed_the_summary_bound(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "broad",
            "Which aggregate tasks failed?",
            "[print(f'> Task :task{index} FAILED') for index in range(1000)]",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertLessEqual(len(result.stdout.encode("utf-8")), 16_384)
        self.assertLessEqual(len(summary["failed_tasks"]), 16)
        self.assertTrue(summary["failed_tasks_truncated"])

    def test_oversized_failed_task_name_does_not_exceed_the_summary_bound(self) -> None:
        workflow = self.create_workflow()
        task_name = "a" * 20_000

        result = self.run_gradle(
            workflow,
            "broad",
            "Which oversized task failed?",
            f"print('> Task :{task_name} FAILED')",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertLessEqual(len(result.stdout.encode("utf-8")), 16_384)
        self.assertTrue(summary["failed_tasks_truncated"])
        self.assertLess(len(summary["failed_tasks"][0].encode("utf-8")), 1024)

    def test_child_exit_status_and_failed_tasks_are_reported(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "targeted",
            "Which task failed?",
            "print('> Task :compileKotlin FAILED'); print('FAILURE: Build failed'); raise SystemExit(7)",
        )

        self.assertEqual(result.returncode, 7)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["exit_status"], 7)
        self.assertEqual(summary["failed_tasks"], [":compileKotlin"])
        self.assertTrue(summary["failure_fingerprints"])

    def test_ansi_diagnostics_are_normalized_and_fingerprinted(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "targeted",
            "What warning must be fixed?",
            "print('\\x1b[33mwarning: use the new API\\x1b[0m'); print('warning:   use the new API')",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        warning = json.loads(result.stdout)["warning_fingerprints"]
        self.assertEqual(len(warning), 1)
        self.assertEqual(warning[0]["count"], 2)
        self.assertEqual(len(warning[0]["fingerprint"]), 64)

    def test_kotlin_and_deprecation_warning_formats_are_fingerprinted(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "targeted",
            "Which compiler and Gradle warnings remain?",
            "print('w: src/Main.kt:1:1 This declaration needs opt-in'); print('This API has been deprecated and will be removed')",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        warnings = json.loads(result.stdout)["warning_fingerprints"]
        self.assertEqual(len(warnings), 2)
        self.assertTrue(any(item["excerpt"].startswith("w:") for item in warnings))
        self.assertTrue(any("deprecated" in item["excerpt"] for item in warnings))

    def test_multiline_failure_is_fingerprinted_as_one_diagnostic_block(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "targeted",
            "What source failure occurred?",
            "print('FAILURE: Build failed'); print('* What went wrong:'); print('e: Unresolved reference: missing'); print('  at Source.kt:1'); print('* Try:'); raise SystemExit(1)",
        )

        self.assertEqual(result.returncode, 1)
        failures = json.loads(result.stdout)["failure_fingerprints"]
        self.assertEqual(len(failures), 1)
        self.assertIn("Unresolved reference", failures[0]["excerpt"])

    def test_model_visible_output_and_ledger_redact_credentials(self) -> None:
        workflow = self.create_workflow()
        secret = "top secret tail-marker"

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            f"Does password={secret} stay private?",
            "--",
            str(self.gradle),
            f"-PapiToken={secret}",
            "--",
            sys.executable,
            "-c",
            (
                f"print('warning: authToken={secret}'); "
                f"print('error: password={secret}'); "
                f"print('warning: Authorization: Bearer {secret}')"
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        ledger = (self.root / workflow / "ledger.json").read_text()
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, ledger)
        self.assertNotIn("tail-marker", result.stdout)
        self.assertNotIn("tail-marker", ledger)
        self.assertIn("[REDACTED]", result.stdout)
        self.assertIn("[REDACTED]", ledger)

    def test_missing_command_fails_without_fallback(self) -> None:
        workflow = self.create_workflow()

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Can the unavailable command run?",
            "--",
            str(self.root.parent / "missing" / "gradlew"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("launch_error", json.loads(result.stdout))
        self.assertFalse(list((self.root / workflow).glob("*.log")))

    def test_sigterm_reaps_child_and_records_interrupted_run(self) -> None:
        workflow = self.create_workflow()
        pid_file = self.root.parent / "descendant.pid"
        descendant_code = "import time; time.sleep(60)"
        child_code = (
            "from pathlib import Path; import subprocess, sys, time; "
            f"descendant = subprocess.Popen([sys.executable, '-c', {descendant_code!r}]); "
            f"Path({str(pid_file)!r}).write_text(str(descendant.pid)); "
            "time.sleep(60)"
        )
        wrapper = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Can interruption stop the build safely?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                child_code,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(pid_file.exists(), "child did not start")

        wrapper.send_signal(signal.SIGTERM)
        stdout, stderr = wrapper.communicate(timeout=10)

        self.assertEqual(wrapper.returncode, 128 + signal.SIGTERM, stderr)
        summary = json.loads(stdout)
        self.assertEqual(summary["interrupted_signal"], signal.SIGTERM)
        self.assertNotIn("launch_error", summary)
        self.assertTrue(Path(summary["log"]).is_file())
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual(ledger["runs"][0]["interrupted_signal"], signal.SIGTERM)
        self.assert_process_gone(int(pid_file.read_text()))

    def test_signal_during_launch_reaps_the_created_process_group(self) -> None:
        workflow = self.create_workflow()
        arguments = GRADLE_RUN.parser().parse_args(
            [
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Can interruption during launch stop the build safely?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                "import time; time.sleep(60)",
            ]
        )
        real_popen = subprocess.Popen
        started: list[subprocess.Popen[bytes]] = []

        def interrupt_before_returning_child(
            *popen_arguments: object, **popen_options: object
        ) -> subprocess.Popen[bytes]:
            child = real_popen(*popen_arguments, **popen_options)
            started.append(child)
            signal.raise_signal(signal.SIGINT)
            return child

        output = io.StringIO()
        wrapper_reaped_child = False
        try:
            with (
                mock.patch.object(
                    GRADLE_RUN.subprocess,
                    "Popen",
                    side_effect=interrupt_before_returning_child,
                ),
                mock.patch("sys.stdout", output),
            ):
                result = GRADLE_RUN.run_command(self.root, arguments)
            wrapper_reaped_child = bool(started) and not process_is_running(started[0].pid)
        finally:
            for child in started:
                if process_is_running(child.pid):
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait()

        self.assertEqual(result, 128 + signal.SIGINT)
        self.assertEqual(json.loads(output.getvalue())["interrupted_signal"], signal.SIGINT)
        self.assertEqual(len(started), 1)
        self.assertTrue(wrapper_reaped_child, "wrapper left the launched child running")

    def test_sigint_reaps_child_and_records_interrupted_run(self) -> None:
        workflow = self.create_workflow()
        pid_file = self.root.parent / "child.pid"
        child_code = (
            "from pathlib import Path; import os, time; "
            f"Path({str(pid_file)!r}).write_text(str(os.getpid())); "
            "time.sleep(60)"
        )
        wrapper = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Can Ctrl-C stop the build safely?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                child_code,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(pid_file.exists(), "child did not start")

        wrapper.send_signal(signal.SIGINT)
        stdout, stderr = wrapper.communicate(timeout=10)

        self.assertEqual(wrapper.returncode, 128 + signal.SIGINT, stderr)
        summary = json.loads(stdout)
        self.assertEqual(summary["interrupted_signal"], signal.SIGINT)
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual(ledger["runs"][0]["interrupted_signal"], signal.SIGINT)
        self.assert_process_gone(int(pid_file.read_text()))

    def test_interrupted_run_preserves_partial_diagnostics(self) -> None:
        workflow = self.create_workflow()
        pid_file = self.root.parent / "diagnostic-child.pid"
        child_code = (
            "from pathlib import Path; import os, time; "
            "print('e: Unresolved reference: missingAfterInterrupt', flush=True); "
            "print('warning: partial warning remains', flush=True); "
            f"Path({str(pid_file)!r}).write_text(str(os.getpid())); "
            "time.sleep(60)"
        )
        wrapper = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "What evidence was emitted before interruption?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                child_code,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(pid_file.exists(), "child did not start")

        wrapper.send_signal(signal.SIGINT)
        stdout, stderr = wrapper.communicate(timeout=10)

        self.assertEqual(wrapper.returncode, 128 + signal.SIGINT, stderr)
        summary = json.loads(stdout)
        self.assertIn(
            "missingAfterInterrupt", summary["failure_fingerprints"][0]["excerpt"]
        )
        self.assertIn("partial warning", summary["warning_fingerprints"][0]["excerpt"])
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertTrue(ledger["runs"][0]["failure_fingerprints"])
        self.assertTrue(ledger["runs"][0]["warning_fingerprints"])
        self.assertTrue(
            any(
                "missingAfterInterrupt" in item["excerpt"]
                for item in ledger["failure_fingerprints"].values()
            )
        )

    def test_repeated_sigint_during_cleanup_records_interrupted_run(self) -> None:
        workflow = self.create_workflow()
        pid_file = self.root.parent / "signal-resistant-child.pid"
        child_code = (
            "from pathlib import Path; import os, signal, time; "
            "signal.signal(signal.SIGINT, signal.SIG_IGN); "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"Path({str(pid_file)!r}).write_text(str(os.getpid())); "
            "time.sleep(60)"
        )
        wrapper = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Can repeated Ctrl-C stop the build safely?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                child_code,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        child_pid: int | None = None
        stdout = ""
        stderr = ""
        try:
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(pid_file.exists(), "child did not start")
            child_pid = int(pid_file.read_text())

            wrapper.send_signal(signal.SIGINT)
            time.sleep(0.1)
            wrapper.send_signal(signal.SIGINT)
            stdout, stderr = wrapper.communicate(timeout=10)
        finally:
            if wrapper.poll() is None:
                wrapper.kill()
                wrapper.communicate()
            if child_pid is not None:
                try:
                    os.kill(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

        self.assertEqual(wrapper.returncode, 128 + signal.SIGINT, stderr)
        summary = json.loads(stdout)
        self.assertEqual(summary["interrupted_signal"], signal.SIGINT)
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual(ledger["runs"][0]["interrupted_signal"], signal.SIGINT)
        assert child_pid is not None
        self.assert_process_gone(child_pid)

    def test_signal_after_child_exit_preserves_the_completed_run(self) -> None:
        workflow = self.create_workflow()
        arguments = [
            str(SCRIPT),
            "--root",
            str(self.root),
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Can finalization preserve a completed build?",
            "--",
            str(self.gradle),
            "--",
            sys.executable,
            "-c",
            "print('warning: final diagnostic')",
        ]
        extract_diagnostics = GRADLE_RUN.extract_diagnostics

        def interrupt_during_finalization(log: Path) -> GRADLE_RUN.Diagnostics:
            signal.raise_signal(signal.SIGINT)
            return extract_diagnostics(log)

        with (
            mock.patch.object(sys, "argv", arguments),
            mock.patch.object(
                GRADLE_RUN,
                "extract_diagnostics",
                side_effect=interrupt_during_finalization,
            ) as extraction,
            mock.patch("sys.stdout", new=io.StringIO()) as stdout,
        ):
            exit_status = GRADLE_RUN.main()

        extraction.assert_called_once()
        self.assertEqual(exit_status, 0)
        self.assertEqual(json.loads(stdout.getvalue())["exit_status"], 0)
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual(ledger["run_count"], 1)
        self.assertEqual(ledger["runs"][0]["exit_status"], 0)

    def test_blank_question_fails_without_running_the_command(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(workflow, "targeted", "", "raise SystemExit(99)")

        self.assertEqual(result.returncode, 2)
        self.assertIn("non-empty", result.stderr)
        self.assertFalse(list((self.root / workflow).glob("*.log")))

    def test_non_gradle_command_fails_without_running(self) -> None:
        workflow = self.create_workflow()

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Can a non-Gradle command run?",
            "--",
            sys.executable,
            "-c",
            "raise SystemExit(99)",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Gradle launcher", result.stderr)
        self.assertFalse(list((self.root / workflow).glob("*.log")))

    def test_custom_gradle_wrapper_script_is_accepted(self) -> None:
        workflow = self.create_workflow()
        custom_wrapper = self.gradle.with_name("gradlew_custom")
        self.gradle.rename(custom_wrapper)
        self.gradle = custom_wrapper

        result = self.run_gradle(
            workflow,
            "targeted",
            "Does the affected-module check pass?",
            "print('ok')",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["exit_status"], 0)
        self.assertIn("--console=plain", summary["command"])
        self.assertIn("--no-scan", summary["command"])

    def test_gradle_defaults_preserve_an_explicit_scan(self) -> None:
        workflow = self.create_workflow()
        self.gradle.write_text("#!/bin/sh\nprintf 'args: %s\\n' \"$*\"\n")

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Do default console flags preserve scans?",
            "--",
            str(self.gradle),
            "check",
            "--scan",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertIn("--console=plain", summary["command"])
        self.assertIn("--scan", summary["command"])
        self.assertNotIn("--no-scan", summary["command"])

    def test_gradle_defaults_stay_before_a_user_option_separator(self) -> None:
        workflow = self.create_workflow()
        self.gradle.write_text("#!/bin/sh\nprintf 'args: %s\\n' \"$*\"\n")

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Do Gradle defaults stay out of task arguments?",
            "--",
            str(self.gradle),
            "check",
            "--",
            "task-option",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        command = json.loads(result.stdout)["command"].split()
        separator = command.index("--")
        self.assertLess(command.index("--console=plain"), separator)
        self.assertLess(command.index("--no-scan"), separator)

    def test_task_arguments_do_not_override_gradle_defaults(self) -> None:
        workflow = self.create_workflow()
        self.gradle.write_text("#!/bin/sh\nprintf 'args: %s\\n' \"$*\"\n")

        result = self.invoke(
            "run",
            "--workflow",
            workflow,
            "--scope",
            "targeted",
            "--question",
            "Do task arguments leave Gradle defaults intact?",
            "--",
            str(self.gradle),
            "check",
            "--",
            "--scan",
            "--console=verbose",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        command = json.loads(result.stdout)["command"].split()
        separator = command.index("--")
        self.assertLess(command.index("--console=plain"), separator)
        self.assertLess(command.index("--no-scan"), separator)


class GradleRunHeartbeatTest(unittest.TestCase):
    def test_wait_blocks_between_a_finite_number_of_heartbeats(self) -> None:
        child = mock.Mock()
        child.wait.return_value = 0
        timers = [mock.Mock() for _ in GRADLE_RUN.HEARTBEAT_DELAYS]

        with mock.patch.object(GRADLE_RUN.threading, "Timer", side_effect=timers) as timer:
            result = GRADLE_RUN.wait_for_child(child, sequence=1)

        self.assertEqual(result, 0)
        child.wait.assert_called_once_with()
        self.assertEqual(timer.call_count, len(GRADLE_RUN.HEARTBEAT_DELAYS))
        for item in timers:
            item.start.assert_called_once_with()
            item.cancel.assert_called_once_with()
            item.join.assert_called_once_with()

    def test_heartbeat_only_prints_while_the_child_is_running(self) -> None:
        child = mock.Mock()
        child.poll.side_effect = [None, 0]

        with mock.patch("sys.stderr", new=io.StringIO()) as stderr:
            GRADLE_RUN.emit_heartbeat(child, sequence=1, delay=30.0)
            GRADLE_RUN.emit_heartbeat(child, sequence=1, delay=60.0)

        self.assertEqual(len(stderr.getvalue().splitlines()), 1)

    def test_terminate_child_reaps_a_running_process(self) -> None:
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        GRADLE_RUN.terminate_child(child)

        self.assertIsNotNone(child.poll())


class GradleRunWindowsProcessTest(unittest.TestCase):
    def test_windows_launch_uses_a_new_process_group(self) -> None:
        with mock.patch.object(
            GRADLE_RUN.subprocess,
            "CREATE_NEW_PROCESS_GROUP",
            0x00000200,
            create=True,
        ):
            options = GRADLE_RUN.process_launch_options("nt")

        self.assertEqual(options, {"creationflags": 0x00000200})

    def test_windows_cleanup_escalates_to_the_process_tree(self) -> None:
        child = mock.Mock()
        child.pid = 4242
        child.poll.return_value = None
        child.wait.side_effect = [
            subprocess.TimeoutExpired("gradlew", 5),
            0,
        ]

        with (
            mock.patch.object(GRADLE_RUN.os, "name", "nt"),
            mock.patch.object(
                GRADLE_RUN.signal,
                "CTRL_BREAK_EVENT",
                1,
                create=True,
            ),
            mock.patch.object(GRADLE_RUN.subprocess, "run") as taskkill,
        ):
            GRADLE_RUN.terminate_child(child, isolated_process_group=True)

        child.send_signal.assert_called_once_with(1)
        taskkill.assert_called_once_with(
            ["taskkill", "/PID", "4242", "/T", "/F"],
            check=False,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            timeout=5,
        )
        child.wait.assert_has_calls([mock.call(timeout=5), mock.call()])

    def test_windows_cleanup_kills_tree_when_launcher_exits_after_ctrl_break(self) -> None:
        child = mock.Mock()
        child.pid = 4242
        child.poll.return_value = None
        child.wait.return_value = 0

        with (
            mock.patch.object(GRADLE_RUN.os, "name", "nt"),
            mock.patch.object(
                GRADLE_RUN.signal,
                "CTRL_BREAK_EVENT",
                1,
                create=True,
            ),
            mock.patch.object(GRADLE_RUN.subprocess, "run") as taskkill,
        ):
            GRADLE_RUN.terminate_child(child, isolated_process_group=True)

        child.send_signal.assert_called_once_with(1)
        taskkill.assert_called_once_with(
            ["taskkill", "/PID", "4242", "/T", "/F"],
            check=False,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            timeout=5,
        )


class GradleRunWorkflowTest(GradleRunTestCase):
    def test_concurrent_run_fails_before_launching(self) -> None:
        workflow = self.create_workflow()
        ready = self.root.parent / "active-run.ready"
        unexpected = self.root.parent / "unexpected-run"
        active = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Does the active task finish?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                f"from pathlib import Path; import time; Path({str(ready)!r}).touch(); time.sleep(60)",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), "active run did not start")

            result = self.run_gradle(
                workflow,
                "targeted",
                "Can another task use this workflow?",
                f"from pathlib import Path; Path({str(unexpected)!r}).touch()",
            )
        finally:
            if active.poll() is None:
                active.send_signal(signal.SIGTERM)
            active.communicate(timeout=10)

        self.assertEqual(result.returncode, 2)
        self.assertIn("workflow is busy", result.stderr)
        self.assertFalse(unexpected.exists())

    def test_finish_fails_while_a_run_is_active(self) -> None:
        workflow = self.create_workflow()
        ready = self.root.parent / "finish-active.ready"
        active = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "run",
                "--workflow",
                workflow,
                "--scope",
                "targeted",
                "--question",
                "Does the active task finish before cleanup?",
                "--",
                str(self.gradle),
                "--",
                sys.executable,
                "-c",
                f"from pathlib import Path; import time; Path({str(ready)!r}).touch(); time.sleep(60)",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), "active run did not start")

            result = self.invoke("finish", "--workflow", workflow)
        finally:
            if active.poll() is None:
                active.send_signal(signal.SIGTERM)
            active.communicate(timeout=10)

        self.assertEqual(result.returncode, 2)
        self.assertIn("workflow is busy", result.stderr)
        self.assertTrue((self.root / workflow).is_dir())

    def test_workflow_ledger_records_scope_question_and_command(self) -> None:
        workflow = self.create_workflow()
        result = self.run_gradle(
            workflow, "broad", "What does the aggregate check reveal?", "print('ok')"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        entry = ledger["runs"][0]
        self.assertEqual(entry["scope"], "broad")
        self.assertEqual(entry["question"], "What does the aggregate check reveal?")
        self.assertIn(sys.executable, entry["command"])

    def test_repeated_failure_fingerprint_is_flagged(self) -> None:
        workflow = self.create_workflow()
        command = "print('FAILURE: same diagnostic'); raise SystemExit(1)"
        self.assertEqual(
            self.run_gradle(workflow, "targeted", "First diagnosis?", command).returncode, 1
        )

        result = self.run_gradle(workflow, "targeted", "Did the fix change it?", command)

        self.assertEqual(result.returncode, 1)
        self.assertTrue(json.loads(result.stdout)["repeated_primary_failure"])

    def test_changed_source_failure_is_not_masked_by_the_gradle_block(self) -> None:
        workflow = self.create_workflow()
        generic_block = (
            "print('FAILURE: Build failed'); "
            "print('e: Unresolved reference: {source}'); "
            "print('* What went wrong:'); "
            "print('Execution failed for task compileKotlin'); "
            "raise SystemExit(1)"
        )
        first = self.run_gradle(
            workflow,
            "targeted",
            "What is the first source failure?",
            generic_block.format(source="firstSymbol"),
        )
        self.assertEqual(first.returncode, 1)

        second = self.run_gradle(
            workflow,
            "targeted",
            "Did the source failure change?",
            generic_block.format(source="secondSymbol"),
        )

        self.assertEqual(second.returncode, 1)
        summary = json.loads(second.stdout)
        self.assertFalse(summary["repeated_primary_failure"])
        self.assertIn("secondSymbol", summary["failure_fingerprints"][0]["excerpt"])

    def test_warning_fingerprints_are_deduplicated_across_runs(self) -> None:
        workflow = self.create_workflow()
        self.assertEqual(
            self.run_gradle(
                workflow, "targeted", "First warning?", "print('warning: same warning')"
            ).returncode,
            0,
        )

        result = self.run_gradle(
            workflow, "targeted", "Did the warning remain?", "print('warning: same warning')"
        )

        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        fingerprints = ledger["warning_fingerprints"]
        self.assertEqual(len(fingerprints), 1)
        self.assertEqual(next(iter(fingerprints.values()))["occurrences"], 2)
        self.assertEqual(len(json.loads(result.stdout)["warning_fingerprints"]), 1)

    def test_many_unique_diagnostics_keep_the_ledger_bounded(self) -> None:
        workflow = self.create_workflow()

        result = self.run_gradle(
            workflow,
            "broad",
            "Which warnings are unique?",
            "[print(f'warning: unique {index}') for index in range(1000)]",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual(
            len(ledger["warning_fingerprints"]), GRADLE_RUN.MAX_STORED_FINGERPRINTS
        )
        self.assertEqual(ledger["warning_fingerprints_truncated_occurrences"], 744)
        self.assertEqual(
            json.loads(result.stdout)["warning_fingerprints_truncated"], 744
        )

    def test_logs_are_pruned_with_evicted_ledger_runs(self) -> None:
        workflow = self.create_workflow()

        with mock.patch.object(GRADLE_RUN, "MAX_LEDGER_RUNS", 2):
            for index in range(3):
                arguments = GRADLE_RUN.parser().parse_args(
                    [
                        "--root",
                        str(self.root),
                        "run",
                        "--workflow",
                        workflow,
                        "--scope",
                        "targeted",
                        "--question",
                        f"Does retained run {index + 1} pass?",
                        "--",
                        str(self.gradle),
                        "--",
                        sys.executable,
                        "-c",
                        "print('ok')",
                    ]
                )
                with mock.patch("sys.stdout", new=io.StringIO()):
                    self.assertEqual(GRADLE_RUN.run_command(self.root, arguments), 0)

        logs = sorted(path.name for path in (self.root / workflow).glob("*.log"))
        self.assertEqual(logs, ["0002.log", "0003.log"])
        ledger = json.loads((self.root / workflow / "ledger.json").read_text())
        self.assertEqual([run["sequence"] for run in ledger["runs"]], [2, 3])

    def test_finish_deletes_only_the_managed_workflow_directory(self) -> None:
        first = self.create_workflow()
        second = self.create_workflow()

        result = self.invoke("finish", "--workflow", first)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / first).exists())
        self.assertTrue((self.root / second).is_dir())

    def test_finish_is_idempotent(self) -> None:
        workflow = self.create_workflow()
        self.assertEqual(self.invoke("finish", "--workflow", workflow).returncode, 0)

        result = self.invoke("finish", "--workflow", workflow)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["already_finished"])

    def test_finish_rejects_an_unknown_valid_workflow_identifier(self) -> None:
        self.root.mkdir(parents=True)

        result = self.invoke("finish", "--workflow", "0" * 32)

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown workflow identifier", result.stderr)

    def test_invalid_workflow_identifier_fails_closed(self) -> None:
        self.root.mkdir(parents=True)
        sibling = self.root.parent / "sibling"
        sibling.mkdir()

        result = self.invoke("finish", "--workflow", "../sibling")

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sibling.is_dir())
        self.assertIn("invalid workflow", result.stderr.lower())

    def test_cleanup_rejects_a_workflow_symlink(self) -> None:
        workflow = self.create_workflow()
        directory = self.root / workflow
        outside = self.root.parent / "outside"
        outside.mkdir()
        shutil.rmtree(directory)
        directory.symlink_to(outside, target_is_directory=True)

        result = self.invoke("finish", "--workflow", workflow)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(outside.is_dir())


if __name__ == "__main__":
    unittest.main()
