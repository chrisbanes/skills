import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL
from evals.harness.experiment import (
    JUDGE_PROTOCOL_SOURCES,
    _attempt_payload,
    _case_digest,
    _judge_packet_path,
    _judge_protocol_digest,
    _rejudgment_fingerprint,
    _rejudgment_result_path,
    _skill_catalog_digest,
    _skill_source_paths,
    _subject_result_from_record,
    execute_experiment,
    load_raw_records,
    next_attempt_workspace,
    preflight,
    reconcile_automatic_eligibility,
    regrade_records,
    rejudge_packets,
    write_rejudged_reports,
)
from evals.harness.judge import JudgeConfig, build_judge_command
from evals.harness.cases import Validator
from evals.harness.runner import RunConfig, record_judge_runtime, record_runtime
from evals.harness.results import (
    FingerprintMismatch,
    load_result,
    result_fingerprint,
    run_with_one_retry,
    write_result,
)
from evals.tests import test_codex_runner
from evals.tests.test_claude_runner import BODY, TARGET, ClaudeForcedIntegrityTest, fixture_lines
from evals.tests.test_codex_runner import sample_case


class ResultLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_matching_rejudgment(self, packet_path: Path, payload: dict) -> None:
        config = JudgeConfig("gpt-5.6-sol", "high")
        fingerprint = _rejudgment_fingerprint(
            packet_path,
            config,
            skill_catalog_digest=_skill_catalog_digest(()),
            codex_version="codex-cli 1",
            judge_prompt_digest=hashlib.sha256(
                build_judge_command(packet_path, self.root, config, skill_paths=())[-1].encode()
            ).hexdigest(),
        )
        write_result(
            _rejudgment_result_path(self.root, packet_path, fingerprint),
            fingerprint,
            {**payload, "codex_version": "codex-cli 1"},
        )

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

    def test_attempt_payload_counts_completed_turns(self):
        attempt = SimpleNamespace(
            returncode=0,
            usage={"input_tokens": 10, "output_tokens": 2},
            events=(
                {"type": "turn.started"},
                {"type": "turn.completed"},
                {"type": "turn.completed"},
            ),
            elapsed_seconds=1.5,
        )

        payload = _attempt_payload(attempt)

        self.assertEqual(2, payload["turns"])

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

    def test_judge_protocol_changes_the_experiment_fingerprint(self):
        common = {
            "case_digest": "case-sha",
            "arm": "automatic",
            "skill_sha": "skill-sha",
            "codex_version": "codex-cli 1",
            "model": "gpt-6-luna",
            "reasoning": "high",
        }
        first = result_fingerprint(**common, judge_protocol_digest="prompt-one")
        second = result_fingerprint(**common, judge_protocol_digest="prompt-two")
        self.assertNotEqual(first, second)

    def test_packet_dependency_changes_judge_protocol_digest(self):
        for name in JUDGE_PROTOCOL_SOURCES:
            (self.root / name).write_text("original", encoding="utf-8")
        baseline = _judge_protocol_digest(self.root)
        for name in JUDGE_PROTOCOL_SOURCES:
            with self.subTest(source=name):
                path = self.root / name
                path.write_text("changed", encoding="utf-8")
                self.assertNotEqual(baseline, _judge_protocol_digest(self.root))
                path.write_text("original", encoding="utf-8")

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
        (fixture / ".kotlin" / "errors").mkdir(parents=True)
        (fixture / ".kotlin" / "errors" / "compiler.log").write_text(
            "generated diagnostic\n", encoding="utf-8"
        )

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
            judge_prompt_digest="prompt-sha",
        )
        second = _rejudgment_fingerprint(
            packet,
            config,
            skill_catalog_digest="catalog-sha",
            codex_version="codex-cli 2",
            judge_prompt_digest="prompt-sha",
        )

        self.assertNotEqual(first, second)

        revised_prompt = _rejudgment_fingerprint(
            packet,
            config,
            skill_catalog_digest="catalog-sha",
            codex_version="codex-cli 1",
            judge_prompt_digest="revised-prompt-sha",
        )
        self.assertNotEqual(first, revised_prompt)

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
        self.write_matching_rejudgment(
            packet_path,
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
        write_result(
            self.root / "rejudgments" / packet_path.stem / ("0" * 64 + ".json"),
            "0" * 64,
            {
                "candidate_id": candidate_id,
                "codex_version": "codex-cli 1",
                "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
                "judge": {"returncode": 1, "output": {}},
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

        with patch("evals.harness.experiment.discover_skill_paths", return_value=()):
            paths = write_rejudged_reports(
                self.root, [original], audit_seed=3, repo_root=self.root
            )

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

        with self.assertRaisesRegex(ValueError, "missing current rejudgment"):
            write_rejudged_reports(
                self.root, [original], audit_seed=3, repo_root=self.root
            )

    def test_rejudged_report_refuses_judgment_from_old_prompt(self):
        fingerprint = "a" * 64
        packet_path = _judge_packet_path(self.root, "candidate", fingerprint, 1)
        packet_path.parent.mkdir(parents=True)
        packet_path.write_text(
            json.dumps({"candidate_id": "candidate", "rubric": []}),
            encoding="utf-8",
        )
        self.write_matching_rejudgment(
            packet_path,
            {
                "candidate_id": "candidate",
                "judge_model": {"model": "gpt-5.6-sol", "reasoning": "high"},
                "judge": {"returncode": 0, "output": {"criteria": [], "overall_pass": True}},
            },
        )
        original = {
            "id": "case:none:1", "fingerprint": fingerprint,
            "repetition": 1, "arm": "none",
        }

        with patch("evals.harness.experiment.discover_skill_paths", return_value=()), \
             patch("evals.harness.experiment.build_judge_command", return_value=["changed prompt"]):
            with self.assertRaisesRegex(ValueError, "missing current rejudgment"):
                write_rejudged_reports(
                    self.root, [original], audit_seed=3, repo_root=self.root
                )

    def test_rejudged_report_skips_ineligible_automatic_records(self):
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
        self.write_matching_rejudgment(
            packet_path,
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
        included = {
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
            "automatic_eligible": True,
        }
        ineligible = {
            "id": "explicit:automatic:1",
            "fingerprint": "b" * 64,
            "repetition": 1,
            "arm": "automatic",
            "automatic_eligible": False,
        }

        with patch("evals.harness.experiment.discover_skill_paths", return_value=()):
            paths = write_rejudged_reports(
                self.root, [included, ineligible], audit_seed=3,
                repo_root=self.root,
            )

        rejudged = json.loads(paths["results"].read_text(encoding="utf-8"))
        self.assertEqual(["case:none:1"], [record["id"] for record in rejudged])

    def test_rejudgment_planning_skips_ineligible_automatic_packets(self):
        included = _judge_packet_path(self.root, "included", "a" * 64, 1)
        excluded = _judge_packet_path(self.root, "excluded", "b" * 64, 1)
        included.parent.mkdir(parents=True)
        included.write_text("{}\n", encoding="utf-8")
        excluded.write_text("{}\n", encoding="utf-8")

        plan = rejudge_packets(
            self.root,
            self.root,
            JudgeConfig("gpt-5.6-sol", "high"),
            execute=False,
            records=[
                {
                    "fingerprint": "a" * 64,
                    "repetition": 1,
                    "arm": "automatic",
                    "automatic_eligible": True,
                },
                {
                    "fingerprint": "b" * 64,
                    "repetition": 1,
                    "arm": "automatic",
                    "automatic_eligible": False,
                },
            ],
        )

        self.assertEqual(1, plan["packet_count"])
        self.assertEqual(1, plan["judge_calls"])
        self.assertEqual(1, plan["skipped_packet_count"])

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

    def test_loading_raw_records_rejects_mixed_runtimes_and_builtin_sets(self):
        claude = {"runtime": "claude", "runtime_version": "2.1.296", "builtin_skills": ["a"]}
        for override, differing in (
            ({}, "runtime, runtime_version, builtin_skills"),
            ({**claude, "runtime_version": "2.1.300"}, "runtime_version"),
            ({**claude, "builtin_skills": ["a", "b"]}, "builtin_skills"),
            ({**claude, "judge_runtime": "claude", "judge_runtime_version": "2.1.296"},
             "codex_version, judge_runtime, judge_runtime_version"),
        ):
            with self.subTest(differing):
                self.write_raw_record("first", "automatic", 1, **claude)
                self.write_raw_record("second", "automatic", 1, **override)
                with self.assertRaisesRegex(
                    ValueError, f"different run controls: {differing}$"
                ):
                    load_raw_records(self.root)

    def test_builtin_skills_change_the_fingerprint_only_when_given(self):
        common = {
            "case_digest": "case-sha", "arm": "none", "skill_sha": "skill-sha",
            "codex_version": None, "model": "claude-haiku-5-5", "reasoning": "high",
            "runtime": "claude", "runtime_version": "2.1.296",
        }

        base = result_fingerprint(**common)
        first = result_fingerprint(**common, builtin_skills=("debug", "simplify"))

        self.assertNotEqual(base, first)
        self.assertEqual(first, result_fingerprint(**common, builtin_skills=("simplify", "debug")))
        self.assertNotEqual(first, result_fingerprint(**common, builtin_skills=("debug",)))

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

    def test_codex_fingerprint_unchanged(self):
        # Golden digests computed at baseline, before the runtime fields existed.
        fields = {
            "case_digest": "c" * 64,
            "arm": "forced",
            "skill_sha": "abc123",
            "codex_version": "codex-cli 1.2.3",
            "model": "gpt-6-sol",
            "reasoning": "high",
            "judge_model": "gpt-6-sol",
            "judge_reasoning": "high",
            "judge_protocol_digest": "d" * 64,
            "skill_catalog_digest": "e" * 64,
        }

        self.assertEqual(
            "41f20e7d8e8b6828459d94fbc04500dd5a36d7765e297706f73fbbd43a2a7d30",
            result_fingerprint(**fields),
        )
        self.assertEqual(
            "83bc2c53dfc31d9a494e6a9deffd45db56789534296af1bbf09344027ab732e3",
            result_fingerprint(
                case_digest="c" * 64,
                arm="none",
                skill_sha="abc123",
                codex_version="codex-cli 1.2.3",
                model="gpt-6-sol",
                reasoning="high",
            ),
        )
        self.assertNotEqual(
            result_fingerprint(**fields),
            result_fingerprint(**fields, runtime="claude"),
        )

    def test_legacy_record_defaults(self):
        workspace = self.root / "workspaces" / "case" / "none" / "1" / "attempt-1"
        workspace.mkdir(parents=True)
        legacy = {
            "id": "case:none:1",
            "case_id": "case",
            "arm": "none",
            "subject": {"command": ["codex", "exec", "-C", str(workspace), "prompt"]},
        }

        self.assertEqual("codex", record_runtime(legacy))
        self.assertEqual("codex", record_judge_runtime(legacy))
        result = _subject_result_from_record(legacy, self.root)
        self.assertEqual(workspace.resolve(), result.workspace)
        self.assertEqual("codex", result.runtime)

        current = {
            **legacy,
            "runtime": "codex",
            "subject": {"command": ["other"], "workspace": str(workspace)},
        }
        self.assertEqual(
            workspace.resolve(), _subject_result_from_record(current, self.root).workspace
        )


FAKE_CLAUDE = """#!/bin/sh
case "$*" in
  "--version") echo version >> '{log}'; echo "2.1.296 (Claude Code)"; exit 0;;
  *"Reply with OK."*) echo discovery >> '{log}';;
  *"--tools Read --allowedTools"*) echo judge >> '{log}'; cat '{judge}'; exit 0;;
  *) echo subject >> '{log}';;
esac
if [ -d .claude/skills ]; then
  skills="[$(ls .claude/skills | sed 's/.*/"&"/' | paste -sd, -)]"
else
  skills='["debug","simplify"]'
fi
printf '{{"type":"system","subtype":"init","skills":%s,"mcp_servers":[]}}\\n' "$skills"
cat '{subject}'
"""
FAKE_CODEX = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "codex-cli 1.2.3"; exit 0; fi
printf '%s\\n' '{judgment}'
"""
JUDGMENT = {
    "criteria": [
        {"id": "c1", "pass": True, "evidence": "diff"},
        {"id": "c2", "pass": True, "evidence": "diff"},
    ],
    "overall_pass": True,
    "rationale": "ok",
}


class ClaudeExperimentTest(unittest.TestCase):
    tearDown = test_codex_runner.CodexRunnerTest.tearDown

    def setUp(self):
        test_codex_runner.CodexRunnerTest.setUp(self)
        (self.root / "evals" / "schemas" / "judge-output.schema.json").write_text(
            "{}\n", encoding="utf-8"
        )
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@localhost",
             "commit", "-qm", "baseline"],
            cwd=self.root, check=True,
        )
        (self.root / "skills" / TARGET / "SKILL.md").write_text(
            f"---\nname: {TARGET}\ndescription: Use when testing.\n---\n\n{BODY}",
            encoding="utf-8",
        )
        subject = self.root / "subject.jsonl"
        subject.write_text(
            "".join(
                json.dumps(line) + "\n"
                for line in ClaudeForcedIntegrityTest.forced_lines(None)
            ),
            encoding="utf-8",
        )
        self.claude = self.root / "fake-claude"
        self.claude.write_text(
            FAKE_CLAUDE.format(
                judge=Path(__file__).parent / "data" / "claude_stream_judge.jsonl",
                subject=subject,
                log=self.root / "claude.log",
            ),
            encoding="utf-8",
        )
        self.codex = self.root / "fake-codex"
        self.codex.write_text(
            FAKE_CODEX.format(judgment=json.dumps({
                "type": "item.completed",
                "item": {"type": "agent_message", "text": json.dumps(JUDGMENT)},
            })),
            encoding="utf-8",
        )
        for script in (self.claude, self.codex):
            script.chmod(0o755)
        self.case = replace(
            sample_case(self.root),
            validators=(Validator(("python3", "-c", "pass"), 30),),
            rubric=({"id": "c1", "text": "One"}, {"id": "c2", "text": "Two"}),
        )
        self.output = self.root / "runs" / "out"

    def run_experiment(self, judge_runtime, judge_model):
        with patch("evals.harness.experiment.discover_skill_paths", return_value=()):
            return execute_experiment(
                self.root,
                [self.case],
                arms=["forced"],
                repetitions=1,
                run_config=RunConfig("claude-haiku-5-5", "high"),
                judge_config=JudgeConfig(judge_model, "high"),
                output_dir=self.output,
                runtime="claude",
                judge_runtime=judge_runtime,
                codex_executable=str(self.codex),
                claude_executable=str(self.claude),
            )

    def calls(self):
        log = self.root / "claude.log"
        return log.read_text().split() if log.is_file() else []

    def raw_payload(self):
        (path,) = (self.output / "raw").glob("*/*/*.json")
        return json.loads(path.read_text(encoding="utf-8"))["payload"]

    def test_claude_subject_with_codex_judge_records_both_runtimes(self):
        paths = self.run_experiment("codex", "gpt-6-sol")

        record = self.raw_payload()
        self.assertEqual("claude", record["runtime"])
        self.assertEqual("2.1.296 (Claude Code)", record["runtime_version"])
        self.assertEqual("codex", record["judge_runtime"])
        self.assertEqual("codex-cli 1.2.3", record["judge_runtime_version"])
        self.assertEqual("codex-cli 1.2.3", record["codex_version"])
        self.assertEqual(["debug", "simplify"], record["builtin_skills"])
        self.assertEqual([TARGET], record["observed_skills"])
        self.assertTrue(record["forced_target_preflight"]["valid"])
        workspace = Path(record["subject"]["workspace"])
        self.assertTrue(workspace.is_relative_to(self.output.resolve() / "workspaces"))
        self.assertTrue((workspace / ".claude" / "skills" / TARGET / "SKILL.md").is_file())
        command = record["subject"]["command"]
        self.assertEqual(
            {"debug": "off", "simplify": "off"},
            json.loads(command[command.index("--settings") + 1])["skillOverrides"],
        )
        self.assertEqual(1, len(json.loads(paths["results"].read_text())))
        self.assertEqual(["version", "discovery", "subject"], self.calls())

    def test_claude_judge_without_codex_omits_the_codex_version(self):
        self.run_experiment("claude", "claude-haiku-5-5")

        record = self.raw_payload()
        self.assertEqual("claude", record["judge_runtime"])
        self.assertEqual("2.1.296 (Claude Code)", record["judge_runtime_version"])
        self.assertNotIn("codex_version", record)
        self.assertEqual(
            {"c1", "c2"}, {item["id"] for item in record["judge"]["output"]["criteria"]}
        )
        self.assertTrue(record["judge_pass"])
        # Claude-only records still load: codex_version is not a control for them.
        self.assertEqual([record["id"]], [r["id"] for r in load_raw_records(self.output)])

    def test_claude_records_round_trip_through_report_regrade_and_rejudge(self):
        self.run_experiment("codex", "gpt-6-sol")
        before = self.calls()
        with patch("evals.harness.experiment.discover_skill_paths", return_value=()):
            records = load_raw_records(self.output)
            reconcile_automatic_eligibility(self.root, [self.case], records)
            regraded = regrade_records(
                self.root, [self.case], self.output, records, audit_seed=1
            )
            # Regrade reuses the recorded data: no discovery or model call.
            self.assertEqual(before, self.calls())
            plan = rejudge_packets(
                self.root, self.output, JudgeConfig("claude-haiku-5-5", "high"),
                execute=True, judge_runtime="claude", claude_executable=str(self.claude),
            )
            rejudged = write_rejudged_reports(
                self.output, records, audit_seed=1, repo_root=self.root
            )

        self.assertEqual("claude", record_runtime(records[0]))
        self.assertEqual("codex", record_judge_runtime(records[0]))
        self.assertEqual(
            [TARGET], json.loads(regraded["results"].read_text())[0]["observed_skills"]
        )
        self.assertEqual(1, plan["completed"])
        (final,) = json.loads(rejudged["results"].read_text())
        self.assertTrue(final["judge_pass"])
        self.assertEqual("claude", final["judge_runtime"])
        self.assertEqual("2.1.296 (Claude Code)", final["judge_runtime_version"])
        self.assertEqual("codex", records[0]["judge_runtime"])
        # Rejudging only checks the version and judges once; it never rediscovers.
        self.assertEqual(["version", "judge"], self.calls()[len(before):])

    def test_preflight_reports_each_selected_runtime_version(self):
        with patch("evals.harness.experiment._command_output") as output:
            output.side_effect = lambda command, **_: " ".join(command)
            versions, skill_sha = preflight(
                self.root, "codex-x", (), runtimes=("claude", "codex"),
                claude_executable="claude-x",
            )

        self.assertEqual(
            {"codex": "codex-x --version", "claude": "claude-x --version"}, versions
        )
        self.assertEqual("git rev-parse HEAD", skill_sha)
        self.assertEqual(
            [["codex-x", "--version"], ["claude-x", "--version"], ["git", "rev-parse", "HEAD"]],
            [call.args[0] for call in output.call_args_list],
        )


if __name__ == "__main__":
    unittest.main()
