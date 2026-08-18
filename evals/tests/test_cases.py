import json
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import CaseValidationError, load_case, validate_corpus


def valid_manifest(**overrides):
    manifest = {
        "id": "compose-state-authoring-direct",
        "title": "Replace unsafe public mutable state",
        "family": "state-effects",
        "target_skills": ["compose-state-and-effects"],
        "expected_skills": ["compose-state-and-effects"],
        "task_mode": "edit",
        "kind": "direct",
        "fixture": "compose-jvm",
        "allowed_write_paths": ["src/main/kotlin/example/Subject.kt"],
        "validators": [
            {"argv": ["python3", "checks/check_subject.py"], "timeout_seconds": 30}
        ],
        "rubric": [{"id": "safe-state", "text": "State writes are snapshot-aware"}],
        "provenance": {"kind": "synthetic"},
    }
    manifest.update(overrides)
    return manifest


class CaseContractTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "skills" / "compose-state-and-effects").mkdir(parents=True)
        (self.root / "skills" / "compose-state-and-effects" / "SKILL.md").write_text(
            "---\nname: compose-state-and-effects\n---\n", encoding="utf-8"
        )
        (self.root / "skills" / "using-chrisbanes-skills").mkdir(parents=True)
        (self.root / "skills" / "using-chrisbanes-skills" / "SKILL.md").write_text(
            "---\nname: using-chrisbanes-skills\n---\n", encoding="utf-8"
        )
        (self.root / "evals" / "fixtures" / "compose-jvm").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_case(self, manifest):
        case_dir = self.root / "evals" / "cases" / manifest["id"]
        case_dir.mkdir(parents=True)
        (case_dir / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
        (case_dir / "prompt.md").write_text("Fix the subject.\n", encoding="utf-8")
        return case_dir

    def test_loads_a_valid_case_through_the_manifest_contract(self):
        case_dir = self.write_case(valid_manifest())

        case = load_case(case_dir / "case.json", self.root)

        self.assertEqual("compose-state-authoring-direct", case.id)
        self.assertEqual(("compose-state-and-effects",), case.expected_skills)
        self.assertFalse(case.calibration)
        self.assertEqual("Fix the subject.\n", case.prompt)

    def test_requires_calibration_marker_to_be_boolean(self):
        case_dir = self.write_case(valid_manifest(calibration="yes"))

        with self.assertRaisesRegex(CaseValidationError, "calibration must be a boolean"):
            load_case(case_dir / "case.json", self.root)

    def test_rejects_validator_paths_that_escape_the_case_contract(self):
        for argv in (["../check.py"], ["/tmp/check.py"]):
            with self.subTest(argv=argv):
                case_dir = self.write_case(
                    valid_manifest(
                        id="unsafe-" + str(len(argv[0])),
                        validators=[{"argv": argv, "timeout_seconds": 30}],
                    )
                )

                with self.assertRaisesRegex(CaseValidationError, "validator argv"):
                    load_case(case_dir / "case.json", self.root)

    def test_rejects_mutable_or_ambiguous_historical_provenance(self):
        historical = {
            "kind": "historical",
            "source_url": "https://github.com/example/project",
            "revision": "main",
            "license": "Apache-2.0",
            "normalization_note": "Package only",
        }
        case_dir = self.write_case(
            valid_manifest(id="historical-case", provenance=historical)
        )

        with self.assertRaisesRegex(CaseValidationError, "full lowercase Git SHA"):
            load_case(case_dir / "case.json", self.root)

    def test_reports_incomplete_corpus_without_weakening_strict_validation(self):
        self.write_case(valid_manifest())

        report = validate_corpus(self.root, allow_incomplete=True)

        self.assertEqual(1, report.case_count)
        self.assertIn("compose-state-hoisting", "\n".join(report.missing_coverage))
        with self.assertRaisesRegex(CaseValidationError, "corpus coverage"):
            validate_corpus(self.root)


if __name__ == "__main__":
    unittest.main()
