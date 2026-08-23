import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from evals.harness.cases import COMPOSE_SKILLS, ROUTER_SKILL, EvalCase, Validator
from evals.harness.codex import (
    RunConfig,
    build_subject_command,
    discover_skill_paths,
    prepare_workspace,
    run_subject,
)
from evals.harness.suites import PUBLIC_SKILLS


def sample_case(root: Path, *, task_mode: str = "edit") -> EvalCase:
    case_dir = root / "evals" / "cases" / "sample"
    case_dir.mkdir(parents=True, exist_ok=True)
    overlay = case_dir / "overlay" / "src" / "main" / "kotlin" / "example"
    overlay.mkdir(parents=True, exist_ok=True)
    (overlay / "Subject.kt").write_text("package example\n", encoding="utf-8")
    return EvalCase(
        id="sample",
        title="Sample",
        family="state-effects",
        target_skills=("compose-state-and-effects",),
        expected_skills=("compose-state-and-effects",),
        task_mode=task_mode,
        kind="direct",
        fixture="compose-jvm",
        allowed_write_paths=("src/main/kotlin/example/Subject.kt",) if task_mode == "edit" else (),
        validators=(Validator(("python3", "checks/check.py"), 30),),
        rubric=({"id": "correct", "text": "The result is correct"},),
        provenance={"kind": "synthetic"},
        prompt="Improve the subject without mentioning a skill.\n",
        directory=case_dir,
    )


class CodexRunnerTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        fixture = self.root / "evals" / "fixtures" / "compose-jvm"
        (fixture / "src" / "main" / "kotlin" / "example").mkdir(parents=True)
        (fixture / "src" / "main" / "kotlin" / "example" / "Base.kt").write_text(
            "package example\n", encoding="utf-8"
        )
        (fixture / "gradlew").write_text("#!/bin/sh\necho real\n", encoding="utf-8")
        (fixture / "gradlew").chmod(0o755)
        (fixture / "subject-gradlew").write_text(
            "#!/bin/sh\necho simulated\n", encoding="utf-8"
        )
        (fixture / "subject-gradlew").chmod(0o755)
        for skill in PUBLIC_SKILLS:
            skill_dir = self.root / "skills" / skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"---\nname: {skill}\n---\n", encoding="utf-8")
        schemas = self.root / "evals" / "schemas"
        schemas.mkdir(parents=True)
        (schemas / "subject-output.schema.json").write_text("{}\n", encoding="utf-8")
        self.config = RunConfig(model="gpt-5.6-terra", reasoning="medium")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_builds_three_explicit_and_isolated_skill_arms(self):
        case = sample_case(self.root)
        workspace = self.root / "workspace"
        unrelated = self.root / "global-skills" / "ponytail" / "SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("---\nname: ponytail\n---\n", encoding="utf-8")
        catalog = (*discover_skill_paths(self.root, roots=(unrelated.parents[1],)),)

        none = build_subject_command(
            case, "none", self.root, workspace, self.config, skill_paths=catalog
        )
        forced = build_subject_command(
            case, "forced", self.root, workspace, self.config, skill_paths=catalog
        )
        automatic = build_subject_command(
            case, "automatic", self.root, workspace, self.config, skill_paths=catalog
        )

        for command in (none, forced, automatic):
            rendered = " ".join(command)
            self.assertIn("--ephemeral", command)
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--ignore-rules", command)
            self.assertIn("--strict-config", command)
            self.assertIn("--json", command)
            self.assertIn('model_reasoning_effort="medium"', rendered)
            self.assertIn("sandbox_workspace_write.network_access=false", rendered)
            self.assertIn('web_search="disabled"', rendered)
            self.assertIn(str(unrelated.resolve()), rendered)
            self.assertIn("enabled = false", rendered)
            self.assertIn("SKILL.md", rendered)
        self.assertEqual(1, " ".join(none).count("path = "))
        self.assertEqual(2, " ".join(forced).count("path = "))
        self.assertEqual(16, " ".join(automatic).count("path = "))
        self.assertEqual(0, " ".join(none).count("enabled = true"))
        self.assertEqual(1, " ".join(forced).count("enabled = true"))
        self.assertEqual(15, " ".join(automatic).count("enabled = true"))
        self.assertIn("$compose-state-and-effects", forced[-1])
        self.assertNotIn("$compose-state-and-effects", automatic[-1])
        self.assertIn("If you run Gradle, use `--offline --no-scan`.", automatic[-1])
        self.assertIn("only skills whose SKILL.md instructions you actually read", automatic[-1])
        self.assertNotEqual(case.prompt, automatic[-1])

    def test_discovers_repo_and_external_skill_files_without_duplicates(self):
        external = self.root / "external" / "one" / "SKILL.md"
        external.parent.mkdir(parents=True)
        external.write_text("---\nname: one\n---\n", encoding="utf-8")

        paths = discover_skill_paths(
            self.root, roots=(external.parents[1], external.parents[1])
        )

        self.assertEqual(1, len(paths))
        self.assertEqual(1, paths.count(external.resolve()))

    def test_none_arm_does_not_disclose_repo_skill_or_schema_paths(self):
        case = sample_case(self.root)
        workspace = self.root / "workspace"

        command = build_subject_command(
            case, "none", self.root, workspace, self.config, skill_paths=()
        )
        rendered = " ".join(command)

        self.assertNotIn(str(self.root / "skills"), rendered)
        self.assertNotIn("compose-state-and-effects", rendered)
        self.assertIn(str(workspace / ".eval/subject-output.schema.json"), rendered)

    def test_selects_read_only_or_workspace_write_from_the_case_contract(self):
        workspace = self.root / "workspace"
        edit = build_subject_command(sample_case(self.root), "none", self.root, workspace, self.config)
        review = build_subject_command(
            sample_case(self.root, task_mode="review"), "none", self.root, workspace, self.config
        )

        self.assertEqual("workspace-write", edit[edit.index("--sandbox") + 1])
        self.assertNotIn("--approve-for-me", edit)
        self.assertEqual("read-only", review[review.index("--sandbox") + 1])
        self.assertNotIn("--approve-for-me", review)

    def test_forced_negative_control_invokes_target_while_behavior_stays_negative(self):
        case = replace(sample_case(self.root), kind="negative")

        command = build_subject_command(
            case, "forced", self.root, self.root / "workspace", self.config
        )

        self.assertEqual(1, " ".join(command).count("enabled = true"))
        self.assertIn("$compose-state-and-effects", command[-1])

    def test_prepares_independent_fixture_and_overlay_copies(self):
        case = sample_case(self.root)
        fixture = self.root / "evals" / "fixtures" / case.fixture
        (fixture / ".gradle").mkdir()
        (fixture / ".gradle" / "cache.bin").write_text("generated\n", encoding="utf-8")
        (fixture / "build").mkdir()
        (fixture / "build" / "output.bin").write_text("generated\n", encoding="utf-8")
        first = prepare_workspace(case, self.root, self.root / "runs" / "first")
        second = prepare_workspace(case, self.root, self.root / "runs" / "second")

        subject = first / "src" / "main" / "kotlin" / "example" / "Subject.kt"
        subject.write_text("changed\n", encoding="utf-8")
        (first / ".gradle").mkdir()
        (first / ".gradle" / "cache.bin").write_text("generated\n", encoding="utf-8")
        (first / "build").mkdir()
        (first / "build" / "output.bin").write_text("generated\n", encoding="utf-8")
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=first,
            text=True,
            capture_output=True,
            check=True,
        ).stdout

        self.assertTrue((first / ".git").is_dir())
        self.assertEqual("#!/bin/sh\necho simulated\n", (first / "gradlew").read_text())
        self.assertEqual("#!/bin/sh\necho real\n", (first / "gradlew-real").read_text())
        self.assertFalse((first / "subject-gradlew").exists())
        self.assertEqual(" M src/main/kotlin/example/Subject.kt\n", status)
        self.assertEqual("package example\n", (second / subject.relative_to(first)).read_text())

    def test_staged_skills_ignore_generated_bytecode(self):
        case = sample_case(self.root)
        skill = self.root / "skills" / "compose-state-and-effects"
        script = skill / "scripts" / "helper.py"
        script.parent.mkdir()
        script.write_text("print('source')\n", encoding="utf-8")
        cache = script.parent / "__pycache__" / "helper.cpython-314.pyc"
        cache.parent.mkdir()
        cache.write_bytes(b"generated")
        adjacent_bytecode = script.with_suffix(".pyc")
        adjacent_bytecode.write_bytes(b"generated")

        workspace = prepare_workspace(
            case,
            self.root,
            self.root / "runs" / "bytecode",
            enabled_skills=("compose-state-and-effects",),
        )
        staged = workspace / ".agents" / "skills" / "compose-state-and-effects"

        self.assertTrue((staged / "SKILL.md").is_file())
        self.assertTrue((staged / "scripts" / "helper.py").is_file())
        self.assertFalse((staged / "scripts" / "__pycache__").exists())
        self.assertFalse((staged / "scripts" / "helper.pyc").exists())

    def test_captures_jsonl_final_output_and_workspace_diff(self):
        case = sample_case(self.root)
        fake = self.root / "fake-codex"
        fake.write_text(
            "#!/bin/sh\n"
            "workspace=''\n"
            "previous=''\n"
            "for arg in \"$@\"; do\n"
            "  if [ \"$previous\" = '-C' ]; then workspace=$arg; fi\n"
            "  previous=$arg\n"
            "done\n"
            "printf '// changed\\n' >> \"$workspace/src/main/kotlin/example/Subject.kt\"\n"
            "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"summary\\\":\\\"done\\\",\\\"skills_used\\\":[\\\"compose-state-and-effects\\\"],\\\"evidence\\\":[\\\"diff\\\"]}\"}}'\n"
            "printf '%s\\n' '{\"type\":\"turn.completed\",\"usage\":{\"input_tokens\":10,\"output_tokens\":5}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)

        result = run_subject(
            case,
            "forced",
            self.root,
            self.root / "runs" / "subject",
            self.config,
            codex_executable=str(fake),
        )

        self.assertEqual(0, result.returncode)
        self.assertTrue(
            (
                result.workspace
                / ".agents/skills/compose-state-and-effects/SKILL.md"
            ).is_file()
        )
        self.assertEqual("done", result.final_output["summary"])
        self.assertEqual({"input_tokens": 10, "output_tokens": 5}, result.usage)
        self.assertEqual(("src/main/kotlin/example/Subject.kt",), result.changed_paths)
        self.assertIn("// changed", result.diff)

    def test_captures_untracked_files_in_workspace_diff(self):
        case = sample_case(self.root)
        fake = self.root / "fake-codex-untracked"
        fake.write_text(
            "#!/bin/sh\n"
            "workspace=''\n"
            "previous=''\n"
            "for arg in \"$@\"; do\n"
            "  if [ \"$previous\" = '-C' ]; then workspace=$arg; fi\n"
            "  previous=$arg\n"
            "done\n"
            "printf 'new evidence\\n' > \"$workspace/notes.txt\"\n"
            "printf '%s\\n' '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"{\\\"summary\\\":\\\"done\\\",\\\"skills_used\\\":[],\\\"evidence\\\":[]}\"}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)

        result = run_subject(
            case,
            "none",
            self.root,
            self.root / "runs" / "untracked",
            self.config,
            codex_executable=str(fake),
        )

        self.assertEqual(("notes.txt",), result.changed_paths)
        self.assertIn("+++ b/notes.txt", result.diff)
        self.assertIn("+new evidence", result.diff)


if __name__ == "__main__":
    unittest.main()
