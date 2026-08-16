import tempfile
import unittest
from pathlib import Path

from evals.harness.results import (
    FingerprintMismatch,
    load_result,
    result_fingerprint,
    run_with_one_retry,
    write_result,
)
from evals.harness.experiment import next_attempt_workspace


class ResultLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_round_trips_an_atomic_fingerprinted_result(self):
        fingerprint = result_fingerprint(
            case_digest="case-sha",
            arm="forced",
            skill_sha="skill-sha",
            codex_version="codex-cli 1",
            model="gpt-5.6-sol",
            reasoning="medium",
        )
        path = self.root / "result.json"

        write_result(path, fingerprint, {"outcome": "pass"})

        self.assertEqual({"outcome": "pass"}, load_result(path, fingerprint))
        self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_refuses_to_resume_a_stale_fingerprint(self):
        path = self.root / "result.json"
        write_result(path, "old", {"outcome": "pass"})

        with self.assertRaises(FingerprintMismatch):
            load_result(path, "new")

    def test_retries_only_once_for_a_retryable_failure(self):
        calls = []

        def operation():
            calls.append(len(calls))
            return {"valid": len(calls) > 1}

        result, retries = run_with_one_retry(operation, lambda value: not value["valid"])

        self.assertTrue(result["valid"])
        self.assertEqual(1, retries)
        self.assertEqual(2, len(calls))

    def test_resume_uses_a_new_attempt_when_interrupted_workspace_exists(self):
        condition = self.root / "condition"
        (condition / "attempt-1").mkdir(parents=True)
        (condition / "attempt-2").mkdir()

        self.assertEqual(condition / "attempt-3", next_attempt_workspace(condition))


if __name__ == "__main__":
    unittest.main()
