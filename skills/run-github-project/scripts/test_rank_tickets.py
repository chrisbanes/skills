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
    "--configuration-digest",
    "sha256:config",
    "--base-branch",
    "main",
    "--execution-approver",
    "maintainer",
)
DEFAULT_STATUS_ARGUMENTS = (
    "--backlog-status",
    "Backlog",
    "--ready-status",
    "Ready",
    "--in-progress-status",
    "In progress",
    "--needs-triage-label",
    "needs-triage",
    "--epic-label",
    "epic",
    "--human-work-label",
    "ready-for-human",
)
DEFAULT_WAYFINDER_ARGUMENTS = (
    "--wayfinder-map-label",
    "wayfinder:map",
    "--wayfinder-research-label",
    "wayfinder:research",
    "--wayfinder-prototype-label",
    "wayfinder:prototype",
    "--wayfinder-grilling-label",
    "wayfinder:grilling",
    "--wayfinder-task-label",
    "wayfinder:task",
)


def implementation_plan(number: int, **overrides: object) -> dict:
    result = {
        "commentId": f"IC_plan_{number}",
        "permalink": (
            f"https://github.com/acme/repo/issues/{number}#issuecomment-plan"
        ),
        "author": "chris",
        "digest": f"sha256:plan-{number}",
        "createdAt": "2026-07-28T09:00:00Z",
        "publishedAt": "2026-07-28T09:00:00Z",
        "updatedAt": "2026-07-28T09:00:00Z",
        "plannedBranch": "main",
        "plannedSha": f"base-{number}",
        "markerVersion": 2,
        "revision": 1,
        "supersedes": None,
        "replanRequest": None,
        "isMinimized": False,
    }
    result.update(overrides)
    return result


def run_ranker(
    items: list[dict],
    *arguments: str,
    mode: str = "drain",
) -> tuple[int, dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--mode",
            mode,
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
        "implementationPlans": [implementation_plan(number)],
    }
    if "implementationPlan" in overrides:
        result.pop("implementationPlans")
    result.update(overrides)
    return result


def backlog_ticket(number: int, **overrides: object) -> dict:
    result = ticket(
        number,
        projectStatus="Backlog",
        labels=["needs-triage"],
        planningTransition=None,
        readyTransition=None,
        implementationPlan=None,
    )
    result.update(overrides)
    return result


def wayfinder_ticket(
    number: int,
    *,
    ticket_type: str = "research",
    **overrides: object,
) -> dict:
    result = ticket(
        number,
        projectStatus="Planning",
        labels=[f"wayfinder:{ticket_type}"],
        planningTransition={
            "id": f"PVTE_{number}_planning",
            "actor": "maintainer",
            "createdAt": "2026-07-28T08:00:00Z",
            "status": "Planning",
            "wasAutomated": False,
        },
        readyTransition=None,
        implementationPlan=None,
        parentIssue={
            "number": 1,
            "state": "OPEN",
            "labels": ["wayfinder:map"],
        },
    )
    result.update(overrides)
    return result


