import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL
from evals.harness.experiment import (
    _case_digest,
    _judge_packet_path,
    _rejudgment_fingerprint,
    _rejudgment_result_path,
    _skill_source_paths,
    load_raw_records,
    next_attempt_workspace,
    rejudge_packets,
    write_rejudged_reports,
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
            "suite": "compose",
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

    def test_case_digest_includes_fixture_but_ignores_generated_outputs(self):
        case_dir = self.root / "evals" / "cases" / "sample"
        fixture = self.root / "evals" / "fixtures" / "sample-jvm"
        case_dir.mkdir(parents=True)
        fixture.mkdir(parents=True)
        (case_dir / "prompt.md").write_text("Inspect it.\n", encoding="utf-8")
        source = fixture / "Fixture.kt"
        source.write_text("class Fixture\n", encoding="utf-8")
        case = SimpleNamespace(directory=case_dir, fixture="sample-jvm")

        original = _case_digest(case)
        source.write_text("class ChangedFixture\n", encoding="utf-8")
        changed = _case_digest(case)
        (fixture / "build").mkdir()
        (fixture / "build" / "generated.bin").write_bytes(b"generated")

        self.assertNotEqual(original, changed)
        self.assertEqual(changed, _case_digest(case))

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

    def test_rejudging_a_new_runtime_preserves_the_previous_result(self):
        packet = self.root / "judge-packets" / "candidate.json"
        packet.parent.mkdir()
        packet.write_text(
            json.dumps(
                {
                    "candidate_id": "candidate",
                    "task": "Review the subject",
                    "task_mode": "review",
                    "rubric": [{"id": "correct", "text": "Correct"}],
                }
            ),
            encoding="utf-8",
        )
        calls = self.root / "judge-calls.txt"
        fake = self.root / "fake-codex"
        legacy_result = self.root / "rejudgments" / "candidate.json"
        legacy_result.parent.mkdir()
        legacy_result.write_text('{"legacy": true}\n', encoding="utf-8")

        def write_fake(version: str) -> None:
            fake.write_text(
                "#!/bin/sh\n"
                f"if [ \"$1\" = \"--version\" ]; then echo '{version}'; exit 0; fi\n"
                f"echo judge >> '{calls}'\n"
                "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"criteria\\\":[{\\\"id\\\":\\\"correct\\\",\\\"pass\\\":true,\\\"evidence\\\":\\\"diff\\\"}],\\\"overall_pass\\\":true,\\\"rationale\\\":\\\"ok\\\"}\"}}'\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)

        config = JudgeConfig("gpt-5.6-sol", "high")
        with patch("evals.harness.experiment.discover_skill_paths", return_value=()):
            write_fake("codex-cli 1")
            rejudge_packets(
                self.root,
                self.root,
                config,
                execute=True,
                codex_executable=str(fake),
            )
            write_fake("codex-cli 2")
            rejudge_packets(
                self.root,
                self.root,
                config,
                execute=True,
                codex_executable=str(fake),
            )
            rejudge_packets(
                self.root,
                self.root,
                config,
                execute=True,
                codex_executable=str(fake),
            )

        results = sorted((self.root / "rejudgments" / "candidate").glob("*.json"))
        self.assertEqual(2, len(results))
        self.assertEqual(["judge", "judge"], calls.read_text().splitlines())
        self.assertEqual('{"legacy": true}\n', legacy_result.read_text(encoding="utf-8"))
        versions = {
            json.loads(path.read_text(encoding="utf-8"))["payload"]["codex_version"]
            for path in results
        }
        self.assertEqual({"codex-cli 1", "codex-cli 2"}, versions)

    def test_rejudgment_result_path_is_keyed_by_full_fingerprint(self):
        packet = self.root / "packet.json"

        first = _rejudgment_result_path(self.root, packet, "a" * 64)
        second = _rejudgment_result_path(self.root, packet, "b" * 64)

        self.assertNotEqual(first, second)
        self.assertEqual("a" * 64 + ".json", first.name)

    def test_rejudged_report_overlays_a_valid_matching_judgment(self):
        fingerprint = "a" * 64
        candidate_id = "candidate"
        packet_path = _judge_packet_path(self.root, candidate_id, fingerprint, 1)
        packet_path.parent.mkdir(parents=True)
        packet_path.write_text(
            json.dumps(
                {
                    "candidate_id": candidate_id,
                    "rubric": [{"id": "correct", "text": "Correct"}],
                }
            ),
            encoding="utf-8",
        )
        rejudgment_path = self.root / "rejudgments" / packet_path.stem / "result.json"
        write_result(
            rejudgment_path,
            "rejudgment-sha",
            {
                "candidate_id": candidate_id,
                "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
                "judge": {
                    "returncode": 0,
                    "events": [],
                    "output": {
                        "criteria": [
                            {"id": "correct", "pass": True, "evidence": "diff"}
                        ],
                        "overall_pass": True,
                        "rationale": "ok",
                    },
                    "usage": {},
                    "stderr": "",
                    "elapsed_seconds": 1.0,
                    "retries": 0,
                },
            },
        )
        original = {
            "id": "case:none:1",
            "fingerprint": fingerprint,
            "repetition": 1,
            "arm": "none",
            "kind": "direct",
            "expected_skills": [],
            "reported_skills": [],
            "reported_router": False,
            "objective_pass": True,
            "judge_pass": False,
            "outcome_pass": False,
            "forbidden_action_failure": False,
            "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
            "judge": {"returncode": 1, "output": {}},
        }

        paths = write_rejudged_reports(self.root, [original], audit_seed=3)

        rejudged = json.loads(paths["results"].read_text(encoding="utf-8"))
        self.assertTrue(rejudged[0]["judge_pass"])
        self.assertTrue(rejudged[0]["outcome_pass"])
        self.assertEqual(1, rejudged[0]["original_judge"]["returncode"])
        self.assertFalse(original["judge_pass"])
        self.assertFalse(original["outcome_pass"])

    def test_rejudged_report_refuses_missing_judgments(self):
        fingerprint = "a" * 64
        packet_path = _judge_packet_path(self.root, "candidate", fingerprint, 1)
        packet_path.parent.mkdir(parents=True)
        packet_path.write_text(
            json.dumps({"candidate_id": "candidate", "rubric": []}),
            encoding="utf-8",
        )
        original = {
            "id": "case:none:1",
            "fingerprint": fingerprint,
            "repetition": 1,
        }

        with self.assertRaisesRegex(ValueError, "missing rejudgment"):
            write_rejudged_reports(self.root, [original], audit_seed=3)

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

    def test_loading_raw_records_defaults_legacy_results_to_compose(self):
        self.write_raw_record("legacy", "automatic", 1)
        path = self.root / "raw" / "legacy" / "automatic" / "1.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        del document["payload"]["suite"]
        path.write_text(json.dumps(document), encoding="utf-8")

        record = load_raw_records(self.root)[0]

        self.assertEqual("compose", record["suite"])

    def test_loading_raw_records_rejects_mixed_suites(self):
        self.write_raw_record("first", "automatic", 1)
        self.write_raw_record(
            "second",
            "automatic",
            1,
            suite="kotlin-gradle",
        )

        with self.assertRaisesRegex(ValueError, "different run controls: suite"):
            load_raw_records(self.root)

    def test_loading_raw_records_rejects_malformed_payloads(self):
        path = self.root / "raw" / "case" / "automatic" / "1.json"
        path.parent.mkdir(parents=True)

        for document in ({}, {"payload": []}, []):
            with self.subTest(document=document):
                path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "object payload"):
                    load_raw_records(self.root)

    def test_skill_sources_include_references_but_ignore_generated_bytecode(self):
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
        bytecode = (
            self.root
            / "skills"
            / "compose-performance"
            / "scripts"
            / "__pycache__"
            / "helper.cpython-314.pyc"
        )
        bytecode.parent.mkdir(parents=True)
        bytecode.write_bytes(b"generated")
        adjacent_bytecode = bytecode.parent.parent / "helper.pyc"
        adjacent_bytecode.write_bytes(b"generated")

        sources = _skill_source_paths(self.root)

        self.assertIn(reference.resolve(), sources)
        self.assertNotIn(bytecode.resolve(), sources)
        self.assertNotIn(adjacent_bytecode.resolve(), sources)


if __name__ == "__main__":
    unittest.main()
