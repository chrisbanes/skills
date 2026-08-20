import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.harness.cases import validate_corpus
from evals.harness.codex import prepare_workspace
from evals.harness.experiment import filter_cases, preflight
from evals.harness.grade import grade_subject
from evals.harness.suites import KOTLIN_GRADLE_SKILLS
from evals.tests.test_grade import make_result


REPO_ROOT = Path(__file__).resolve().parents[2]


class KotlinGradleMatrixTest(unittest.TestCase):
    def test_has_risk_weighted_skill_triads_and_routing_cases(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        self.assertEqual(19, report.case_count)
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

    def test_default_filter_selects_all_19_scored_cases(self):
        report = validate_corpus(REPO_ROOT, suite="kotlin-gradle")

        selected = filter_cases(report.cases, case_ids=None, skills=None)

        self.assertEqual(19, len(selected))

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


if __name__ == "__main__":
    unittest.main()
