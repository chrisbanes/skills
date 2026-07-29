#!/usr/bin/env python3
"""Tests for the GitHub Project ticket ranker."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("rank_tickets.py")
DEFAULT_PRIORITY_ARGUMENTS = (
    "--priority",
    "Critical",
    "--priority",
    "High",
    "--priority",
    "Medium",
    "--priority",
    "Low",
)
DEFAULT_PROJECT_ARGUMENTS = (
    "--repository",
    "acme/repo",
    "--base-branch",
    "main",
    "--execution-approver",
    "maintainer",
)
DEFAULT_STATUS_ARGUMENTS = (
    "--ready-status",
    "Ready",
    "--in-progress-status",
    "In progress",
)


def run_ranker(items: list[dict], *arguments: str) -> tuple[int, dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--current-user",
            "chris",
            *DEFAULT_PROJECT_ARGUMENTS,
            *DEFAULT_PRIORITY_ARGUMENTS,
            *DEFAULT_STATUS_ARGUMENTS,
            *arguments,
        ],
        input=json.dumps(items),
        capture_output=True,
        check=False,
        text=True,
    )
    return result.returncode, json.loads(result.stdout)


def ticket(number: int, **overrides: object) -> dict:
    result = {
        "number": number,
        "title": f"Issue {number}",
        "url": f"https://github.com/acme/repo/issues/{number}",
        "state": "OPEN",
        "projectItemId": f"PVTI_{number}",
        "projectStatus": "Ready",
        "projectPriority": "High",
        "projectPosition": number,
        "labels": ["ready-for-agent"],
        "assignees": [],
        "blockedBy": [],
        "openDescendants": [],
        "openPullRequests": [],
        "planningTransition": {
            "id": f"PVTE_{number}_planning",
            "actor": "maintainer",
            "createdAt": "2026-07-28T08:00:00Z",
            "status": "Planning",
            "wasAutomated": False,
        },
        "readyTransition": {
            "id": f"PVTE_{number}_ready",
            "actor": "chris",
            "createdAt": "2026-07-28T10:00:00Z",
            "status": "Ready",
            "wasAutomated": False,
        },
        "implementationPlan": {
            "commentId": f"IC_plan_{number}",
            "permalink": f"https://github.com/acme/repo/issues/{number}#issuecomment-plan",
            "author": "chris",
            "digest": f"sha256:plan-{number}",
            "createdAt": "2026-07-28T09:00:00Z",
            "updatedAt": "2026-07-28T09:00:00Z",
            "plannedBranch": "main",
            "plannedSha": f"base-{number}",
        },
    }
    result.update(overrides)
    return result


def pull_request(number: int, **overrides: object) -> dict:
    result = {
        "number": number,
        "url": f"https://github.com/acme/repo/pull/{number}",
        "author": "chris",
        "closesIssue": True,
        "headRepository": "acme/repo",
        "headRefName": f"cb/issue-{number}",
        "headSha": f"head-{number}",
        "baseRepository": "acme/repo",
        "baseRefName": "main",
        "isDraft": False,
    }
    result.update(overrides)
    return result


def first_entry(output: dict) -> dict:
    entries = output["claims"] or output["candidates"]
    return entries[0]


class RankTicketsTest(unittest.TestCase):
    def test_returns_multiple_claims_and_candidates_up_to_limit(self) -> None:
        implementation = ticket(
            1,
            projectStatus="In progress",
            projectPriority="Low",
            assignees=["chris"],
        )
        pull_request_claim = ticket(
            2,
            projectStatus="In progress",
            projectPriority="High",
            assignees=["chris"],
            openPullRequests=[pull_request(200)],
        )
        candidate = ticket(3, projectPriority="Critical")

        returncode, output = run_ranker(
            [implementation, pull_request_claim, candidate],
            "--max-claims",
            "3",
        )

        self.assertEqual(0, returncode)
        self.assertNotIn("eligible", output)
        self.assertEqual(
            [2, 1],
            [entry["ticket"]["number"] for entry in output["claims"]],
        )
        self.assertEqual(
            [3],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )

    def test_stops_when_claims_exceed_limit(self) -> None:
        first = ticket(4, projectStatus="In progress", assignees=["chris"])
        second = ticket(5, projectStatus="In progress", assignees=["chris"])

        returncode, output = run_ranker([first, second])

        self.assertEqual(2, returncode)
        self.assertEqual("over-capacity-claims", output["reason"])
        self.assertEqual(1, output["claimLimit"])
        self.assertEqual([4, 5], output["claimed"])

    def test_blocked_claims_count_toward_the_limit(self) -> None:
        blocked = ticket(
            6,
            projectStatus="In progress",
            assignees=["chris"],
            labels=[],
        )
        valid = ticket(7, projectStatus="In progress", assignees=["chris"])

        returncode, output = run_ranker(
            [blocked, valid],
            "--max-claims",
            "1",
        )

        self.assertEqual(2, returncode)
        self.assertEqual("over-capacity-claims", output["reason"])
        self.assertEqual([6, 7], output["claimed"])

    def test_returns_all_candidates_in_scheduler_order(self) -> None:
        resumable_later = ticket(
            8,
            projectPriority="Low",
            projectPosition=99,
            openPullRequests=[pull_request(800)],
        )
        resumable_earlier = ticket(
            11,
            projectPriority="High",
            projectPosition=3,
            openPullRequests=[pull_request(1100)],
        )
        high = ticket(9, projectPriority="High", projectPosition=2)
        critical = ticket(10, projectPriority="Critical", projectPosition=20)

        returncode, output = run_ranker(
            [resumable_later, high, critical, resumable_earlier],
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [11, 8, 10, 9],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            ["resume-pr", "resume-pr", "claim", "claim"],
            [entry["action"] for entry in output["candidates"]],
        )

    def test_resumes_current_users_in_progress_item_before_ready_work(self) -> None:
        ready = ticket(1, projectPriority="Critical")
        in_progress = ticket(
            2,
            projectStatus="In progress",
            projectPriority="Low",
            projectPosition=99,
            assignees=["chris"],
        )

        returncode, output = run_ranker([ready, in_progress])

        self.assertEqual(0, returncode)
        self.assertEqual(2, first_entry(output)["ticket"]["number"])
        self.assertEqual("resume-implementation", first_entry(output)["action"])

    def test_ranks_ready_items_by_priority_then_project_position(self) -> None:
        later_on_board = ticket(3, projectPosition=20)
        earlier_on_board = ticket(4, projectPosition=2)
        critical = ticket(
            5,
            projectPriority="Critical",
            projectPosition=200,
        )

        returncode, output = run_ranker(
            [later_on_board, earlier_on_board, critical],
        )

        self.assertEqual(0, returncode)
        self.assertEqual(5, first_entry(output)["ticket"]["number"])

        returncode, output = run_ranker([later_on_board, earlier_on_board])

        self.assertEqual(0, returncode)
        self.assertEqual(4, first_entry(output)["ticket"]["number"])

    def test_open_descendants_make_a_parent_ineligible(self) -> None:
        parent = ticket(
            10,
            projectPriority="Critical",
            projectPosition=1,
            openDescendants=[11, 12],
        )
        child = ticket(11, projectPosition=2)

        returncode, output = run_ranker([parent, child])

        self.assertEqual(0, returncode)
        self.assertEqual(11, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [{"number": 10, "reasons": ["open descendants ['11', '12']"]}],
            output["excluded"],
        )

    def test_invalid_unclaimed_item_does_not_stop_other_ready_work(self) -> None:
        invalid = ticket(
            20,
            projectPriority="Emergency",
            projectPosition=1,
        )
        valid = ticket(
            21,
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker([invalid, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(21, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [{"number": 20, "reasons": ["unknown project priority 'Emergency'"]}],
            output["excluded"],
        )

    def test_unassigned_in_progress_item_is_stale_not_claimable(self) -> None:
        stale = ticket(
            40,
            projectStatus="In progress",
            projectPriority="Critical",
            projectPosition=1,
        )
        ready = ticket(
            41,
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker([stale, ready])

        self.assertEqual(0, returncode)
        self.assertEqual(41, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [{"number": 40, "reasons": ["in progress without an assignee"]}],
            output["excluded"],
        )

    def test_ready_assignment_without_verified_handoff_blocks_even_with_owned_pr(self) -> None:
        partial_claim = ticket(
            50,
            projectPosition=1,
            assignees=["chris"],
            openPullRequests=[pull_request(500)],
            implementationPlan=None,
        )

        returncode, output = run_ranker([partial_claim])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                {
                    "number": 50,
                    "reasons": [
                        "assigned to current user while project status is still ready",
                        "missing current implementation plan",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_invalid_claim_blocks_only_its_slot(self) -> None:
        invalid_claim = ticket(
            51,
            projectPosition=1,
            assignees=["chris"],
            projectStatus="In progress",
            labels=[],
        )
        valid_claim = ticket(
            52,
            projectStatus="In progress",
            assignees=["chris"],
        )
        candidate = ticket(53)

        returncode, output = run_ranker(
            [invalid_claim, valid_claim, candidate],
            "--max-claims",
            "3",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [51],
            [claim["number"] for claim in output["blockedClaims"]],
        )
        self.assertEqual(
            [52],
            [claim["ticket"]["number"] for claim in output["claims"]],
        )
        self.assertEqual(
            [53],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )

    def test_does_not_resume_own_pr_that_does_not_close_issue(self) -> None:
        unrelated_pr = ticket(
            60,
            projectPriority="Critical",
            projectPosition=1,
            openPullRequests=[
                pull_request(600, closesIssue=False),
            ],
        )
        valid = ticket(
            61,
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker([unrelated_pr, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(61, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [
                {
                    "number": 60,
                    "reasons": [
                        "current user's PR does not close the issue "
                        "https://github.com/acme/repo/pull/600",
                    ],
                },
            ],
            output["excluded"],
        )

    def test_malformed_unclaimed_item_is_reported_without_stopping(self) -> None:
        malformed = {
            "number": 70,
            "assignees": [],
        }
        valid = ticket(71, projectPosition=1)

        returncode, output = run_ranker([malformed, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(71, first_entry(output)["ticket"]["number"])
        self.assertEqual(70, output["excluded"][0]["number"])
        self.assertIn("missing", output["excluded"][0]["reasons"][0])

    def test_unset_priority_ranks_after_configured_priorities(self) -> None:
        unset = ticket(80, projectPriority=None, projectPosition=1)
        low = ticket(81, projectPriority="Low", projectPosition=100)

        returncode, output = run_ranker([unset, low])

        self.assertEqual(0, returncode)
        self.assertEqual(81, first_entry(output)["ticket"]["number"])

    def test_malformed_claimed_item_blocks_its_slot(self) -> None:
        malformed_claim = {
            "number": 90,
            "assignees": [{"login": "chris"}],
        }

        returncode, output = run_ranker([malformed_claim, ticket(91)])

        self.assertEqual(0, returncode)
        self.assertEqual(90, output["blockedClaims"][0]["number"])
        self.assertEqual(91, output["candidates"][0]["ticket"]["number"])

    def test_priority_order_is_required(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--current-user",
                "chris",
                *DEFAULT_PROJECT_ARGUMENTS,
            ],
            input="[]",
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("--priority", result.stderr)

    def test_assignee_objects_use_login_as_identity(self) -> None:
        claimed = ticket(
            100,
            projectStatus="In progress",
            assignees=[{"login": "chris", "name": "Chris Banes"}],
        )

        returncode, output = run_ranker([claimed])

        self.assertEqual(0, returncode)
        self.assertEqual(100, first_entry(output)["ticket"]["number"])
        self.assertEqual("resume-implementation", first_entry(output)["action"])

    def test_ready_handoff_rejects_project_workflow_automation(self) -> None:
        automated = ticket(
            110,
            readyTransition={
                "id": "PVTE_110",
                "actor": "github-project-automation",
                "createdAt": "2026-07-28T10:00:00Z",
                "status": "Ready",
                "wasAutomated": True,
            },
        )
        valid = ticket(111)

        returncode, output = run_ranker([automated, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(111, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [
                {
                    "number": 110,
                    "reasons": [
                        "ready transition came from Project workflow automation",
                    ],
                },
            ],
            output["excluded"],
        )

    def test_planning_transition_requires_configured_execution_approver(self) -> None:
        unapproved = ticket(
            120,
            projectStatus="Planning",
            implementationPlan=None,
            planningTransition={
                "id": "PVTE_120_planning",
                "actor": "outsider",
                "createdAt": "2026-07-28T08:00:00Z",
                "status": "Planning",
                "wasAutomated": False,
            },
        )
        valid = ticket(121)

        returncode, output = run_ranker([unapproved, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(121, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [
                {
                    "number": 120,
                    "reasons": [
                        "planning transition actor 'outsider' is not approved",
                    ],
                },
            ],
            output["excluded"],
        )

    def test_plan_edit_after_ready_invalidates_handoff(self) -> None:
        stale_handoff = ticket(
            130,
            implementationPlan={
                "commentId": "IC_plan_130",
                "permalink": "https://github.com/acme/repo/issues/130#issuecomment-plan",
                "author": "chris",
                "digest": "sha256:plan-130-edited",
                "createdAt": "2026-07-28T09:00:00Z",
                "updatedAt": "2026-07-28T11:00:00Z",
                "plannedBranch": "main",
                "plannedSha": "base-130",
            },
        )
        valid = ticket(131)

        returncode, output = run_ranker([stale_handoff, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(131, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [
                {
                    "number": 130,
                    "reasons": [
                        "ready transition predates the current implementation plan",
                    ],
                },
            ],
            output["excluded"],
        )

    def test_resume_pr_must_target_configured_repository_and_base(self) -> None:
        wrong_base = ticket(
            140,
            openPullRequests=[
                pull_request(1400, baseRepository="acme/other", baseRefName="release"),
            ],
        )
        valid = ticket(141)

        returncode, output = run_ranker([wrong_base, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(141, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [
                {
                    "number": 140,
                    "reasons": [
                        "current user's PR targets acme/other:release, expected acme/repo:main",
                    ],
                },
            ],
            output["excluded"],
        )

    def test_assignee_display_name_is_not_treated_as_login(self) -> None:
        ambiguous = ticket(150, assignees=[{"name": "chris"}])
        valid = ticket(151)

        returncode, output = run_ranker([ambiguous, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(151, first_entry(output)["ticket"]["number"])
        self.assertEqual(150, output["excluded"][0]["number"])
        self.assertIn("assignee", output["excluded"][0]["reasons"][0])

    def test_non_finite_project_position_is_invalid(self) -> None:
        invalid = ticket(160, projectPosition=float("nan"))
        valid = ticket(161)

        returncode, output = run_ranker([invalid, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(161, first_entry(output)["ticket"]["number"])
        self.assertEqual(
            [{"number": 160, "reasons": ["ticket 160: projectPosition must be finite"]}],
            output["excluded"],
        )

    def test_blocker_objects_must_be_normalized_to_identifiers(self) -> None:
        invalid = ticket(170, blockedBy=[{"number": 171}])
        valid = ticket(171)

        returncode, output = run_ranker([invalid, valid])

        self.assertEqual(0, returncode)
        self.assertEqual(171, first_entry(output)["ticket"]["number"])
        self.assertEqual(170, output["excluded"][0]["number"])
        self.assertIn("strings or integers", output["excluded"][0]["reasons"][0])

    def test_returns_authorized_planning_item_after_implementation_work(self) -> None:
        planning = ticket(
            180,
            projectStatus="Planning",
            projectPriority="Critical",
            projectPosition=1,
            labels=["ready-for-agent"],
            planningTransition={
                "id": "PVTE_180_planning",
                "actor": "maintainer",
                "createdAt": "2026-07-28T08:00:00Z",
                "status": "Planning",
                "wasAutomated": False,
            },
            implementationPlan=None,
        )
        implementation = ticket(
            181,
            projectPriority="Low",
            projectPosition=99,
        )

        returncode, output = run_ranker([planning, implementation])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [(181, "claim"), (180, "plan")],
            [
                (entry["ticket"]["number"], entry["action"])
                for entry in output["candidates"]
            ],
        )

    def test_planning_requires_ready_for_agent_label(self) -> None:
        planning = ticket(
            182,
            projectStatus="Planning",
            labels=[],
            implementationPlan=None,
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertEqual(
            [{"number": 182, "reasons": ["missing ready-for-agent label"]}],
            output["excluded"],
        )

    def test_planning_requires_human_execution_approver_transition(self) -> None:
        planning = ticket(
            183,
            projectStatus="Planning",
            implementationPlan=None,
            planningTransition={
                "id": "PVTE_183_planning",
                "actor": "github-project-automation",
                "createdAt": "2026-07-28T08:00:00Z",
                "status": "Planning",
                "wasAutomated": True,
            },
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertEqual(
            [{"number": 183, "reasons": ["planning transition was automated"]}],
            output["excluded"],
        )

    def test_resumes_assigned_planning_claim(self) -> None:
        planning = ticket(
            184,
            projectStatus="Planning",
            assignees=["chris"],
            implementationPlan=None,
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [(184, "resume-planning")],
            [
                (entry["ticket"]["number"], entry["action"])
                for entry in output["claims"]
            ],
        )

    def test_planning_claim_does_not_consume_implementation_slot(self) -> None:
        planning = ticket(
            185,
            projectStatus="Planning",
            assignees=["chris"],
            implementationPlan=None,
        )
        implementation = ticket(
            186,
            projectStatus="In progress",
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [planning, implementation],
            "--max-claims",
            "1",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            ["resume-implementation", "resume-planning"],
            [entry["action"] for entry in output["claims"]],
        )

    def test_resumes_planning_handoff_when_current_plan_is_published(self) -> None:
        planning = ticket(
            187,
            projectStatus="Planning",
            assignees=["chris"],
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual(
            "resume-planning-handoff",
            output["claims"][0]["action"],
        )

    def test_new_human_planning_transition_requests_replanning(self) -> None:
        planning = ticket(
            189,
            projectStatus="Planning",
            assignees=["chris"],
            planningTransition={
                "id": "PVTE_189_replan",
                "actor": "maintainer",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Planning",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual("resume-planning", output["claims"][0]["action"])

    def test_planning_item_with_wrong_branch_is_replanned(self) -> None:
        planning = ticket(
            192,
            projectStatus="Planning",
            assignees=["chris"],
            implementationPlan={
                "commentId": "IC_plan_192",
                "permalink": "https://github.com/acme/repo/issues/192#issuecomment-plan",
                "author": "chris",
                "digest": "sha256:plan-192",
                "createdAt": "2026-07-28T09:00:00Z",
                "updatedAt": "2026-07-28T09:00:00Z",
                "plannedBranch": "release",
                "plannedSha": "base-192",
            },
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["blockedPlanningClaims"])
        self.assertEqual("resume-planning", output["claims"][0]["action"])

    def test_planning_item_with_another_authors_marker_is_blocked(self) -> None:
        planning = ticket(
            193,
            projectStatus="Planning",
            assignees=["chris"],
            implementationPlan={
                "commentId": "IC_plan_193",
                "permalink": "https://github.com/acme/repo/issues/193#issuecomment-plan",
                "author": "mallory",
                "digest": "sha256:plan-193",
                "createdAt": "2026-07-28T09:00:00Z",
                "updatedAt": "2026-07-28T09:00:00Z",
                "plannedBranch": "main",
                "plannedSha": "base-193",
            },
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 193,
                    "reasons": [
                        "implementation plan author 'mallory' "
                        "does not match current user 'chris'",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_resumes_verified_runner_requeue_in_planning(self) -> None:
        requeued = ticket(
            197,
            projectStatus="Planning",
            assignees=["chris"],
        )
        requeued["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )

        returncode, output = run_ranker([requeued])

        self.assertEqual(0, returncode)
        self.assertEqual("resume-planning", output["claims"][0]["action"])

    def test_runner_requeue_requires_verified_prior_ready_handoff(self) -> None:
        invalid_requeue = ticket(
            198,
            projectStatus="Planning",
            assignees=["chris"],
        )
        invalid_requeue["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )
        invalid_requeue["implementationPlan"]["updatedAt"] = "2026-07-28T11:00:00Z"

        returncode, output = run_ranker([invalid_requeue])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 198,
                    "reasons": [
                        "runner Planning requeue lacks a verified prior Ready handoff",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_ready_handoff_rejects_another_authors_marker(self) -> None:
        handoff = ticket(
            196,
            assignees=["chris"],
            implementationPlan={
                "commentId": "IC_plan_196",
                "permalink": "https://github.com/acme/repo/issues/196#issuecomment-plan",
                "author": "mallory",
                "digest": "sha256:plan-196",
                "createdAt": "2026-07-28T09:00:00Z",
                "updatedAt": "2026-07-28T09:00:00Z",
                "plannedBranch": "main",
                "plannedSha": "base-196",
            },
        )

        returncode, output = run_ranker([handoff])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                {
                    "number": 196,
                    "reasons": [
                        "assigned to current user while project status is still ready",
                        "implementation plan author 'mallory' "
                        "does not match current user 'chris'",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_resumes_verified_runner_authored_ready_handoff(self) -> None:
        handoff = ticket(
            188,
            assignees=["chris"],
            readyTransition={
                "id": "PVTE_188_ready",
                "actor": "chris",
                "createdAt": "2026-07-28T10:00:00Z",
                "status": "Ready",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([handoff])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["blockedClaims"])
        self.assertEqual(
            "resume-planning-handoff",
            output["claims"][0]["action"],
        )

    def test_ready_handoff_does_not_consume_implementation_slot(self) -> None:
        handoff = ticket(190, assignees=["chris"])
        implementation = ticket(
            191,
            projectStatus="In progress",
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [handoff, implementation],
            "--max-claims",
            "1",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            ["resume-implementation", "resume-planning-handoff"],
            [entry["action"] for entry in output["claims"]],
        )

    def test_ready_handoff_attests_reuse_of_an_older_verified_plan(self) -> None:
        handoff = ticket(
            194,
            assignees=["chris"],
            implementationPlan={
                "commentId": "IC_plan_194",
                "permalink": "https://github.com/acme/repo/issues/194#issuecomment-plan",
                "author": "chris",
                "digest": "sha256:plan-194",
                "createdAt": "2026-07-28T07:00:00Z",
                "updatedAt": "2026-07-28T07:00:00Z",
                "plannedBranch": "main",
                "plannedSha": "base-194",
            },
        )

        returncode, output = run_ranker([handoff])

        self.assertEqual(0, returncode)
        self.assertEqual(
            "resume-planning-handoff",
            output["claims"][0]["action"],
        )

    def test_ready_handoff_must_follow_latest_planning_authorization(self) -> None:
        stale_handoff = ticket(
            195,
            assignees=["chris"],
            readyTransition={
                "id": "PVTE_195_ready",
                "actor": "chris",
                "createdAt": "2026-07-28T07:30:00Z",
                "status": "Ready",
                "wasAutomated": False,
            },
            implementationPlan={
                "commentId": "IC_plan_195",
                "permalink": "https://github.com/acme/repo/issues/195#issuecomment-plan",
                "author": "chris",
                "digest": "sha256:plan-195",
                "createdAt": "2026-07-28T07:00:00Z",
                "updatedAt": "2026-07-28T07:00:00Z",
                "plannedBranch": "main",
                "plannedSha": "base-195",
            },
        )

        returncode, output = run_ranker([stale_handoff])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                {
                    "number": 195,
                    "reasons": [
                        "assigned to current user while project status is still ready",
                        "ready transition predates the latest planning authorization",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )


if __name__ == "__main__":
    unittest.main()
