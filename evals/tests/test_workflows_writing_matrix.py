import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.harness.cases import validate_corpus
from evals.harness.codex import (
    RunConfig,
    automatically_invokable_public_skills,
    build_subject_command,
    prepare_workspace,
)
from evals.harness.experiment import (
    evaluation_conditions,
    execute_experiment,
    filter_cases,
    reconcile_automatic_eligibility,
)
from evals.harness.judge import JudgeConfig
from evals.harness.suites import PUBLIC_SKILLS, WORKFLOWS_WRITING_SKILLS
from evals.validators.text_case import validate_task_graph


REPO_ROOT = Path(__file__).resolve().parents[2]


def plan_artifact(dependency: str = "none") -> str:
    return (
        "<!-- to-plan:conversation-plan:v1 id=123e4567-e89b-42d3-a456-426614174000 -->\n"
        "# Quote missing validator files\n\n"
        "**Planned against:** `main` at `0123456789abcdef0123456789abcdef01234567`\n\n"
        "## Implementation context\n\n"
        "Existing: `validator.py` defines `missing_file_error`.\n\n"
        "## Implementation slices\n\n"
        "**Task graph and parallelism:** The graph is acyclic; one slice has no parallel work.\n\n"
        "### 1. Quote missing-file paths\n\n"
        "**Task ID:** `T1`\n"
        f"**Depends on:** `{dependency}`\n\n"
        "**Files and symbols:** Edit existing `missing_file_error` in `validator.py` and its test in `tests/test_validator.py`.\n\n"
        "**Test:** Change the assertion for `settings file.json` to expect exactly `missing file: 'settings file.json'`; expect it to fail before the implementation edit.\n\n"
        "**Implementation:** Quote the supplied path in `missing_file_error` without changing its signature.\n\n"
        "**Validate:** From repository root, run `python3 -B -m unittest tests.test_validator`; expect it to pass.\n\n"
        "**Complete when:** The path, including spaces, is preserved inside quotes and the focused test passes.\n\n"
        "## Acceptance coverage\n\n"
        "| Quoted diagnostic | 1 | Focused test |\n\n"
        "## Final validation\n\n"
        "- From repository root, run `python3 -B -m unittest tests.test_validator`; expect success.\n"
    )


