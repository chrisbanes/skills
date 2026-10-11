import json
import os
import shutil
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path

from evals.harness.claude import ClaudeRuntime, discover_builtin_skills
from evals.harness.grade import grade_subject
from evals.harness.runner import (
    RunConfig,
    SubjectResult,
    captured_skill_file_evidence,
    prepare_workspace,
    reported_skill_names,
    run_subject,
)
from evals.harness.score import forced_integrity_status, is_behavioral_evidence
from evals.tests import test_codex_runner
from evals.tests.test_codex_runner import sample_case
from evals.tests.test_grade import make_case


FIXTURE = Path(__file__).parent / "data" / "claude_stream_subject.jsonl"
SANDBOX = {
    "enabled": True,
    "failIfUnavailable": True,
    "allowUnsandboxedCommands": False,
    "autoAllowBashIfSandboxed": True,
    "network": {"allowedDomains": []},
}


def option(command, flag):
    return command[command.index(flag) + 1]


class ClaudeRunnerTest(unittest.TestCase):
    setUp = test_codex_runner.CodexRunnerTest.setUp
    tearDown = test_codex_runner.CodexRunnerTest.tearDown

    def write_subject_schema(self):
        (self.root / "evals" / "schemas" / "subject-output.schema.json").write_text(
            json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema",
                        "type": "object"}),
            encoding="utf-8",
        )

    def test_review_none_command_isolates_claude(self):
        self.write_subject_schema()
        case = sample_case(self.root, task_mode="review")
        workspace = self.root / "workspace"
        runtime = ClaudeRuntime(builtin_skills=("simplify", "debug"))

        command = runtime.build_subject_command(
            case, "none", self.root, workspace, self.config,
            executable="claude", skill_paths=None,
        )

        self.assertEqual(["claude", "-p"], command[:2])
        for flag in (
            "--verbose", "--no-session-persistence", "--strict-mcp-config",
            "--disable-slash-commands",
        ):
            self.assertIn(flag, command)
        self.assertEqual("stream-json", option(command, "--output-format"))
        self.assertEqual("project", option(command, "--setting-sources"))
        self.assertEqual("dontAsk", option(command, "--permission-mode"))
        self.assertEqual("gpt-5.6-terra", option(command, "--model"))
        self.assertEqual("medium", option(command, "--effort"))
        self.assertEqual("Read,Grep,Glob,Bash,Skill", option(command, "--tools"))
        self.assertEqual("Read,Grep,Glob,Bash,Skill", option(command, "--allowedTools"))
        self.assertEqual("WebFetch,WebSearch", option(command, "--disallowedTools"))
        self.assertEqual({"type": "object"}, json.loads(option(command, "--json-schema")))
        self.assertEqual(
            {
                "sandbox": SANDBOX,
                "autoMemoryEnabled": False,
                "skillOverrides": {"simplify": "off", "debug": "off"},
            },
            json.loads(option(command, "--settings")),
        )
        self.assertNotIn("--bare", command)

    def test_edit_forced_command_uses_skill_tool_instruction(self):
        self.write_subject_schema()
        case = sample_case(self.root)
        runtime = ClaudeRuntime(builtin_skills=("simplify", "compose-state-and-effects"))

        command = runtime.build_subject_command(
            case, "forced", self.root, self.root / "workspace", self.config,
            executable="claude", skill_paths=None,
        )

        self.assertEqual(
            "Read,Grep,Glob,Bash,Skill,Edit,Write", option(command, "--tools")
        )
        self.assertNotIn("--disable-slash-commands", command)
        # A staged target is never switched off, even when a built-in shares its name.
        self.assertEqual(
            {"simplify": "off"}, json.loads(option(command, "--settings"))["skillOverrides"]
        )
        prompt = command[2]
        self.assertIn("Skill tool", prompt)
        self.assertIn("`compose-state-and-effects`", prompt)
        self.assertNotIn("$compose-state-and-effects", prompt)
        self.assertNotIn("`cat`", prompt)
        self.assertIn("In the final `skills_used`, include each of these exact public", prompt)

    def test_fixture_skill_dependencies_are_never_switched_off(self):
        self.write_subject_schema()
        case = replace(sample_case(self.root), constant_skills=("implement",))

        command = ClaudeRuntime(builtin_skills=("implement", "simplify")).build_subject_command(
            case, "none", self.root, self.root / "workspace", self.config,
            executable="claude", skill_paths=None,
        )

        self.assertEqual(
            {"simplify": "off"}, json.loads(option(command, "--settings"))["skillOverrides"]
        )

    def test_validates_claude_effort_levels(self):
        for effort in ("low", "medium", "high", "xhigh", "max"):
            ClaudeRuntime().validate_reasoning(effort)
        with self.assertRaises(ValueError):
            ClaudeRuntime().validate_reasoning("minimal")

    def test_stages_fixture_skill_dependencies_into_claude_only(self):
        dependency = self.root / "evals/fixtures/compose-jvm/.agents/skills/implement"
        (dependency / "references").mkdir(parents=True)
        (dependency / "SKILL.md").write_text("---\nname: implement\n---\n", encoding="utf-8")
        (dependency / "references" / "notes.md").write_text("notes\n", encoding="utf-8")
        case = replace(sample_case(self.root), constant_skills=("implement",))

        claude = prepare_workspace(
            case, self.root, self.root / "claude-workspace",
            enabled_skills=case.target_skills, skill_dir=ClaudeRuntime.skill_dir,
        )
        codex = prepare_workspace(
            case, self.root, self.root / "codex-workspace",
            enabled_skills=case.target_skills,
        )

        self.assertEqual(
            "notes\n", (claude / ".claude/skills/implement/references/notes.md").read_text()
        )
        self.assertTrue((claude / ".agents/skills/implement/SKILL.md").is_file())
        self.assertFalse((codex / ".claude").exists())
        self.assertTrue((codex / ".agents/skills/implement/SKILL.md").is_file())

    def test_stages_skills_into_claude_skill_directory(self):
        case = sample_case(self.root)
        workspace = prepare_workspace(
            case, self.root, self.root / "workspace",
            enabled_skills=case.target_skills, skill_dir=ClaudeRuntime.skill_dir,
        )

        self.assertTrue(
            (workspace / ".claude/skills/compose-state-and-effects/SKILL.md").is_file()
        )
        self.assertFalse((workspace / ".agents").exists())


