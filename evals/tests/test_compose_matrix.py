import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import COMPOSE_SKILLS, validate_corpus
from evals.harness.codex import prepare_workspace
from evals.harness.grade import grade_subject
from evals.tests.test_grade import make_result


REPO_ROOT = Path(__file__).resolve().parents[2]


class ComposeMatrixTest(unittest.TestCase):
    def test_has_the_exact_standalone_and_router_overlap_matrix(self):
        report = validate_corpus(REPO_ROOT)

        self.assertEqual(38, report.case_count)
        standalone = [case for case in report.cases if case.kind != "overlap"]
        overlaps = [case for case in report.cases if case.kind == "overlap"]
        self.assertEqual(33, len(standalone))
        self.assertEqual(5, len(overlaps))
        for skill in COMPOSE_SKILLS:
            cases = [case for case in standalone if case.target_skills == (skill,)]
            self.assertEqual(3, len(cases), skill)
            self.assertEqual(1, sum(case.provenance["kind"] == "historical" for case in cases))
            negative = next(case for case in cases if case.kind == "negative")
            self.assertEqual((skill,), negative.expected_skills)

    def test_automatic_prompts_do_not_name_or_invoke_expected_skills(self):
        report = validate_corpus(REPO_ROOT)

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)

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
        report = validate_corpus(REPO_ROOT)

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
        report = validate_corpus(REPO_ROOT)
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


if __name__ == "__main__":
    unittest.main()