class WorkflowsWritingMatrixTest(unittest.TestCase):
    def test_project_execution_routes_mandatory_scheduler_and_review_contracts(self):
        entrypoint = (REPO_ROOT / "skills/run-github-project/SKILL.md").read_text(
            encoding="utf-8"
        )
        controller = (
            REPO_ROOT / "skills/run-github-project/references/execution-controller.md"
        ).read_text(encoding="utf-8")
        setup = (
            REPO_ROOT / "skills/run-github-project/references/review-and-setup.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "`next` or `drain` | [Review and setup](references/review-and-setup.md) for binding validation",
            entrypoint,
        )
        self.assertIn("validate the binding through the setup", controller)
        self.assertIn("committed digest", setup)
        self.assertIn("If any value is missing,", setup)
        self.assertIn("references/drain-scheduler.md", entrypoint)
        self.assertIn("references/review-contracts.md", entrypoint)
        normalized = " ".join(entrypoint.split())
        self.assertIn("before drain queue work", normalized)
        self.assertIn("before acceptance work", normalized)
        self.assertIn("drain-scheduler.md", controller)
        self.assertIn("review-contracts.md", controller)

    def test_integration_failure_guidance_restores_only_verified_controller_branch(self):
        entrypoint = (REPO_ROOT / "skills/implement-with-subagents/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/implementation-mode.md", entrypoint)
        guidance = (
            REPO_ROOT / "skills/implement-with-subagents/references/implementation-mode.md"
        ).read_text(encoding="utf-8")
        integration_step = " ".join(
            guidance.split("9. Integrate", maxsplit=1)[1]
            .split("10. After every repair", maxsplit=1)[0]
            .split()
        )

        conflict_path = integration_step.split(
            "If the Git operation conflicts before", maxsplit=1
        )[1].split("If the integration operation completes", maxsplit=1)[0]
        completed_path = integration_step.split(
            "If the integration operation completes", maxsplit=1
        )[1]

        post_integration_capture = (
            "record the integration branch and its exact `HEAD` SHA as that "
            "attempt's post-integration SHA"
        )
        self.assertIn(post_integration_capture, integration_step)
        self.assertLess(
            integration_step.index(post_integration_capture),
            integration_step.index("Recheck every affected validation"),
        )

        self.assertIn("git merge --abort", conflict_path)
        self.assertIn("git cherry-pick --abort", conflict_path)
        self.assertIn("recorded pre-attempt SHA", conflict_path)
        self.assertIn("worktree is clean", conflict_path)
        self.assertIn(
            "same owner the exact pre-attempt SHA and conflict evidence",
            conflict_path,
        )
        self.assertIn(
            "git worktree add -b <repair-branch> <repair-path> <recorded-pre-attempt-sha>",
            conflict_path,
        )
        self.assertIn("replay their task-scoped commit(s) there in order", conflict_path)
        self.assertIn("git cherry-pick <task-commit-sha>", conflict_path)
        self.assertIn("resolves any replay conflict in that isolated worktree", conflict_path)
        self.assertIn("Do not retry the stale task branch unchanged", conflict_path)

        self.assertIn("do not use an abort command", completed_path)
        self.assertIn("pre-attempt state was clean", completed_path)
        self.assertIn("current branch is still that integration branch", completed_path)
        self.assertIn("HEAD` is still the exact post-integration SHA", completed_path)
        self.assertIn("worktree is currently clean", completed_path)
        self.assertIn("Preserve the failed integrated tree first", completed_path)
        self.assertIn("fresh controller-owned recovery branch", completed_path)
        self.assertIn("does not already exist", completed_path)
        self.assertIn("create it without force", completed_path)
        self.assertIn(
            "git branch <recovery-branch> <recorded-post-integration-sha>",
            completed_path,
        )
        self.assertIn("recovery branch still resolves to the exact post-integration SHA", completed_path)
        self.assertLess(
            completed_path.index("`git rev-parse <recovery-branch>` resolves to the exact post-integration SHA"),
            completed_path.index("git reset --hard <recorded-pre-attempt-sha>"),
        )
        self.assertIn("create a new task-owned repair branch and isolated worktree from that recovery ref", completed_path)
        self.assertIn(
            "git worktree add -b <repair-branch> <repair-path> <recovery-branch>",
            completed_path,
        )
        self.assertIn(
            "inspect the complete repaired branch range from the recorded pre-attempt SHA",
            completed_path,
        )
        self.assertIn(
            "integrate the entire repaired task branch in dependency order",
            completed_path,
        )
        self.assertIn(
            "including both the original task change from the failed integration "
            "and its repair commits",
            completed_path,
        )
        self.assertIn("Do not cherry-pick only the repair commit", completed_path)
        self.assertIn("Rerun affected evidence on the reintegrated tree", completed_path)
        self.assertIn("git reset --hard <recorded-pre-attempt-sha>", completed_path)
        self.assertIn("do not reset task-owned branches or other refs/worktrees", completed_path)
        self.assertIn("do not remove untracked files or unrelated changes", completed_path)
        self.assertIn("exact recorded pre-attempt SHA and clean", completed_path)
        self.assertIn("stop and report the integration checkout as blocked", completed_path)

    def test_has_skill_triads_and_workflow_calibration_coverage_without_routing(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        benchmark = [case for case in report.cases if not case.calibration]
        calibration = [case for case in report.cases if case.calibration]
        self.assertEqual(21, len(benchmark))
        self.assertEqual(16, len(calibration))
        self.assertIn("grounded-writing", PUBLIC_SKILLS)
        self.assertNotIn("implement", PUBLIC_SKILLS)
        self.assertEqual(21, len(filter_cases(report.cases, case_ids=None, skills=None)))
        self.assertFalse(any(case.kind == "routing" for case in report.cases))
        self.assertEqual(
            {
                "implement-with-subagents-missing-provider-challenge",
                "run-github-project-missing-provider-challenge",
                "to-plan-authorized-draft-direct",
                "to-plan-material-assumption-proof-calibration",
                "to-plan-material-assumption-proof-novel",
                "to-plan-prior-confirmed-novel",
                "to-plan-unresolved-choice-negative",
                "to-plan-discussion-only-negative",
                "implement-with-subagents-reuse-direct",
                "implement-with-subagents-stale-evidence-negative",
                "implement-with-subagents-missing-output-negative",
                "implement-with-subagents-post-edit-negative",
                "implement-with-subagents-failed-verification-negative",
                "implement-with-subagents-explicit-rerun-novel",
                "implement-with-subagents-runtime-capability-calibration",
                "implement-with-subagents-accepted-item-noop-calibration",
            },
            {case.id for case in calibration},
        )
        for skill in WORKFLOWS_WRITING_SKILLS:
            kinds = {case.kind for case in benchmark if skill in case.target_skills}
            with self.subTest(skill=skill):
                self.assertEqual({"direct", "novel", "negative"}, kinds)

        self.assertEqual(
            {
                "to-plan-direct",
                "to-plan-novel",
                "to-plan-negative",
            },
            {
                case.id
                for case in benchmark
                if case.target_skills == ("to-plan",)
            },
        )

        subagent_cases = [
            case
            for case in benchmark
            if case.fixture == "workflow-subagents" and not case.calibration
        ]
        self.assertEqual(3, len(subagent_cases))
        self.assertTrue(
            all(
                case.target_skills == ("implement-with-subagents",)
                and case.constant_skills == ("implement",)
                for case in subagent_cases
            )
        )
        self.assertTrue(
            all(
                not case.constant_skills
                for case in report.cases
                if case.fixture == "workflow"
            )
        )

    def test_workflow_fixture_supplies_the_implement_dependency_in_every_arm(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "implement-with-subagents-direct"
        )
        config = RunConfig(model="gpt-5.6-terra", reasoning="medium")

        for arm in ("none", "forced", "automatic"):
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as temp_dir:
                workspace = Path(temp_dir) / "workspace"
                command = build_subject_command(
                    case, arm, REPO_ROOT, workspace, config, skill_paths=()
                )
                rendered = " ".join(command)
                self.assertIn(
                    str(workspace / ".agents/skills/implement/SKILL.md"), rendered
                )
                self.assertIn("enabled = true", rendered)
                self.assertIn(
                    "Evaluator-owned fixture dependencies to omit: implement",
                    rendered,
                )
                self.assertIn(
                    "Enabled public skills are not fixture dependencies", rendered
                )

                prepare_workspace(
                    case,
                    REPO_ROOT,
                    workspace,
                    enabled_skills=automatically_invokable_public_skills(REPO_ROOT),
                )
                self.assertTrue(
                    (workspace / ".agents/skills/implement/SKILL.md").is_file()
                )
                if arm == "automatic":
                    self.assertNotIn(
                        str(
                            workspace
                            / ".agents"
                            / "skills"
                            / "implement-with-subagents"
                            / "SKILL.md"
                        ),
                        rendered,
                    )
                    self.assertFalse(
                        (
                            workspace
                            / ".agents"
                            / "skills"
                            / "implement-with-subagents"
                        ).exists()
                    )

    def test_missing_provider_challenge_omits_the_implement_dependency(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "implement-with-subagents-missing-provider-challenge"
        )

        self.assertEqual((), case.constant_skills)
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            prepare_workspace(case, REPO_ROOT, workspace, enabled_skills=())

            self.assertFalse(
                (workspace / ".agents/skills/implement/SKILL.md").exists()
            )

    def test_advanced_workflow_skills_require_explicit_invocation(self):
        explicit_only = (
            "implement-with-subagents",
            "run-github-project",
            "shepherd",
            "to-plan",
        )
        for skill in explicit_only:
            config = REPO_ROOT / "skills" / skill / "agents" / "openai.yaml"
            entrypoint = REPO_ROOT / "skills" / skill / "SKILL.md"
            with self.subTest(skill=skill):
                self.assertIn(
                    "allow_implicit_invocation: false",
                    config.read_text(encoding="utf-8"),
                )
                self.assertIn(
                    "disable-model-invocation: true",
                    entrypoint.read_text(encoding="utf-8"),
                )

        self.assertEqual(
            set(PUBLIC_SKILLS) - set(explicit_only),
            set(automatically_invokable_public_skills(REPO_ROOT)),
        )
        schema = json.loads((REPO_ROOT / "skills.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            "boolean",
            schema["properties"]["disable-model-invocation"]["type"],
        )
        self.assertNotIn("paths", schema["properties"])

    def test_automatic_conditions_exclude_explicit_only_workflow_skills(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        conditions = evaluation_conditions(REPO_ROOT, report.cases, ("automatic",))

        self.assertEqual(
            {
                "grounded-writing-direct",
                "grounded-writing-novel",
                "grounded-writing-negative",
                "android-benchmark-comparison-direct",
                "android-benchmark-comparison-novel",
                "android-benchmark-comparison-negative",
                "release-kotlin-library-direct",
                "release-kotlin-library-novel",
                "release-kotlin-library-negative",
            },
            {case.id for case, _ in conditions},
        )

    def test_execution_skips_an_explicit_only_automatic_condition(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case for case in report.cases if case.id == "run-github-project-direct"
        )

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "evals.harness.experiment.preflight"
        ) as preflight:
            paths = execute_experiment(
                REPO_ROOT,
                [case],
                arms=["automatic"],
                repetitions=1,
                run_config=RunConfig("gpt-5.6-terra", "medium"),
                judge_config=JudgeConfig("gpt-5.6-sol", "high"),
                output_dir=Path(temp_dir),
            )

            self.assertEqual(
                [], json.loads(paths["results"].read_text(encoding="utf-8"))
            )

        preflight.assert_not_called()

    def test_legacy_automatic_records_are_reconciled_from_the_current_corpus(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        records = [
            {"case_id": "run-github-project-direct", "arm": "automatic"},
            {"case_id": "run-github-project-direct", "arm": "forced"},
            {"case_id": "grounded-writing-direct", "arm": "automatic"},
            {"case_id": "removed-case", "arm": "automatic"},
        ]

        reconcile_automatic_eligibility(REPO_ROOT, report.cases, records)

        self.assertFalse(records[0]["automatic_eligible"])
        self.assertFalse(records[1]["automatic_eligible"])
        self.assertTrue(records[2]["automatic_eligible"])
        self.assertEqual(["grounded-writing"], records[2]["expected_skills"])
        self.assertFalse(records[3]["automatic_eligible"])

    def test_no_skill_automatic_control_runs_without_routing_to_its_target(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "android-benchmark-comparison-negative"
        )

        self.assertTrue(case.automatic_no_skill_control)
        self.assertIn(
            (case, "automatic"), evaluation_conditions(REPO_ROOT, (case,), ("automatic",))
        )
        records = [{"case_id": case.id, "arm": "automatic"}]
        reconcile_automatic_eligibility(REPO_ROOT, report.cases, records)

        self.assertTrue(records[0]["automatic_eligible"])
        self.assertEqual([], records[0]["expected_skills"])
        self.assertEqual([], records[0]["allowed_skills"])

    def test_behavioral_expectations_do_not_assert_fixture_prose(self):
        expectations = json.loads(
            (
                REPO_ROOT
                / "evals/cases/implement-with-subagents-novel/expectations.json"
            ).read_text(encoding="utf-8")
        )

        self.assertNotIn(
            "minimal `implement` dependency", expectations.get("must_contain", [])
        )

    def test_workflow_prompts_do_not_disclose_the_target_skill(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        for case in report.cases:
            with self.subTest(case=case.id):
                prompt = case.prompt.lower()
                self.assertNotIn("$", prompt)
                for skill in case.expected_skills:
                    self.assertNotIn(skill, prompt)

    def test_review_prompts_allow_skill_instruction_reads(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")

        for case in report.cases:
            with self.subTest(case=case.id):
                self.assertNotIn("do not run agents, commands", case.prompt.lower())

    def test_grounded_writing_validator_accepts_public_quality_guidance(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "draft.md").write_text(
                "`Full` keeps the complete effect when visual fidelity matters. "
                "Choose `Adaptive` during sustained interaction when steadier "
                "performance matters more than the visible detail it reduces. "
                "The settings preserve the same public API; Adaptive remains "
                "experimental on Android backdrops.\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                ["python3", str(validator), "grounded-writing-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_plan_artifact_validator_requires_one_marked_local_draft(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            draft = workspace / ".scratch/to-plan/repair-validator-output.md"
            draft.parent.mkdir(parents=True)
            draft.write_text(plan_artifact(), encoding="utf-8")

            completed = subprocess.run(
                ["python3", str(validator), "to-plan-authorized-draft-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_task_graph_validator_accepts_required_dependency_edge(self):
        subject = (
            "## Implementation slices\n\n"
            "### 1. Prepare a compatible model\n"
            "**Task ID:** `T1`\n"
            "**Depends on:** `none`\n\n"
            "### 2. Wire the model into the endpoint\n"
            "**Task ID:** `T2`\n"
            "**Depends on:** `T1`\n"
        )

        failures = validate_task_graph(
            subject,
            {"required_edges": [["T2", "T1"]], "require_acyclic": True},
        )

        self.assertEqual([], failures)

    def test_material_assumption_proof_case_requires_dependent_implementation(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "to-plan-material-assumption-proof-calibration"
        )
        self.assertEqual("workflow-report-publication", case.fixture)
        self.assertTrue(case.calibration)
        self.assertIn("early-proof", case.prompt)
        self.assertIn("T3 must depend directly on T1, as well as T2", case.prompt)
        fixture = REPO_ROOT / "evals/fixtures/workflow-report-publication"
        publisher = (fixture / "report_publisher.py").read_text(encoding="utf-8")
        config = json.loads((fixture / "report_config.json").read_text(encoding="utf-8"))
        self.assertIn("def publish_report", publisher)
        self.assertIn("published.write_bytes(contents)", publisher)
        self.assertNotIn("os.replace", publisher)
        self.assertLess(
            publisher.index("published.write_bytes(contents)"),
            publisher.index("mark_published("),
        )
        self.assertEqual(
            {
                "staging_mount": "/runtime/reports/staging",
                "published_mount": "/runtime/reports/published",
            },
            config,
        )
        expectations = json.loads(
            (case.directory / "expectations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [["T2", "T1"], ["T3", "T1"], ["T3", "T2"]],
            expectations["task_graph"]["required_edges"],
        )
        self.assertTrue(expectations["task_graph"]["require_acyclic"])

    def test_novel_material_assumption_proof_case_is_not_scripted(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case
            for case in report.cases
            if case.id == "to-plan-material-assumption-proof-novel"
        )
        self.assertEqual("novel", case.kind)
        self.assertTrue(case.calibration)
        self.assertEqual("workflow-report-publication", case.fixture)
        self.assertNotIn("os.replace", case.prompt)
        self.assertNotIn("T3", case.prompt)
        rubric_ids = {item["id"] for item in case.rubric}
        self.assertTrue(
            {
                "repository-evidence",
                "bounded-proof",
                "failure-gate",
                "task-dependency",
                "proposed-publication",
            }
            <= rubric_ids
        )
        expectations = json.loads(
            (case.directory / "expectations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [["T2", "T1"], ["T3", "T1"], ["T3", "T2"]],
            expectations["task_graph"]["required_edges"],
        )
        self.assertTrue(expectations["task_graph"]["require_acyclic"])

    def test_evidence_backed_plan_counterexample_rejects_speculative_proof(self):
        report = validate_corpus(REPO_ROOT, suite="workflows-writing")
        case = next(
            case for case in report.cases if case.id == "to-plan-authorized-draft-direct"
        )
        self.assertTrue(case.calibration)
        rubric = {item["id"]: item["text"] for item in case.rubric}
        self.assertIn("one implementation slice", rubric["proportionality"])
        self.assertIn("without a speculative proof task", rubric["proportionality"])

    def test_task_graph_validator_ignores_fenced_markdown_headings_and_fields(self):
        subject = (
            "```markdown\n"
            "## Implementation slices\n"
            "### 1. Example only\n"
            "**Task ID:** `FAKE`\n"
            "**Depends on:** `MISSING`\n"
            "```\n"
            "## Implementation slices\n\n"
            "### 1. Actual task\n"
            "**Task ID:** `T1`\n"
            "**Depends on:** `none`\n\n"
            "```md\n"
            "### 2. Fenced example, not a slice\n"
            "**Task ID:** `FAKE2`\n"
            "**Depends on:** `T1`\n"
            "```\n"
            "## Acceptance coverage\n"
        )

        failures = validate_task_graph(
            subject, {"required_edges": [], "require_acyclic": True}
        )

        self.assertEqual([], failures)

    def test_task_graph_validator_rejects_unnumbered_slice_before_valid_slice(self):
        subject = (
            "## Implementation slices\n\n"
            "### Unnumbered but declared slice\n"
            "**Task ID:** `T0`\n"
            "**Depends on:** `none`\n\n"
            "### 1. Numbered slice\n"
            "**Task ID:** `T1`\n"
            "**Depends on:** `none`\n"
        )

        failures = validate_task_graph(
            subject, {"required_edges": [], "require_acyclic": True}
        )

        self.assertTrue(
            any("malformed implementation slice heading" in failure for failure in failures),
            failures,
        )

    def test_task_graph_validator_rejects_slice_at_unexpected_heading_level(self):
        subject = (
            "## Implementation slices\n\n"
            "### 1. Numbered slice\n"
            "**Task ID:** `T1`\n"
            "**Depends on:** `none`\n\n"
            "#### 2. Hidden deeper slice\n"
            "**Task ID:** `T2`\n"
            "**Depends on:** `T1`\n"
        )

        failures = validate_task_graph(
            subject, {"required_edges": [], "require_acyclic": True}
        )

        self.assertTrue(
            any("unexpected heading level" in failure for failure in failures), failures
        )

    def test_task_graph_validator_rejects_slice_that_ends_its_section(self):
        subject = (
            "## Implementation slices\n\n"
            "### 1. Numbered slice\n"
            "**Task ID:** `T1`\n"
            "**Depends on:** `none`\n\n"
            "## Unnumbered slice\n"
            "**Task ID:** `T2`\n"
            "**Depends on:** `T1`\n"
        )

        failures = validate_task_graph(
            subject, {"required_edges": [], "require_acyclic": True}
        )

        self.assertTrue(
            any("unexpected section boundary" in failure for failure in failures), failures
        )

    def test_task_graph_validator_reserves_none_as_dependency_sentinel(self):
        subject = (
            "## Implementation slices\n\n"
            "### 1. A task named none\n"
            "**Task ID:** `NONE`\n"
            "**Depends on:** `none`\n"
        )

        failures = validate_task_graph(
            subject, {"required_edges": [], "require_acyclic": True}
        )

        self.assertTrue(any("task ID 'none' is reserved" in failure for failure in failures))

    def test_plan_artifact_validator_rejects_cyclic_task_dependencies(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            draft = workspace / ".scratch/to-plan/cyclic-plan.md"
            draft.parent.mkdir(parents=True)
            draft.write_text(plan_artifact(dependency="T1"), encoding="utf-8")

            completed = subprocess.run(
                ["python3", str(validator), "to-plan-authorized-draft-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("task dependency graph contains a cycle", completed.stderr)

    def test_plan_artifact_validator_rejects_multiple_local_drafts(self):
        validator = REPO_ROOT / "evals/validators/text_case.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            drafts = workspace / ".scratch/to-plan"
            drafts.mkdir(parents=True)
            for name in ("first.md", "second.md"):
                (drafts / name).write_text("placeholder\n", encoding="utf-8")

            completed = subprocess.run(
                ["python3", str(validator), "to-plan-authorized-draft-direct"],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("expected 1 files, found 2", completed.stderr)


if __name__ == "__main__":
    unittest.main()