def fixture_lines():
    return [json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines()]


def fixture_stdout(lines=None):
    return "".join(json.dumps(line) + "\n" for line in (lines or fixture_lines()))


class ClaudeParseTest(unittest.TestCase):
    def setUp(self):
        self.runtime = ClaudeRuntime()
        self.events, self.output, self.usage = self.runtime.parse(fixture_stdout())

    def test_parses_structured_output_and_normalized_usage(self):
        result = fixture_lines()[-1]
        self.assertEqual(result["structured_output"], self.output)
        self.assertEqual(10 + 16382 + 63575, self.usage["input_tokens"])
        self.assertEqual(1090, self.usage["output_tokens"])
        self.assertEqual(16382, self.usage["cache_creation_input_tokens"])
        self.assertEqual(63575, self.usage["cache_read_input_tokens"])

    def test_tolerates_trailing_events_after_result(self):
        trailing = [*fixture_lines(), {"type": "system", "subtype": "task_summary"}]
        _, output, usage = self.runtime.parse(fixture_stdout(trailing) + "not json\n")
        self.assertEqual(self.output, output)
        self.assertEqual(self.usage, usage)

    def test_commands_pair_bash_calls_with_exit_codes(self):
        commands = self.runtime.commands(self.events)
        self.assertEqual(
            [("cat note.txt", 0), ("ls missing", 1), ("curl -sS https://example.com", 56)],
            [(c.command, c.exit_code) for c in commands],
        )
        self.assertEqual("hello probe", commands[0].output)
        self.assertTrue(commands[1].output.startswith("Exit code 1\nls: missing"))
        self.assertEqual({"completed"}, {c.status for c in commands})
        self.assertEqual(["toolu_04", "toolu_06", "toolu_08"], [c.id for c in commands])

    def test_failed_command_without_exit_line_is_never_exit_zero(self):
        lines = fixture_lines()
        lines[7]["message"]["content"][0]["content"] = "Command failed"
        commands = self.runtime.commands(self.runtime.parse(fixture_stdout(lines))[0])
        self.assertEqual(1, commands[1].exit_code)

    def test_unanswered_and_denied_bash_calls_are_attempts(self):
        lines = fixture_lines()[:-1]
        del lines[9]  # The curl call never returns.
        lines.append({**fixture_lines()[-1], "permission_denials": [{
            "tool_name": "Bash", "tool_use_id": "toolu_99",
            "tool_input": {"command": "rm -rf /"},
        }]})
        commands = self.runtime.commands(self.runtime.parse(fixture_stdout(lines))[0])
        self.assertEqual(
            [("curl -sS https://example.com", None, "in_progress"),
             ("rm -rf /", None, "denied")],
            [(c.command, c.exit_code, c.status) for c in commands[2:]],
        )

    def test_counts_tools_and_turns(self):
        # Skill plus three Bash calls; StructuredOutput is excluded.
        self.assertEqual(4, self.runtime.tool_call_count(self.events))
        self.assertEqual(1, self.runtime.turn_count(self.events))

    def test_observed_skills_use_public_canonical_names(self):
        self.assertEqual([], self.runtime.observed_skills(self.events))
        lines = fixture_lines()
        lines[1]["message"]["content"][0]["input"]["skill"] = (
            "chrisbanes-skills:kotlin-api-design"
        )
        router = json.loads(json.dumps(lines[1]))
        router["message"]["content"][0]["input"]["skill"] = "using-chrisbanes-skills"
        lines.insert(2, router)
        events = self.runtime.parse(fixture_stdout(lines))[0]
        self.assertEqual(["kotlin-api-design"], self.runtime.observed_skills(events))

    def test_skill_texts_follow_successful_skill_results(self):
        self.assertEqual(
            [("toolu_02", "Base directory for this skill: /workspace/.claude/skills/"
              "probe-skill\n\n# Probe skill\n\nSay \"probe-skill loaded\" in your summary.\n")],
            self.runtime.skill_texts(self.events),
        )
        lines = fixture_lines()
        lines[2]["message"]["content"][0]["is_error"] = True
        self.assertEqual(
            [], self.runtime.skill_texts(self.runtime.parse(fixture_stdout(lines))[0])
        )


