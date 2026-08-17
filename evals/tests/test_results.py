import json
import tempfile
import unittest
from pathlib import Path

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL
from evals.harness.experiment import (
    _judge_packet_path,
    _rejudgment_fingerprint,
    _skill_source_paths,
    load_raw_records,
    next_attempt_workspace,
)
from evals.harness.judge import JudgeConfig
from evals.harness.results import (
    FingerprintMismatch,
    load_result,
    result_fingerprint,
    run_with_one_retry,
    write_result,
)


class ResultLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_raw_record(self, case: str, arm: str, repetition: int, **overrides):
        payload = {
            "id": f"{case}:{arm}:{repetition}",
            "codex_version": "codex-cli 1",
            "skill_sha": "skill-sha",
            "skill_catalog_digest": "catalog-sha",
            "subject_model": {"model": "gpt-5.6-terra", "reasoning": "medium"},
            "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
            "subject": {"final_output": {"skills_used": []}},
        }
        payload.update(overrides)
        path = self.root / "raw" / case / arm / f"{repetition}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"payload": payload}), encoding="utf-8")

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

    def test_skill_catalog_changes_the_experiment_fingerprint(self):
        common = {
            "case_digest": "case-sha",
            "arm": "automatic",
            "skill_sha": "skill-sha",
            "codex_version": "codex-cli 1",
            "model": "gpt-5.6-sol",
            "reasoning": "medium",
        }

        first = result_fingerprint(**common, skill_catalog_digest="catalog-one")
        second = result_fingerprint(**common, skill_catalog_digest="catalog-two")

        self.assertNotEqual(first, second)

    def test_judge_packet_paths_are_unique_across_arms_without_disclosing_them(self):
        common = {
            "case_digest": "case-sha",
            "skill_sha": "skill-sha",
            "codex_version": "codex-cli 1",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
        }
        forced = result_fingerprint(**common, arm="forced")
        automatic = result_fingerprint(**common, arm="automatic")

        forced_path = _judge_packet_path(self.root, "candidate", forced, 1)
        automatic_path = _judge_packet_path(self.root, "candidate", automatic, 1)

        self.assertNotEqual(forced_path, automatic_path)
        self.assertNotIn("forced", forced_path.name)
        self.assertNotIn("automatic", automatic_path.name)

    def test_rejudgment_fingerprint_includes_codex_runtime_version(self):
        packet = self.root / "packet.json"
        packet.write_text("{}\n", encoding="utf-8")
        config = JudgeConfig("gpt-5.6-sol", "high")

        first = _rejudgment_fingerprint(
            packet,
            config,
            skill_catalog_digest="catalog-sha",
            codex_version="codex-cli 1",
        )
        second = _rejudgment_fingerprint(
            packet,
            config,
            skill_catalog_digest="catalog-sha",
            codex_version="codex-cli 2",
        )

        self.assertNotEqual(first, second)

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

    def test_loading_raw_records_canonicalizes_plugin_qualified_routing(self):
        self.write_raw_record(
            "case",
            "automatic",
            1,
            subject={
                "final_output": {
                    "skills_used": [
                        "chrisbanes-skills:compose-state-and-effects"
                    ]
                }
            },
        )

        record = load_raw_records(self.root)[0]

        self.assertEqual(["compose-state-and-effects"], record["reported_skills"])

    def test_loading_raw_records_rejects_incomparable_run_controls(self):
        self.write_raw_record("first", "automatic", 1)
        self.write_raw_record(
            "second",
            "automatic",
            1,
            subject_model={"model": "gpt-5.6-sol", "reasoning": "high"},
        )

        with self.assertRaisesRegex(ValueError, "different run controls: subject_model"):
            load_raw_records(self.root)

    def test_skill_sources_include_cluster_references(self):
        for skill in (*COMPOSE_SKILLS, ROUTER_SKILL):
            skill_file = self.root / "skills" / skill / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text(f"---\nname: {skill}\n---\n", encoding="utf-8")
        reference = (
            self.root
            / "skills"
            / "compose-performance"
            / "references"
            / "stability.md"
        )
        reference.parent.mkdir()
        reference.write_text("Stability guidance\n", encoding="utf-8")

        sources = _skill_source_paths(self.root)

        self.assertIn(reference.resolve(), sources)


if __name__ == "__main__":
    unittest.main()