def wayfinder_reconciliation(number: int, **overrides: object) -> dict:
    result = {
        "commentId": f"IC_wayfinder_reconciliation_{number}",
        "permalink": (
            f"https://github.com/acme/repo/issues/{number}#issuecomment-reconcile"
        ),
        "author": "chris",
        "createdAt": "2026-07-28T09:00:00Z",
        "markerVersion": 1,
        "disposition": "resolved",
        "mapNumber": 1,
        "projectItemId": f"PVTI_{number}",
        "outcomePermalink": (
            f"https://github.com/acme/repo/issues/{number}#issuecomment-resolution"
        ),
        "configurationDigest": "sha256:config",
        "planDigest": f"sha256:wayfinder-{number}",
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


def replan_request(
    number: int,
    *,
    disposition: str = "autonomous-replan",
    **overrides: object,
) -> dict:
    result = {
        "commentId": f"IC_replan_{number}",
        "permalink": (
            f"https://github.com/acme/repo/issues/{number}#issuecomment-replan"
        ),
        "author": "chris",
        "createdAt": "2026-07-28T11:00:00Z",
        "disposition": disposition,
        "previousPlanPermalink": (
            f"https://github.com/acme/repo/issues/{number}#issuecomment-plan"
        ),
        "previousPlanDigest": f"sha256:plan-{number}",
        "baseSha": f"base-{number}",
        "implementationHeadSha": None,
        "pullRequestUrl": None,
    }
    result.update(overrides)
    return result


def first_entry(output: dict) -> dict:
    entries = output["claims"] or output["candidates"]
    return entries[0]


class RankTicketsTest(unittest.TestCase):
    def test_disabled_wayfinder_preserves_the_existing_output_shape(self) -> None:
        returncode, output = run_ranker([ticket(199)])

        self.assertEqual(0, returncode)
        self.assertNotIn("wayfinderHumanFrontier", output)
        self.assertNotIn("wayfinderClaimedHitl", output)

    def test_selects_the_unique_unsuperseded_plan_revision(self) -> None:
        old_permalink = (
            "https://github.com/acme/repo/issues/202#issuecomment-plan-v1"
        )
        replan_permalink = (
            "https://github.com/acme/repo/issues/202#issuecomment-replan"
        )
        versioned = ticket(
            202,
            implementationPlans=[
                implementation_plan(
                    202,
                    commentId="IC_plan_202_v1",
                    permalink=old_permalink,
                    digest="sha256:plan-202-v1",
                    updatedAt="2026-07-28T13:30:00Z",
                    markerVersion=1,
                    isMinimized=True,
                ),
                implementation_plan(
                    202,
                    commentId="IC_plan_202_v2",
                    permalink=(
                        "https://github.com/acme/repo/issues/202#issuecomment-plan-v2"
                    ),
                    digest="sha256:plan-202-v2",
                    createdAt="2026-07-28T13:00:00Z",
                    publishedAt="2026-07-28T13:00:00Z",
                    updatedAt="2026-07-28T13:00:00Z",
                    revision=2,
                    supersedes=old_permalink,
                    replanRequest=replan_permalink,
                ),
            ],
            readyTransition={
                "id": "PVTE_202_ready",
                "actor": "chris",
                "createdAt": "2026-07-28T14:00:00Z",
                "status": "Ready",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([versioned])

        self.assertEqual(0, returncode)
        self.assertEqual("claim", output["candidates"][0]["action"])

    def test_requeued_ticket_hands_off_after_a_new_plan_revision(self) -> None:
        old_permalink = (
            "https://github.com/acme/repo/issues/203#issuecomment-plan-v1"
        )
        replan = replan_request(
            203,
            previousPlanPermalink=old_permalink,
            previousPlanDigest="sha256:plan-203-v1",
        )
        requeued = ticket(
            203,
            projectStatus="Planning",
            assignees=["chris"],
            implementationPlans=[
                implementation_plan(
                    203,
                    commentId="IC_plan_203_v1",
                    permalink=old_permalink,
                    digest="sha256:plan-203-v1",
                    updatedAt="2026-07-28T13:30:00Z",
                    markerVersion=1,
                    isMinimized=True,
                ),
                implementation_plan(
                    203,
                    commentId="IC_plan_203_v2",
                    permalink=(
                        "https://github.com/acme/repo/issues/203#issuecomment-plan-v2"
                    ),
                    digest="sha256:plan-203-v2",
                    createdAt="2026-07-28T13:00:00Z",
                    publishedAt="2026-07-28T13:00:00Z",
                    updatedAt="2026-07-28T13:00:00Z",
                    revision=2,
                    supersedes=old_permalink,
                    replanRequest=replan["permalink"],
                ),
            ],
            replanRequest=replan,
        )
        requeued["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )

        returncode, output = run_ranker([requeued])

        self.assertEqual(0, returncode)
        self.assertEqual(
            "resume-planning-handoff",
            output["claims"][0]["action"],
        )

        requeued["implementationPlans"][1]["replanRequest"] = None
        returncode, output = run_ranker([requeued])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 203,
                    "reasons": [
                        "active plan revision does not link the verified "
                        "replan report",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_assigned_backlog_item_resumes_cleanup_without_consuming_slot(self) -> None:
        backlog = ticket(
            200,
            projectStatus="Backlog",
            assignees=["chris"],
            replanRequest=replan_request(200, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_200_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
        )
        implementation = ticket(
            201,
            projectStatus="In progress",
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [backlog, implementation],
            "--max-claims",
            "1",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            ["resume-backlog-cleanup", "resume-implementation"],
            [entry["action"] for entry in output["claims"]],
        )

    def test_keeps_assigned_cleanup_separate_from_unassigned_triage(self) -> None:
        cleanup = ticket(
            205,
            projectStatus="Backlog",
            assignees=["chris"],
            replanRequest=replan_request(205, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_205_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
        )
        triage = backlog_ticket(206)

        returncode, output = run_ranker([triage, cleanup])

        self.assertEqual(0, returncode)
        self.assertEqual(
            ["resume-backlog-cleanup"],
            [entry["action"] for entry in output["claims"]],
        )
        self.assertEqual(
            [206],
            [
                entry["ticket"]["number"]
                for entry in output["triageCandidates"]
            ],
        )

    def test_backlog_cleanup_ignores_implementation_readiness_changes(self) -> None:
        backlog = ticket(
            209,
            state="CLOSED",
            projectStatus="Backlog",
            labels=[],
            assignees=["chris"],
            blockedBy=[99],
            openDescendants=[100],
            replanRequest=replan_request(209, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_209_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([backlog])

        self.assertEqual(0, returncode)
        self.assertEqual(
            "resume-backlog-cleanup",
            output["claims"][0]["action"],
        )

    def test_unassigned_backlog_item_waits_for_human_planning_transition(self) -> None:
        backlog = ticket(
            204,
            projectStatus="Backlog",
            assignees=[],
            replanRequest=replan_request(204, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_204_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([backlog])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual([], output["candidates"])
        self.assertEqual(
            [
                {
                    "ticket": backlog,
                    "action": "move-to-planning",
                },
            ],
            output["humanActions"],
        )

    def test_human_planning_transition_after_backlog_starts_fresh(self) -> None:
        planning = ticket(
            205,
            projectStatus="Planning",
            assignees=[],
            replanRequest=replan_request(205, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_205_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
            planningTransition={
                "id": "PVTE_205_planning",
                "actor": "maintainer",
                "createdAt": "2026-07-28T15:00:00Z",
                "status": "Planning",
                "wasAutomated": False,
            },
        )

        returncode, output = run_ranker([planning])

        self.assertEqual(0, returncode)
        self.assertEqual("plan", output["candidates"][0]["action"])

    def test_broken_plan_revision_chain_is_ineligible(self) -> None:
        broken = ticket(
            206,
            implementationPlans=[
                implementation_plan(
                    206,
                    revision=2,
                    supersedes=(
                        "https://github.com/acme/repo/issues/206"
                        "#issuecomment-missing"
                    ),
                ),
            ],
        )

        returncode, output = run_ranker([broken])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertIn(
            "implementation plan chain must have exactly one root",
            output["excluded"][0]["reasons"][0],
        )

    def test_ready_handoff_rejects_active_plan_edited_after_transition(self) -> None:
        handoff = ticket(207)
        handoff["implementationPlans"][0]["updatedAt"] = "2026-07-28T11:00:00Z"

        returncode, output = run_ranker([handoff])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertIn(
            "ready transition predates the current implementation plan",
            output["excluded"][0]["reasons"],
        )

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

    def test_ranks_unblocked_backlog_triage_candidates_separately(self) -> None:
        later = backlog_ticket(12, projectPosition=20)
        earlier = backlog_ticket(13, projectPosition=2)
        critical = backlog_ticket(
            14,
            projectPriority="Critical",
            projectPosition=200,
        )
        implementation = ticket(15, projectPriority="Low")

        returncode, output = run_ranker(
            [later, earlier, critical, implementation],
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [14, 13, 12],
            [
                entry["ticket"]["number"]
                for entry in output["triageCandidates"]
            ],
        )
        self.assertEqual(
            ["triage", "triage", "triage"],
            [entry["action"] for entry in output["triageCandidates"]],
        )
        self.assertEqual(
            [15],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )

    def test_parks_backlog_item_with_open_native_blocker(self) -> None:
        blocked = backlog_ticket(16, blockedBy=[17])

        returncode, output = run_ranker([blocked])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["triageCandidates"])
        self.assertEqual(
            [
                {
                    "ticket": blocked,
                    "role": "triage",
                    "reasons": ["blocked by ['17']"],
                },
            ],
            output["parkedBlocked"],
        )
        self.assertEqual([], output["excluded"])

    def test_parks_backlog_parent_with_open_descendant(self) -> None:
        parent = backlog_ticket(18, openDescendants=[19])

        returncode, output = run_ranker([parent])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["triageCandidates"])
        self.assertEqual(
            [
                {
                    "ticket": parent,
                    "role": "triage",
                    "reasons": ["open descendants ['19']"],
                },
            ],
            output["parkedBlocked"],
        )

    def test_unblocked_epic_is_ready_for_reconciliation(self) -> None:
        epic = backlog_ticket(19, labels=["epic"])

        returncode, output = run_ranker([epic])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [{"ticket": epic, "action": "close-epic"}],
            output["readyEpics"],
        )

    def test_parks_epic_until_its_native_descendants_close(self) -> None:
        epic = backlog_ticket(
            20,
            labels=["epic"],
            openDescendants=[21],
        )

        returncode, output = run_ranker([epic])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["readyEpics"])
        self.assertEqual(
            [
                {
                    "ticket": epic,
                    "role": "epic",
                    "reasons": ["open descendants ['21']"],
                },
            ],
            output["parkedBlocked"],
        )

    def test_human_gated_epic_is_never_automatically_closed(self) -> None:
        epic = backlog_ticket(
            21,
            labels=["epic", "ready-for-human"],
        )

        returncode, output = run_ranker([epic])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["readyEpics"])
        self.assertEqual(
            [{"ticket": epic, "action": "perform-human-work"}],
            output["humanActions"],
        )

    def test_human_work_waits_for_native_blockers(self) -> None:
        human_work = backlog_ticket(
            22,
            labels=["ready-for-human"],
            blockedBy=[20],
        )

        returncode, output = run_ranker([human_work])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["humanActions"])
        self.assertEqual(
            [
                {
                    "ticket": human_work,
                    "role": "human",
                    "reasons": ["blocked by ['20']"],
                },
            ],
            output["parkedBlocked"],
        )

    def test_current_user_assignment_does_not_turn_human_work_into_cleanup(self) -> None:
        human_work = backlog_ticket(
            23,
            labels=["ready-for-human"],
            assignees=["chris"],
        )

        returncode, output = run_ranker([human_work])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual([], output["blockedPlanningClaims"])
        self.assertEqual(
            [{"ticket": human_work, "action": "perform-human-work"}],
            output["humanActions"],
        )

    def test_malformed_assigned_human_work_is_not_a_planning_claim(self) -> None:
        human_work = backlog_ticket(
            24,
            labels=["ready-for-human"],
            assignees=["chris"],
        )
        del human_work["projectPosition"]

        returncode, output = run_ranker([human_work])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["blockedPlanningClaims"])
        self.assertEqual(
            [{"number": 24, "reasons": ["ticket 24: missing projectPosition"]}],
            output["excluded"],
        )

    def test_ready_for_agent_backlog_item_requests_planning_transition(self) -> None:
        ready = backlog_ticket(22, labels=["ready-for-agent"])

        returncode, output = run_ranker([ready])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["triageCandidates"])
        self.assertEqual([], output["parkedBlocked"])
        self.assertEqual(
            [{"ticket": ready, "action": "move-to-planning"}],
            output["humanActions"],
        )

    def test_human_action_does_not_hide_runnable_agent_work(self) -> None:
        human_work = backlog_ticket(24, labels=["ready-for-human"])
        agent_work = ticket(25)

        returncode, output = run_ranker([human_work, agent_work])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [25],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            [24],
            [entry["ticket"]["number"] for entry in output["humanActions"]],
        )

    def test_rejects_conflicting_backlog_action_labels(self) -> None:
        conflicting = backlog_ticket(
            26,
            labels=["ready-for-agent", "ready-for-human"],
        )
        implementation_epic = backlog_ticket(
            27,
            labels=["epic", "ready-for-agent"],
        )

        returncode, output = run_ranker([conflicting, implementation_epic])

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                {"number": 26, "reasons": ["conflicting Backlog action labels"]},
                {
                    "number": 27,
                    "reasons": ["epic cannot be ready for agent implementation"],
                },
            ],
            output["excluded"],
        )

    def test_does_not_automatically_triage_assigned_backlog_item(self) -> None:
        assigned = backlog_ticket(23, assignees=["maintainer"])

        returncode, output = run_ranker([assigned])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["triageCandidates"])
        self.assertEqual(
            [{"number": 23, "reasons": ["assigned to ['maintainer']"]}],
            output["excluded"],
        )

    def test_does_not_automatically_triage_backlog_item_with_open_pr(self) -> None:
        with_pull_request = backlog_ticket(
            24,
            openPullRequests=[
                {
                    "number": 240,
                    "url": "https://github.com/acme/repo/pull/240",
                    "closesIssue": True,
                },
            ],
        )

        returncode, output = run_ranker([with_pull_request])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["triageCandidates"])
        self.assertEqual(
            [
                {
                    "number": 24,
                    "reasons": [
                        "has open implementation PRs "
                        "['https://github.com/acme/repo/pull/240']",
                    ],
                },
            ],
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

    def test_status_names_must_be_unique(self) -> None:
        returncode, output = run_ranker(
            [],
            "--backlog-status",
            "Ready",
        )

        self.assertEqual(2, returncode)
        self.assertEqual("invalid-input", output["reason"])
        self.assertEqual("project statuses must be unique", output["error"])

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
            replanRequest=replan_request(197),
        )
        requeued["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )

        returncode, output = run_ranker([requeued])

        self.assertEqual(0, returncode)
        self.assertEqual("resume-planning", output["claims"][0]["action"])

    def test_runner_requeue_requires_verified_replan_report(self) -> None:
        invalid_requeue = ticket(
            199,
            projectStatus="Planning",
            assignees=["chris"],
        )
        invalid_requeue["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )

        returncode, output = run_ranker([invalid_requeue])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 199,
                    "reasons": [
                        "runner Planning requeue lacks a verified replan report",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_runner_requeue_requires_report_to_name_retained_pr(self) -> None:
        invalid_requeue = ticket(
            208,
            projectStatus="Planning",
            assignees=["chris"],
            replanRequest=replan_request(
                208,
                pullRequestUrl="https://github.com/acme/repo/pull/208",
                implementationHeadSha="wrong-head",
            ),
            openPullRequests=[pull_request(208)],
        )
        invalid_requeue["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )

        returncode, output = run_ranker([invalid_requeue])

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertIn(
            "runner Planning requeue lacks verified retained PR evidence",
            output["blockedPlanningClaims"][0]["reasons"],
        )

        invalid_requeue["replanRequest"]["implementationHeadSha"] = "head-208"
        returncode, output = run_ranker([invalid_requeue])

        self.assertEqual(0, returncode)
        self.assertEqual("resume-planning", output["claims"][0]["action"])

    def test_runner_requeue_requires_verified_prior_ready_handoff(self) -> None:
        invalid_requeue = ticket(
            198,
            projectStatus="Planning",
            assignees=["chris"],
            replanRequest=replan_request(198),
        )
        invalid_requeue["planningTransition"].update(
            actor="chris",
            createdAt="2026-07-28T12:00:00Z",
        )
        invalid_requeue["implementationPlans"][0]["publishedAt"] = (
            "2026-07-28T11:00:00Z"
        )
        invalid_requeue["implementationPlans"][0]["updatedAt"] = (
            "2026-07-28T11:00:00Z"
        )

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

    def test_ranks_unclaimed_wayfinder_research_in_the_planning_lane(self) -> None:
        ordinary_planning = ticket(
            301,
            projectStatus="Planning",
            projectPriority="High",
            projectPosition=30,
            labels=["ready-for-agent"],
            readyTransition=None,
            implementationPlan=None,
        )
        wayfinder_research = wayfinder_ticket(
            302,
            projectPriority="Critical",
            projectPosition=40,
        )

        returncode, output = run_ranker(
            [ordinary_planning, wayfinder_research],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [302, 301],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            ["wayfind", "plan"],
            [entry["action"] for entry in output["candidates"]],
        )

    def test_wayfinder_requires_one_type_an_open_map_and_fresh_human_planning(self) -> None:
        valid = wayfinder_ticket(303)
        wrong_parent = wayfinder_ticket(
            304,
            parentIssue={
                "number": 1,
                "state": "CLOSED",
                "labels": ["wayfinder:map"],
            },
        )
        ambiguous_type = wayfinder_ticket(
            305,
            labels=["wayfinder:research", "wayfinder:task"],
        )
        automated = wayfinder_ticket(
            306,
            planningTransition={
                "id": "PVTE_306_planning",
                "actor": "maintainer",
                "createdAt": "2026-07-28T08:00:00Z",
                "status": "Planning",
                "wasAutomated": True,
            },
        )

        returncode, output = run_ranker(
            [valid, wrong_parent, ambiguous_type, automated],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [303],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            [304, 305, 306],
            [entry["number"] for entry in output["excluded"]],
        )

    def test_surfaces_hitl_wayfinder_work_without_blocking_afk_work(self) -> None:
        research = wayfinder_ticket(307, ticket_type="research")
        afk_task = wayfinder_ticket(
            308,
            ticket_type="task",
            wayfinderTaskMode="afk",
            wayfinderAfkEvidence="The ticket lists only a safe local inventory command.",
        )
        prototype = wayfinder_ticket(309, ticket_type="prototype")
        ambiguous_task = wayfinder_ticket(310, ticket_type="task")
        ordinary = ticket(311, projectPriority="Low")

        returncode, output = run_ranker(
            [ordinary, prototype, ambiguous_task, research, afk_task],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [311, 307, 308],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            [309, 310],
            [entry["ticket"]["number"] for entry in output["wayfinderHumanFrontier"]],
        )
        self.assertEqual([], output["wayfinderClaimedHitl"])
        self.assertEqual(
            ["prototype", "task"],
            [entry["type"] for entry in output["wayfinderHumanFrontier"]],
        )

    def test_malformed_unclaimed_wayfinder_does_not_block_ordinary_execution(self) -> None:
        malformed = wayfinder_ticket(
            312,
            parentIssue={
                "number": 1,
                "state": "OPEN",
                "labels": [],
            },
        )
        ordinary = ticket(313)

        returncode, output = run_ranker(
            [malformed, ordinary],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [313],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual(
            [{"number": 312, "reasons": ["parent is not an open Wayfinder map"]}],
            output["excluded"],
        )

    def test_map_label_alone_is_not_a_wayfinder_child(self) -> None:
        map_only = ticket(
            314,
            projectStatus="Planning",
            labels=["wayfinder:map", "ready-for-agent"],
            readyTransition=None,
            implementationPlan=None,
        )

        returncode, output = run_ranker(
            [map_only],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertEqual(
            [
                {
                    "number": 314,
                    "reasons": ["Wayfinder map is not a child candidate"],
                },
            ],
            output["excluded"],
        )

    def test_preserves_an_assigned_invalid_wayfinder_as_a_planning_blocker(self) -> None:
        claimed = wayfinder_ticket(
            315,
            assignees=["chris"],
            openDescendants=[316],
        )

        returncode, output = run_ranker(
            [claimed],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["candidates"])
        self.assertEqual(
            [{"number": 315, "reasons": ["open descendants ['316']"]}],
            output["blockedPlanningClaims"],
        )

    def test_preserves_an_assigned_map_and_child_collision_as_a_planning_blocker(
        self,
    ) -> None:
        collision = wayfinder_ticket(
            316,
            assignees=["chris"],
            labels=["wayfinder:map", "wayfinder:research"],
        )

        returncode, output = run_ranker(
            [collision],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                {
                    "number": 316,
                    "reasons": ["Wayfinder map cannot carry a child type label"],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_assigned_hitl_wayfinder_is_not_called_frontier_work(self) -> None:
        assigned_prototype = wayfinder_ticket(
            317,
            ticket_type="prototype",
            assignees=["chris"],
        )
        afk_research = wayfinder_ticket(318)

        returncode, output = run_ranker(
            [assigned_prototype, afk_research],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [318],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual([], output["wayfinderHumanFrontier"])
        self.assertEqual(
            [317],
            [entry["ticket"]["number"] for entry in output["wayfinderClaimedHitl"]],
        )
        self.assertEqual(
            "resume-wayfinder-hitl",
            output["wayfinderClaimedHitl"][0]["action"],
        )

    def test_next_selects_hitl_wayfinder_by_planning_rank(self) -> None:
        prototype = wayfinder_ticket(
            319,
            ticket_type="prototype",
            projectPriority="Critical",
        )
        research = wayfinder_ticket(320, projectPriority="High")

        returncode, output = run_ranker(
            [research, prototype],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            mode="next",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [319, 320],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )
        self.assertEqual([], output["wayfinderHumanFrontier"])

    def test_next_honors_an_explicit_wayfinder_ticket_over_project_rank(self) -> None:
        selected = wayfinder_ticket(324, projectPriority="Low")
        higher_wayfinder = wayfinder_ticket(325, projectPriority="Critical")
        ordinary = ticket(326, projectPriority="Critical")

        returncode, output = run_ranker(
            [ordinary, higher_wayfinder, selected],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            "--wayfinder-ticket",
            "324",
            mode="next",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(324, output["selectedWayfinderTicket"])
        self.assertEqual(
            [324],
            [entry["ticket"]["number"] for entry in output["candidates"]],
        )

    def test_explicit_wayfinder_ticket_cannot_bypass_an_existing_claim(self) -> None:
        selected = wayfinder_ticket(327)
        existing_claim = ticket(
            328,
            projectStatus="In progress",
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [selected, existing_claim],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            "--wayfinder-ticket",
            "327",
            mode="next",
        )

        self.assertEqual(2, returncode)
        self.assertIn("cannot bypass existing claims [328]", output["error"])

    def test_explicit_wayfinder_ticket_is_not_available_in_drain(self) -> None:
        returncode, output = run_ranker(
            [wayfinder_ticket(329)],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            "--wayfinder-ticket",
            "329",
        )

        self.assertEqual(2, returncode)
        self.assertEqual(
            "an explicit Wayfinder ticket requires next mode",
            output["error"],
        )

    def test_explicit_wayfinder_ticket_does_not_fall_back_when_ineligible(self) -> None:
        selected = wayfinder_ticket(
            331,
            blockedBy=[330],
        )
        fallback = wayfinder_ticket(332, projectPriority="Critical")

        returncode, output = run_ranker(
            [fallback, selected],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            "--wayfinder-ticket",
            "331",
            mode="next",
        )

        self.assertEqual(2, returncode)
        self.assertIn(
            "selected Wayfinder ticket 331 is ineligible: blocked by ['330']",
            output["error"],
        )

    def test_next_resumes_an_assigned_hitl_wayfinder_claim(self) -> None:
        prototype = wayfinder_ticket(
            321,
            ticket_type="prototype",
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [prototype],
            *DEFAULT_WAYFINDER_ARGUMENTS,
            mode="next",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [321],
            [entry["ticket"]["number"] for entry in output["claims"]],
        )
        self.assertEqual("resume-wayfind", output["claims"][0]["action"])

    def test_resumes_terminal_wayfinder_reconciliation_after_closure(self) -> None:
        interrupted = wayfinder_ticket(
            322,
            assignees=["chris"],
            state="CLOSED",
            projectStatus="Done",
            parentIssue={
                "number": 1,
                "state": "CLOSED",
                "labels": ["wayfinder:map"],
            },
            wayfinderReconciliation=wayfinder_reconciliation(322),
        )

        returncode, output = run_ranker(
            [interrupted],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [322],
            [entry["ticket"]["number"] for entry in output["claims"]],
        )
        self.assertEqual(
            "resume-wayfinder-reconciliation",
            output["claims"][0]["action"],
        )

    def test_wayfinder_reconciliation_stays_behind_earlier_claim_classes(self) -> None:
        cleanup = ticket(
            335,
            projectStatus="Backlog",
            projectPriority="Low",
            assignees=["chris"],
            replanRequest=replan_request(335, disposition="human-required"),
            backlogTransition={
                "id": "PVTE_335_backlog",
                "actor": "chris",
                "createdAt": "2026-07-28T12:00:00Z",
                "status": "Backlog",
                "wasAutomated": False,
            },
        )
        implementation = ticket(
            336,
            projectStatus="In progress",
            projectPriority="Low",
            assignees=["chris"],
        )
        reconciliation = wayfinder_ticket(
            337,
            assignees=["chris"],
            state="CLOSED",
            projectStatus="Done",
            projectPriority="Critical",
            wayfinderReconciliation=wayfinder_reconciliation(337),
        )

        returncode, output = run_ranker(
            [reconciliation, implementation, cleanup],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            [
                "resume-backlog-cleanup",
                "resume-implementation",
                "resume-wayfinder-reconciliation",
            ],
            [entry["action"] for entry in output["claims"]],
        )

    def test_rejects_a_wayfinder_reconciliation_for_another_project_item(self) -> None:
        interrupted = wayfinder_ticket(
            323,
            assignees=["chris"],
            state="CLOSED",
            projectStatus="Done",
            wayfinderReconciliation=wayfinder_reconciliation(
                323,
                projectItemId="PVTI_other",
            ),
        )

        returncode, output = run_ranker(
            [interrupted],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 323,
                    "reasons": [
                        "ticket 323: Wayfinder reconciliation Project item changed",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )

    def test_accepts_an_out_of_scope_wayfinder_reconciliation(self) -> None:
        interrupted = wayfinder_ticket(
            330,
            assignees=["chris"],
            wayfinderReconciliation=wayfinder_reconciliation(
                330,
                disposition="out-of-scope",
            ),
        )

        returncode, output = run_ranker(
            [interrupted],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual(
            "resume-wayfinder-reconciliation",
            output["claims"][0]["action"],
        )

    def test_rejects_an_unknown_wayfinder_reconciliation_disposition(self) -> None:
        interrupted = wayfinder_ticket(
            333,
            assignees=["chris"],
            wayfinderReconciliation=wayfinder_reconciliation(
                333,
                disposition="invalid",
            ),
        )

        returncode, output = run_ranker(
            [interrupted],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertIn(
            "wayfinderReconciliation.disposition must be 'resolved' or 'out-of-scope'",
            output["blockedPlanningClaims"][0]["reasons"][0],
        )

    def test_blocks_a_wayfinder_reconciliation_from_stale_configuration(self) -> None:
        interrupted = wayfinder_ticket(
            334,
            assignees=["chris"],
            state="CLOSED",
            projectStatus="Done",
            wayfinderReconciliation=wayfinder_reconciliation(
                334,
                configurationDigest="sha256:stale-config",
            ),
        )

        returncode, output = run_ranker(
            [interrupted],
            *DEFAULT_WAYFINDER_ARGUMENTS,
        )

        self.assertEqual(0, returncode)
        self.assertEqual([], output["claims"])
        self.assertEqual(
            [
                {
                    "number": 334,
                    "reasons": [
                        "ticket 334: Wayfinder reconciliation configuration changed",
                    ],
                },
            ],
            output["blockedPlanningClaims"],
        )


if __name__ == "__main__":
    unittest.main()