class ClaudeSafetyTest(unittest.TestCase):
    def grade(self, lines):
        events, output, usage = ClaudeRuntime().parse(fixture_stdout(lines))
        with tempfile.TemporaryDirectory() as directory:
            case = make_case(Path(directory), task_mode="review")
            result = SubjectResult(
                case_id="case", arm="automatic", command=("claude",),
                workspace=Path(directory), returncode=0, events=events,
                final_output=output, usage=usage, changed_paths=(), diff="",
                stdout="", stderr="", elapsed_seconds=0.1, runtime="claude",
            )
            return grade_subject(case, result).violations

    def test_flags_network_external_tool_destructive_and_escalation_attempts(self):
        self.assertIn("network command attempted", self.grade(fixture_lines()))

        lines = fixture_lines()
        web = json.loads(json.dumps(lines[8]))
        web["message"]["content"][0].update(
            id="toolu_web", name="WebFetch", input={"url": "https://example.com"}
        )
        mcp = json.loads(json.dumps(web))
        mcp["message"]["content"][0].update(id="toolu_mcp", name="mcp__github__search")
        lines[-1]["permission_denials"] = [
            {"tool_name": "Bash", "tool_use_id": "toolu_99",
             "tool_input": {"command": "rm -rf /"}},
            {"tool_name": "Agent", "tool_use_id": "toolu_98", "tool_input": {}},
        ]
        violations = self.grade([*lines[:10], web, mcp, *lines[10:]])

        self.assertIn("external tool attempted", violations)
        self.assertIn("destructive command attempted", violations)
        self.assertIn("permission escalation attempted", violations)

    def test_external_and_escalation_sequences(self):
        runtime = ClaudeRuntime()
        lines = fixture_lines()
        lines[-1]["permission_denials"] = [
            {"tool_name": "WebSearch", "tool_use_id": "a", "tool_input": {}},
            {"tool_name": "Bash", "tool_use_id": "b", "tool_input": {"command": "ls"}},
            {"tool_name": "NotebookEdit", "tool_use_id": "c", "tool_input": {}},
        ]
        events = runtime.parse(fixture_stdout(lines))[0]
        # The init tool list defines the arm's tools; Bash denials are commands.
        self.assertEqual((13,), runtime.external_tool_attempts(events))
        self.assertEqual((13,), runtime.permission_escalations(events))
        lines[-1]["permission_denials"] = [
            {"tool_name": "Edit", "tool_use_id": "d", "tool_input": {}},
        ]
        events = runtime.parse(fixture_stdout(lines))[0]
        self.assertEqual((), runtime.permission_escalations(events))

    def test_gradle_without_offline_is_flagged(self):
        lines = fixture_lines()
        lines[4]["message"]["content"][0]["input"]["command"] = "./gradlew test"
        self.assertIn("Gradle command omitted --offline", self.grade(lines))


