import json
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import EVALUATED_TOPICS, validate_corpus
from evals.harness.codex import prepare_workspace
from evals.harness.grade import grade_subject
from evals.harness.experiment import filter_cases, regrade_records
from evals.tests.test_grade import make_result


REPO_ROOT = Path(__file__).resolve().parents[2]


class ComposeMatrixTest(unittest.TestCase):
    def test_has_the_exact_concern_slice_and_router_matrix(self):
        report = validate_corpus(REPO_ROOT, suite="compose")

        self.assertEqual(42, report.case_count)
        benchmark = [case for case in report.cases if not case.calibration]
        calibration = [case for case in report.cases if case.calibration]
        self.assertEqual(38, len(benchmark))
        self.assertEqual(4, len(calibration))
        self.assertTrue(all(case.family == "performance" for case in calibration))
        standalone = [case for case in benchmark if case.kind != "routing"]
        routing = [case for case in benchmark if case.kind == "routing"]
        self.assertEqual(33, len(standalone))
        self.assertEqual(5, len(routing))
        for topic, skill in EVALUATED_TOPICS:
            cases = [case for case in standalone if case.id.startswith(f"{topic}-")]
            self.assertEqual(3, len(cases), skill)
            self.assertTrue(all(case.target_skills == (skill,) for case in cases))
            self.assertEqual(1, sum(case.provenance["kind"] == "historical" for case in cases))
            negative = next(case for case in cases if case.kind == "negative")
            self.assertEqual((skill,), negative.expected_skills)

    def test_calibration_cases_require_explicit_selection(self):
        report = validate_corpus(REPO_ROOT, suite="compose")

        default_cases = filter_cases(report.cases, case_ids=None, skills=None)
        self.assertEqual(38, len(default_cases))
        self.assertFalse(any(case.calibration for case in default_cases))

        challenge_id = "compose-performance-strong-skipping-churn-challenge"
        selected = filter_cases(
            report.cases,
            case_ids=[challenge_id],
            skills=None,
        )
        self.assertEqual([challenge_id], [case.id for case in selected])
        self.assertTrue(selected[0].calibration)

    def test_automatic_prompts_do_not_name_or_invoke_expected_skills(self):
        report = validate_corpus(REPO_ROOT, suite="compose")

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)

    def test_stability_novel_requests_the_repair_recommendation_it_grades(self):
        report = validate_corpus(REPO_ROOT, suite="compose")
        case = next(
            case
            for case in report.cases
            if case.id == "compose-stability-diagnostics-novel"
        )

        self.assertIn("recommend the minimal safe repair order", case.prompt.lower())
        repair_criterion = next(
            criterion
            for criterion in case.rubric
            if criterion["id"] == "criterion-2"
        )
        self.assertIn("recommends first", repair_criterion["text"].lower())
        self.assertIn("then deciding", repair_criterion["text"].lower())

    def test_ui_testing_novel_does_not_require_unnecessary_synchronization(self):
        report = validate_corpus(REPO_ROOT, suite="compose")
        case = next(
            case
            for case in report.cases
            if case.id == "compose-ui-testing-patterns-novel"
        )

        seam_criterion = next(
            criterion
            for criterion in case.rubric
            if criterion["id"] == "criterion-2"
        )["text"].lower()
        self.assertIn("callback or semantic assertion", seam_criterion)
        self.assertIn("does not recommend a fixed delay", seam_criterion)
        self.assertNotIn("synchronization", seam_criterion)

    def test_fixture_declares_pinned_compose_jvm_dependencies_and_offline_wrapper(self):
        fixture = REPO_ROOT / "evals" / "fixtures" / "compose-jvm"

        build = (fixture / "build.gradle.kts").read_text(encoding="utf-8")
        wrapper = (fixture / "gradle" / "wrapper" / "gradle-wrapper.properties").read_text(
            encoding="utf-8"
        )
        self.assertIn("org.jetbrains.kotlin.jvm", build)
        self.assertIn("org.jetbrains.compose", build)
        self.assertRegex(build, r'version "[0-9]')
        self.assertRegex(wrapper, r"gradle-[0-9].*-bin.zip")
        self.assertTrue((fixture / "gradlew").stat().st_mode & 0o111)
        self.assertGreater((fixture / "gradle" / "wrapper" / "gradle-wrapper.jar").stat().st_size, 10_000)

    def test_direct_cases_start_red_while_reviews_and_negatives_start_green(self):
        report = validate_corpus(REPO_ROOT, suite="compose")

        with tempfile.TemporaryDirectory() as temp_dir:
            run_root = Path(temp_dir)
            for case in report.cases:
                with self.subTest(case=case.id):
                    workspace = prepare_workspace(case, REPO_ROOT, run_root / case.id)
                    result = make_result(workspace)
                    grade = grade_subject(case, result)
                    if case.kind == "direct":
                        self.assertFalse(grade.objective_pass)
                    else:
                        self.assertTrue(grade.objective_pass)

    def test_state_authoring_accepts_private_backing_state_with_public_read(self):
        report = validate_corpus(REPO_ROOT, suite="compose")
        case = next(
            case for case in report.cases if case.id == "compose-state-authoring-direct"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = prepare_workspace(case, REPO_ROOT, Path(temp_dir) / case.id)
            subject = workspace / "src/main/kotlin/example/Subject.kt"
            subject.write_text(
                """package example

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

class Counter {
    private var mutableCount by mutableStateOf(0)
    val count: Int get() = mutableCount

    fun increment() { mutableCount += 1 }
}
""",
                encoding="utf-8",
            )
            result = make_result(
                workspace, paths=("src/main/kotlin/example/Subject.kt",)
            )

            self.assertTrue(grade_subject(case, result).objective_pass)

    def test_direct_validators_accept_semantic_equivalents_seen_in_live_runs(self):
        report = validate_corpus(REPO_ROOT, suite="compose")
        replacements = (
            ("compose-slot-api-pattern-direct", """package example
import androidx.compose.runtime.Composable
@Composable fun ActionRow(
  leadingContent: @Composable () -> Unit,
  titleContent: @Composable () -> Unit,
) { leadingContent(); titleContent() }
"""),
            ("compose-stability-diagnostics-direct", """package example
import kotlinx.collections.immutable.ImmutableList
data class FeedState(val items: ImmutableList<String>)
"""),
            ("compose-stability-diagnostics-direct", """package example
import kotlinx.collections.immutable.PersistentList
data class FeedState(val items: PersistentList<String>)
"""),
            ("compose-state-hoisting-direct", """package example
import androidx.compose.runtime.Composable
@Composable fun SearchContent(query: String, onQueryChange: (String) -> Unit) = Unit
@Composable private fun SearchContentPreview() {
  var query by remember { mutableStateOf(\"\") }
  SearchContent(query, onQueryChange = { query = it })
}
"""),
            ("compose-ui-testing-patterns-direct", """package example
import androidx.compose.ui.test.junit4.createComposeRule
class SubjectTest {
  val composeTestRule = createComposeRule()
  fun test() { composeTestRule.setContent {} }
}
"""),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            for index, (case_id, source) in enumerate(replacements):
                with self.subTest(case=case_id):
                    case = next(case for case in report.cases if case.id == case_id)
                    workspace = prepare_workspace(
                        case, REPO_ROOT, Path(temp_dir) / f"{case_id}-{index}"
                    )
                    relative_path = (
                        "src/test/kotlin/example/SubjectTest.kt"
                        if case_id == "compose-ui-testing-patterns-direct"
                        else "src/main/kotlin/example/Subject.kt"
                    )
                    subject = workspace / relative_path
                    subject.write_text(source, encoding="utf-8")
                    result = make_result(workspace, paths=(str(subject.relative_to(workspace)),))
                    self.assertTrue(grade_subject(case, result).objective_pass)

    def test_regrades_persisted_subject_evidence_without_model_calls(self):
        report = validate_corpus(REPO_ROOT, suite="compose")
        case = next(
            case for case in report.cases if case.id == "compose-slot-api-pattern-direct"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            workspace = prepare_workspace(
                case,
                REPO_ROOT,
                output_dir / "workspaces" / case.id / "none" / "1" / "attempt-1",
            )
            subject_path = workspace / "src/main/kotlin/example/Subject.kt"
            subject_path.write_text(
                """package example
import androidx.compose.runtime.Composable
@Composable fun ActionRow(
  leadingContent: @Composable () -> Unit,
  titleContent: @Composable () -> Unit,
) { leadingContent(); titleContent() }
""",
                encoding="utf-8",
            )
            result = make_result(
                workspace,
                paths=(str(subject_path.relative_to(workspace)),),
            )
            record = {
                "id": f"{case.id}:none:1",
                "case_id": case.id,
                "arm": "none",
                "kind": case.kind,
                "expected_skills": list(case.expected_skills),
                "reported_skills": [],
                "reported_router": False,
                "objective_pass": False,
                "judge_pass": True,
                "outcome_pass": False,
                "forbidden_action_failure": False,
                "subject": {
                    "command": ["codex", "-C", str(workspace)],
                    "events": list(result.events),
                    "returncode": result.returncode,
                    "final_output": result.final_output,
                    "usage": {},
                    "changed_paths": list(result.changed_paths),
                    "diff": result.diff,
                    "elapsed_seconds": 0.1,
                    "stderr": "",
                    "retries": 0,
                },
                "judge": {"returncode": 0, "retries": 0},
            }

            paths = regrade_records(
                REPO_ROOT, list(report.cases), output_dir, [record], audit_seed=3
            )
            regraded = json.loads(paths["results"].read_text(encoding="utf-8"))

            self.assertTrue(regraded[0]["objective_pass"])
            self.assertTrue(regraded[0]["outcome_pass"])
            self.assertFalse((output_dir / "raw").exists())


if __name__ == "__main__":
    unittest.main()
