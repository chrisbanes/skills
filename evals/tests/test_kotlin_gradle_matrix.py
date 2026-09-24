import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.harness.cases import validate_corpus
from evals.harness.codex import prepare_workspace
from evals.harness.experiment import (
    CODEX_VERSION_TIMEOUT_SECONDS,
    COMMAND_OUTPUT_TIMEOUT_SECONDS,
    GRADLE_PREFLIGHT_TIMEOUT_SECONDS,
    _command_output,
    filter_cases,
    preflight,
    reconcile_automatic_eligibility,
)
from evals.harness.grade import grade_subject
from evals.harness.score import _routing_metrics
from evals.harness.suites import KOTLIN_GRADLE_SKILLS
from evals.validators.text_case import _mask_kotlin_comments
from evals.tests.test_grade import make_result


REPO_ROOT = Path(__file__).resolve().parents[2]


class KotlinGradleMatrixTest(unittest.TestCase):
    def test_has_risk_weighted_skill_triads_and_routing_cases(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        self.assertEqual(22, report.case_count)
        self.assertFalse(any(case.calibration for case in report.cases))
        self.assertEqual(3, sum(case.kind == "routing" for case in report.cases))
        self.assertGreaterEqual(
            sum(case.provenance["kind"] == "historical" for case in report.cases),
            3,
        )
        for skill in KOTLIN_GRADLE_SKILLS:
            skill_cases = [case for case in report.cases if skill in case.target_skills]
            with self.subTest(skill=skill):
                self.assertTrue(any(case.kind == "direct" for case in skill_cases))
                self.assertTrue(any(case.kind == "novel" for case in skill_cases))
                self.assertTrue(any(case.kind == "negative" for case in skill_cases))

    def test_default_filter_selects_all_22_scored_cases(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        selected = filter_cases(report.cases, case_ids=None, skills=None)

        self.assertEqual(22, len(selected))

    def test_positive_edits_and_required_command_cases_start_red(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        with tempfile.TemporaryDirectory() as temp_dir:
            run_root = Path(temp_dir)
            for case in report.cases:
                with self.subTest(case=case.id):
                    workspace = prepare_workspace(case, REPO_ROOT, run_root / case.id)
                    grade = grade_subject(case, make_result(workspace))
                    starts_red = (
                        case.kind != "negative"
                        and (bool(case.allowed_write_paths) or bool(case.required_command_patterns))
                    )
                    self.assertEqual(not starts_red, grade.objective_pass)

    def test_automatic_prompts_do_not_disclose_routing_expectations(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)

    def test_exhaustiveness_review_does_not_require_using_an_unused_payload(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        case = next(
            case
            for case in report.cases
            if case.id == "kotlin-control-exhaustiveness-novel"
        )
        criterion = next(item for item in case.rubric if item["id"] == "branch-data")
        text = criterion["text"].lower()

        self.assertIn("preserves every current rendered string", text)
        self.assertIn("branch data that remains in use", text)
        self.assertIn("does not invent use of validationerror.reason", text)

    def test_value_class_task_exposes_its_write_boundary(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        case = next(
            case
            for case in report.cases
            if case.id == "kotlin-api-value-class-direct"
        )

        self.assertIn(
            "Edit only `src/main/kotlin/example/Subject.kt`", case.prompt
        )

    def test_kotlin_api_ownership_expectations_accept_multiline_domain_owners(self):
        expectation_path = (
            REPO_ROOT
            / "evals/cases/kotlin-api-ownership-direct/expectations.json"
        )
        expectation = json.loads(expectation_path.read_text(encoding="utf-8"))
        patterns = expectation["must_match"]
        sources = (
            """interface ProfileStore {
    fun loadProfile(rawUserId: String): User
}

@Deprecated(
    message = "Use ProfileStore.loadProfile"
)
fun String.loadProfile(
    store: ProfileStore
): User {
    return store.loadProfile(this)
}

fun profileFor(
    rawUserId: String,
    store: ProfileStore,
): User {
    return store.loadProfile(rawUserId)
}
""",
            """package com.example

interface ProfileStore {
    fun load(rawUserId: String): User
}

data class ProfileRepository(private val store: ProfileStore) {
    fun loadProfile(userId: String): User = store.load(userId)
}

@Deprecated("Use ProfileRepository")
fun String.loadProfile(
    repository: com.example.ProfileRepository,
): User = repository.loadProfile(this)

fun profileFor(userId: String, repository: com.example.ProfileRepository): User =
    repository.loadProfile(userId)
""",
            """interface ProfileStore {
    fun loadProfile(rawUserId: String): User
}

@Deprecated("Use ProfileStore.loadProfile")
fun String.loadProfile(store: ProfileStore): User {
    // Preserve the source-compatible entry point.
    val originalId = this
    return store.loadProfile(this)
}

fun profileFor(userId: String, store: ProfileStore): User =
    store.loadProfile(userId)
""",
        )

        for source in sources:
            with self.subTest(source=source):
                for pattern in patterns:
                    self.assertIsNotNone(
                        re.search(
                            pattern,
                            _mask_kotlin_comments(source),
                            re.MULTILINE | re.DOTALL,
                        )
                    )

        direct_repository_access = """interface ProfileStore {
    fun loadProfile(rawUserId: String): User
}

object ProfileDatabase {
    fun loadProfile(rawUserId: String): User = TODO()
}

@Deprecated("Use ProfileStore")
fun String.loadProfile(store: ProfileStore): User =
    ProfileDatabase.loadProfile(this)

fun profileFor(rawUserId: String, store: ProfileStore): User =
    store.loadProfile(rawUserId)
"""
        shim_delegation = patterns[1]
        self.assertIsNone(
            re.search(shim_delegation, direct_repository_access, re.MULTILINE | re.DOTALL)
        )
        commented_delegation = """@Deprecated("Use ProfileStore")
fun String.loadProfile(store: ProfileStore): User {
    // return store.loadProfile(this)
    return ProfileDatabase.loadProfile(this)
}
"""
        block_commented_delegation = """@Deprecated("Use ProfileStore")
fun String.loadProfile(store: ProfileStore): User {
    /* A nested comment /* still a comment */
    return store.loadProfile(this)
    */
    return ProfileDatabase.loadProfile(this)
}
"""
        for source in (commented_delegation, block_commented_delegation):
            with self.subTest(source=source):
                self.assertIsNone(
                    re.search(
                        shim_delegation,
                        _mask_kotlin_comments(source),
                        re.MULTILINE | re.DOTALL,
                    )
                )

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "src/main/kotlin/example/Subject.kt"
            source_path.parent.mkdir(parents=True)
            invalid_source = (
                """interface ProfileStore {
    fun loadProfile(rawUserId: String): User
}
"""
                + block_commented_delegation
                + """
fun profileFor(userId: String, store: ProfileStore): User =
    store.loadProfile(userId)
"""
            )
            for source, expected_code in ((sources[2], 0), (invalid_source, 1)):
                with self.subTest(validator_exit=expected_code):
                    source_path.write_text(source, encoding="utf-8")
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-B",
                            str(REPO_ROOT / "evals/validators/text_case.py"),
                            "kotlin-api-ownership-direct",
                        ],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(expected_code, result.returncode, result.stderr)

    def test_event_channel_expectation_accepts_equivalent_bounded_capacities(self):
        expectation_path = (
            REPO_ROOT
            / "evals"
            / "cases"
            / "kotlin-flow-event-delivery-direct"
            / "expectations.json"
        )
        expectation = json.loads(expectation_path.read_text(encoding="utf-8"))
        channel_pattern = expectation["must_match"][0]

        for declaration in (
            "Channel<Navigation>(Channel.BUFFERED)",
            "Channel<Navigation>(capacity = Channel.BUFFERED)",
            "Channel<Navigation>(1)",
            "Channel<Navigation>(capacity = 64)",
            "private val queue: Channel<Navigation> = Channel(capacity = 1)",
            "val queue: Channel<Navigation> = Channel(Channel.BUFFERED)",
        ):
            with self.subTest(declaration=declaration):
                self.assertIsNotNone(re.search(channel_pattern, declaration))

        self.assertIsNone(re.search(channel_pattern, "Channel<Navigation>(Channel.UNLIMITED)"))
        self.assertIsNone(
            re.search(
                channel_pattern,
                "val queue: Channel<Navigation> = Channel(Channel.UNLIMITED)",
            )
        )

    def test_bounded_validation_cases_require_the_test_task(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        for case_id in (
            "gradle-incidental-validation-direct",
            "router-kotlin-gradle-validation",
        ):
            case = next(case for case in report.cases if case.id == case_id)
            run_pattern = case.required_command_patterns[1]

            for command in (
                "python3 gradle_run.py run --scope targeted --question verified "
                "-- ./gradlew --offline --no-scan test",
                "python3 gradle_run.py run --question verified --scope targeted "
                "-- ./gradlew test --offline --no-scan",
            ):
                with self.subTest(case=case_id, command=command):
                    self.assertIsNotNone(re.search(run_pattern, command, re.DOTALL))

            for command in (
                "python3 gradle_run.py run --scope targeted --question verified "
                "-- ./gradlew --offline --no-scan help",
                "python3 gradle_run.py run --scope targeted --question test "
                "-- ./gradlew --offline --no-scan help",
                "python3 gradle_run.py run --scope targeted --question verified "
                "-- ./gradlew --offline --no-scan testClasses",
            ):
                with self.subTest(case=case_id, command=command):
                    self.assertIsNone(re.search(run_pattern, command, re.DOTALL))

    def test_gradle_routing_is_expected_only_after_an_invocation(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        case_ids = (
            "kotlin-api-ownership-direct",
            "kotlin-api-value-class-direct",
            "kotlin-control-exhaustiveness-direct",
            "kotlin-control-guards-direct",
            "kotlin-coroutine-ownership-direct",
            "kotlin-detached-thread-ownership-direct",
            "kotlin-flow-event-delivery-direct",
        )
        cases = [
            next(case for case in report.cases if case.id == case_id)
            for case_id in case_ids
        ]
        records = [
            {
                "case_id": case.id,
                "arm": "automatic",
                "subject": {
                    "events": [
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "command_execution",
                                "command": "rg --files -g 'gradlew'",
                            },
                        }
                    ]
                },
            }
            for case in cases
        ]

        for case in cases:
            self.assertEqual(case.target_skills, case.expected_skills)
            self.assertIn("gradle-run", case.allowed_skills)
        reconcile_automatic_eligibility(REPO_ROOT, cases, records)
        self.assertTrue(
            all("gradle-run" not in record["expected_skills"] for record in records)
        )
        self.assertTrue(
            all("gradle-run" not in record["allowed_skills"] for record in records)
        )
        records[0]["reported_skills"] = [*records[0]["expected_skills"], "gradle-run"]
        self.assertLess(_routing_metrics([records[0]])[0], 1.0)

        records[0]["subject"]["events"] = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": (
                        "python3 .agents/skills/gradle-run/scripts/gradle_run.py run "
                        "--scope targeted --question test -- ./gradlew --offline test"
                    ),
                },
            }
        ]
        reconcile_automatic_eligibility(REPO_ROOT, cases, records)
        self.assertIn("gradle-run", records[0]["expected_skills"])
        self.assertIn("gradle-run", records[0]["allowed_skills"])

    def test_kotlin_fixture_is_pinned_and_offline_ready(self):
        fixture = REPO_ROOT / "evals" / "fixtures" / "kotlin-jvm"
        build = (fixture / "build.gradle.kts").read_text(encoding="utf-8")
        wrapper = (fixture / "gradle" / "wrapper" / "gradle-wrapper.properties").read_text(
            encoding="utf-8"
        )

        self.assertIn('org.jetbrains.kotlin.jvm") version "2.4.10"', build)
        self.assertIn("kotlinx-coroutines-core:1.10.2", build)
        self.assertIn("gradle-9.7.0-bin.zip", wrapper)
        self.assertTrue((fixture / "gradlew").stat().st_mode & 0o111)
        subject_wrapper = fixture / "subject-gradlew"
        self.assertTrue(subject_wrapper.stat().st_mode & 0o111)
        self.assertIn("BUILD SUCCESSFUL", subject_wrapper.read_text(encoding="utf-8"))

        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        real_gradle_validators = [
            validator
            for case in report.cases
            for validator in case.validators
            if validator.argv[0].startswith("./gradlew")
        ]
        self.assertTrue(real_gradle_validators)
        self.assertTrue(
            all(validator.argv[0] == "./gradlew-real" for validator in real_gradle_validators)
        )

    def test_preflight_uses_the_real_validator_gradle_wrapper(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        fixture = REPO_ROOT / "evals" / "fixtures" / "kotlin-jvm"

        with patch(
            "evals.harness.experiment._command_output", return_value="ok"
        ) as command_output:
            preflight(REPO_ROOT, "codex", report.cases)

        commands = [call.args[0] for call in command_output.call_args_list]
        self.assertIn(
            [str(fixture / "gradlew"), "--offline", "--no-scan", "test"],
            commands,
        )
        self.assertNotIn(
            [str(fixture / "subject-gradlew"), "--offline", "--no-scan", "test"],
            commands,
        )
        timeout_by_command = {
            tuple(call.args[0]): call.kwargs.get(
                "timeout_seconds", COMMAND_OUTPUT_TIMEOUT_SECONDS
            )
            for call in command_output.call_args_list
        }
        self.assertEqual(
            CODEX_VERSION_TIMEOUT_SECONDS,
            timeout_by_command[("codex", "--version")],
        )
        self.assertEqual(
            COMMAND_OUTPUT_TIMEOUT_SECONDS,
            timeout_by_command[("git", "rev-parse", "HEAD")],
        )
        self.assertEqual(
            GRADLE_PREFLIGHT_TIMEOUT_SECONDS,
            timeout_by_command[
                (str(fixture / "gradlew"), "--offline", "--no-scan", "test")
            ],
        )

    def test_command_output_passes_a_bounded_default_timeout(self):
        completed = subprocess.CompletedProcess(
            args=["git", "rev-parse", "HEAD"], returncode=0, stdout="abc\n", stderr=""
        )
        with patch(
            "evals.harness.experiment.subprocess.run", return_value=completed
        ) as run:
            output = _command_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT)

        self.assertEqual("abc", output)
        self.assertEqual(COMMAND_OUTPUT_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])

    def test_cli_version_timeout_fails_with_installation_guidance(self):
        timeout = subprocess.TimeoutExpired(
            cmd=["codex", "--version"], timeout=CODEX_VERSION_TIMEOUT_SECONDS
        )
        with patch(
            "evals.harness.experiment.subprocess.run", side_effect=timeout
        ) as run:
            with self.assertRaisesRegex(
                RuntimeError,
                r"codex --version timed out after 10s.*installation.*signature",
            ):
                preflight(REPO_ROOT, "codex", ())

        self.assertEqual(CODEX_VERSION_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])

    def test_gradle_fixture_timeout_reports_fixture_and_offline_guidance(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")
        case = next(
            case
            for case in report.cases
            if (REPO_ROOT / "evals" / "fixtures" / case.fixture / "gradlew").is_file()
        )
        fixture = REPO_ROOT / "evals" / "fixtures" / case.fixture
        timeout = subprocess.TimeoutExpired(
            cmd=[str(fixture / "gradlew"), "--offline", "--no-scan", "test"],
            timeout=GRADLE_PREFLIGHT_TIMEOUT_SECONDS,
        )
        codex_completed = subprocess.CompletedProcess(
            args=["codex", "--version"], returncode=0, stdout="ok\n", stderr=""
        )
        git_completed = subprocess.CompletedProcess(
            args=["git", "rev-parse", "HEAD"],
            returncode=0,
            stdout="ok\n",
            stderr="",
        )
        with patch(
            "evals.harness.experiment.subprocess.run",
            side_effect=[
                codex_completed,
                git_completed,
                timeout,
            ],
        ) as run:
            with self.assertRaisesRegex(
                RuntimeError,
                r"gradlew --offline --no-scan test timed out after 180s.*offline Gradle dependencies",
            ):
                preflight(REPO_ROOT, "codex", (case,))

        self.assertEqual(GRADLE_PREFLIGHT_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])


if __name__ == "__main__":
    unittest.main()