def init_event(**fields):
    return {"type": "system", "subtype": "init", "skills": [], "mcp_servers": [], **fields}


def write_fake_claude(path: Path, *lines, then="exec sleep 30"):
    """A stand-in `claude` that records pid, env and args, prints lines, then `then`."""
    echoes = "".join(f"printf '%s\\n' '{json.dumps(line)}'\n" for line in lines)
    path.write_text(
        "#!/bin/sh\n"
        f"echo $$ > '{path}.pid'\n"
        f"printf '%s' \"$CLAUDE_CODE_DISABLE_CLAUDE_MDS\" > '{path}.env'\n"
        f"printf '%s\\n' \"$@\" > '{path}.args'\n"
        "echo '{\"type\": \"system\", \"subtype\": \"thinking_tokens\"}'\n"
        f"{echoes}{then}\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


class ClaudeInitCheckTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.workspace = self.root / "workspace"
        skill = self.workspace / ".claude" / "skills" / "compose-state-and-effects"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: x\n---\nbody\n", encoding="utf-8")
        self.fake = self.root / "claude"

    def tearDown(self):
        self.temp_dir.cleanup()

    def execute(self, *lines, then="exec sleep 30"):
        write_fake_claude(self.fake, *lines, then=then)
        started = time.monotonic()
        result = ClaudeRuntime().execute_subject([str(self.fake), "-p"], self.workspace, 60)
        return result, time.monotonic() - started

    def assert_child_gone(self):
        pid = int((self.root / "claude.pid").read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_init_mismatch_stops_the_child_before_model_output(self):
        mismatches = {
            "unexpected_skills": init_event(
                skills=["compose-state-and-effects", "simplify"]
            ),
            "missing_skills": init_event(),
            "mcp_servers": init_event(
                skills=["compose-state-and-effects"],
                mcp_servers=[{"name": "github", "status": "connected"}],
            ),
            "auto_memory": init_event(
                skills=["compose-state-and-effects"],
                memory_paths={"auto": "/home/memory/"},
            ),
        }
        for problem, init in mismatches.items():
            with self.subTest(problem):
                (returncode, stdout, stderr, isolation), elapsed = self.execute(init)
                self.assertLess(elapsed, 15)
                self.assertFalse(isolation["valid"])
                self.assertIn(problem, isolation["problems"])
                self.assertIn("claude init isolation check failed", stderr)
                self.assertNotEqual(0, returncode)
                self.assert_child_gone()

    def test_missing_init_before_model_output_is_invalid(self):
        assistant = fixture_lines()[1]
        (_, _, stderr, isolation), elapsed = self.execute(assistant)
        self.assertLess(elapsed, 15)
        self.assertFalse(isolation["valid"])
        self.assert_child_gone()

    def test_matching_init_passes_through_with_claude_mds_disabled(self):
        lines = fixture_lines()[1:]
        (returncode, stdout, stderr, isolation), _ = self.execute(
            init_event(skills=["compose-state-and-effects"]), *lines, then="exit 0"
        )
        self.assertEqual(0, returncode)
        self.assertTrue(isolation["valid"])
        self.assertEqual("1", (self.root / "claude.env").read_text())
        _, output, _ = ClaudeRuntime().parse(stdout)
        self.assertEqual(fixture_lines()[-1]["structured_output"], output)


TARGET = "compose-state-and-effects"
BODY = "# State and effects\n\nHoist state.\n"


class ClaudeForcedIntegrityTest(unittest.TestCase):
    setUp = test_codex_runner.CodexRunnerTest.setUp
    tearDown = test_codex_runner.CodexRunnerTest.tearDown

    def forced_lines(self):
        lines = fixture_lines()[1:]
        lines[0]["message"]["content"][0]["input"]["skill"] = f"chrisbanes-skills:{TARGET}"
        lines[2]["message"]["content"][0]["text"] = (
            f"Base directory for this skill: /workspace/.claude/skills/{TARGET}\n\n{BODY}"
        )
        lines[-1]["structured_output"]["skills_used"] = [TARGET]
        return lines

    def run_forced(
        self, *lines, arm="forced", init_skills=(TARGET,), runtime="claude", case=None
    ):
        (self.root / "skills" / TARGET / "SKILL.md").write_text(
            f"---\nname: {TARGET}\ndescription: Use when testing.\n---\n\n{BODY}",
            encoding="utf-8",
        )
        fake = write_fake_claude(
            self.root / "claude", init_event(skills=list(init_skills)), *lines,
            then="exit 0",
        )
        case = case or sample_case(self.root)
        result = run_subject(
            case, arm, self.root, self.root / "workspace", self.config,
            runtime=runtime, executable=str(fake),
        )
        return {
            "id": "sample:forced:1",
            "arm": arm,
            "runtime": "claude",
            "target_skills": [TARGET],
            "reported_skills": reported_skill_names(result.final_output),
            "forced_target_preflight": result.forced_target_preflight,
            "subject": {
                "events": list(result.events),
                "captured_skill_files": captured_skill_file_evidence(
                    result.workspace, result.events, runtime="claude"
                ),
            },
        }

    def test_skill_first_with_complete_capture_is_valid(self):
        record = self.run_forced(*self.forced_lines())
        target = record["forced_target_preflight"]["targets"][0]
        self.assertEqual(f".claude/skills/{TARGET}/SKILL.md", target["staged_relative_path"])
        self.assertEqual("valid", forced_integrity_status(record))

    def test_runtime_instance_is_used_as_given(self):
        record = self.run_forced(
            *self.forced_lines(), runtime=ClaudeRuntime(builtin_skills=(TARGET,))
        )
        self.assertEqual(
            "not_uniquely_enabled",
            record["forced_target_preflight"]["targets"][0]["status"],
        )
        self.assertEqual("missing_target", forced_integrity_status(record))

    def test_bash_before_skill_is_invocation_failure(self):
        lines = self.forced_lines()
        record = self.run_forced(*lines[3:5], *lines[:3], *lines[5:])
        self.assertEqual("invocation_failure", forced_integrity_status(record))

    def test_missing_capture_is_invocation_failure(self):
        lines = self.forced_lines()
        del lines[2]
        record = self.run_forced(*lines)
        self.assertEqual("invocation_failure", forced_integrity_status(record))

    def test_failed_skill_call_is_invocation_failure(self):
        lines = self.forced_lines()
        lines[1]["message"]["content"][0]["is_error"] = True
        record = self.run_forced(*lines)
        self.assertEqual("invocation_failure", forced_integrity_status(record))

    def test_isolation_failure_is_missing_target_and_excluded_in_every_arm(self):
        for arm in ("forced", "none", "automatic"):
            with self.subTest(arm):
                shutil.rmtree(self.root / "workspace", ignore_errors=True)
                record = self.run_forced(
                    *self.forced_lines(), arm=arm, init_skills=("simplify",)
                )
                record["automatic_eligible"] = True
                self.assertFalse(record["forced_target_preflight"]["valid"])
                self.assertFalse(is_behavioral_evidence(record, arm))
                if arm == "forced":
                    self.assertEqual("missing_target", forced_integrity_status(record))

    def test_fixture_skill_dependencies_are_staged_for_claude_and_expected_in_init(self):
        dependency = self.root / "evals/fixtures/compose-jvm/.agents/skills/implement"
        dependency.mkdir(parents=True)
        (dependency / "SKILL.md").write_text("---\nname: implement\n---\n", encoding="utf-8")
        case = replace(sample_case(self.root), constant_skills=("implement",))

        record = self.run_forced(
            *self.forced_lines(), init_skills=(TARGET, "implement"), case=case
        )

        self.assertTrue((self.root / "workspace/.claude/skills/implement/SKILL.md").is_file())
        self.assertTrue(record["forced_target_preflight"]["valid"])
        self.assertEqual("valid", forced_integrity_status(record))

        shutil.rmtree(self.root / "workspace")
        record = self.run_forced(*self.forced_lines(), init_skills=(TARGET,), case=case)
        self.assertEqual(
            {"missing_skills": ["implement"]},
            record["forced_target_preflight"]["isolation"]["problems"],
        )

    def test_refuses_workspace_below_a_claude_md(self):
        for name in ("CLAUDE.md", "CLAUDE.local.md"):
            with self.subTest(name):
                marker = self.root / "outer" / name
                marker.parent.mkdir(exist_ok=True)
                marker.write_text("canary\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "--output-dir"):
                    run_subject(
                        sample_case(self.root), "none", self.root,
                        self.root / "outer" / "runs" / "workspace", self.config,
                        runtime="claude", executable="claude",
                    )
                self.assertFalse((self.root / "outer" / "runs").exists())
                marker.unlink()


class BuiltinDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config = RunConfig(model="claude-haiku-5-5", reasoning="high")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_reads_init_skills_then_stops_the_child(self):
        fake = write_fake_claude(
            self.root / "claude",
            init_event(skills=["simplify", "debug"], memory_paths={"auto": "/m/"}),
        )
        started = time.monotonic()
        skills = discover_builtin_skills(str(fake), self.config)

        self.assertLess(time.monotonic() - started, 15)
        self.assertEqual(("debug", "simplify"), skills)
        pid = int((self.root / "claude.pid").read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        args = (self.root / "claude.args").read_text().splitlines()
        self.assertEqual("claude-haiku-5-5", args[args.index("--model") + 1])
        self.assertNotIn("--disable-slash-commands", args)

    def test_fails_without_an_init_event(self):
        fake = write_fake_claude(self.root / "claude", then="exit 1")
        with self.assertRaisesRegex(RuntimeError, "init"):
            discover_builtin_skills(str(fake), self.config)


if __name__ == "__main__":
    unittest.main()
