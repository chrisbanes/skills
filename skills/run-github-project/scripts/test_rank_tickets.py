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
    "--ready-approver",
    "maintainer",
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
        "assignees": [],
        "blockedBy": [],
        "openDescendants": [],
        "openPullRequests": [],
        "readyTransition": {
            "id": f"PVTE_{number}",
            "actor": "maintainer",
            "createdAt": "2026-07-28T10:00:00Z",
            "status": "Ready",
            "wasAutomated": False,
        },
        "agentBrief": {
            "commentId": f"IC_{number}",
            "digest": f"sha256:brief-{number}",
            "createdAt": "2026-07-28T09:00:00Z",
            "updatedAt": "2026-07-28T09:00:00Z",
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


class RankTicketsTest(unittest.TestCase):
    def test_resumes_current_users_in_progress_item_before_ready_work(self) -> None:
        ready = ticket(1, title="Critical ready work", projectPriority="Critical")
        in_progress = ticket(
            2,
            title="Resume this first",
            projectStatus="In progress",
            projectPriority="Low",
            projectPosition=99,
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [ready, in_progress],
            "--ready-status",
            "Ready",
            "--in-progress-status",
            "In progress",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(2, output["selected"]["number"])
        self.assertEqual("resume-implementation", output["reason"])

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
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(5, output["selected"]["number"])

        returncode, output = run_ranker(
            [later_on_board, earlier_on_board],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(4, output["selected"]["number"])

    def test_does_not_require_issue_category_labels(self) -> None:
        maintenance = ticket(
            6,
            title="Update build infrastructure",
            projectPriority="Medium",
            projectPosition=1,
        )

        returncode, output = run_ranker(
            [maintenance],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(6, output["selected"]["number"])

    def test_open_descendants_make_a_parent_ineligible(self) -> None:
        parent = ticket(
            10,
            title="Umbrella issue",
            projectPriority="Critical",
            projectPosition=1,
            openDescendants=[11, 12],
        )
        child = ticket(11, title="Executable child", projectPosition=2)

        returncode, output = run_ranker(
            [parent, child],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(11, output["selected"]["number"])
        self.assertEqual(
            [{"number": 10, "reasons": ["open descendants ['11', '12']"]}],
            output["excluded"],
        )

    def test_invalid_unclaimed_item_does_not_stop_other_ready_work(self) -> None:
        invalid = ticket(
            20,
            title="Unknown priority",
            projectPriority="Emergency",
            projectPosition=1,
        )
        valid = ticket(
            21,
            title="Valid ready work",
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker(
            [invalid, valid],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(21, output["selected"]["number"])
        self.assertEqual(
            [{"number": 20, "reasons": ["unknown project priority 'Emergency'"]}],
            output["excluded"],
        )

    def test_resumes_current_users_unambiguous_existing_pr(self) -> None:
        issue = ticket(
            30,
            title="PR exists but assignment was missed",
            projectPriority="Low",
            projectPosition=50,
            openPullRequests=[
                pull_request(300),
            ],
        )
        new_work = ticket(
            31,
            title="Higher-priority unstarted work",
            projectPriority="Critical",
            projectPosition=1,
        )

        returncode, output = run_ranker(
            [new_work, issue],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(30, output["selected"]["number"])
        self.assertEqual("resume-pr", output["reason"])

    def test_unassigned_in_progress_item_is_stale_not_claimable(self) -> None:
        stale = ticket(
            40,
            title="Stale active item",
            projectStatus="In progress",
            projectPriority="Critical",
            projectPosition=1,
        )
        ready = ticket(
            41,
            title="Claimable ready item",
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker(
            [stale, ready],
            "--ready-status",
            "Ready",
            "--in-progress-status",
            "In progress",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(41, output["selected"]["number"])
        self.assertEqual(
            [{"number": 40, "reasons": ["in progress without an assignee"]}],
            output["excluded"],
        )

    def test_current_users_assignment_without_in_progress_or_pr_stops(self) -> None:
        partial_claim = ticket(
            50,
            title="Assignment succeeded but status did not",
            projectPosition=1,
            assignees=["chris"],
        )

        returncode, output = run_ranker(
            [partial_claim],
            "--ready-status",
            "Ready",
            "--in-progress-status",
            "In progress",
        )

        self.assertEqual(2, returncode)
        self.assertEqual("claimed-item-ineligible", output["reason"])
        self.assertEqual(
            [
                {
                    "number": 50,
                    "reasons": [
                        "assigned to current user while project status is still ready",
                    ],
                },
            ],
            output["claimedButIneligible"],
        )

    def test_does_not_resume_own_pr_that_does_not_close_issue(self) -> None:
        unrelated_pr = ticket(
            60,
            title="PR is linked but not closing",
            projectPriority="Critical",
            projectPosition=1,
            openPullRequests=[
                pull_request(600, closesIssue=False),
            ],
        )
        valid = ticket(
            61,
            title="Actually claimable work",
            projectPriority="Low",
            projectPosition=2,
        )

        returncode, output = run_ranker(
            [unrelated_pr, valid],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(61, output["selected"]["number"])
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
            "title": "Missing normalized fields",
            "assignees": [],
        }
        valid = ticket(
            71,
            title="Valid work survives malformed neighbor",
            projectPosition=1,
        )

        returncode, output = run_ranker(
            [malformed, valid],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(71, output["selected"]["number"])
        self.assertEqual(70, output["excluded"][0]["number"])
        self.assertIn("missing", output["excluded"][0]["reasons"][0])

    def test_unset_priority_ranks_after_configured_priorities(self) -> None:
        unset = ticket(80, projectPriority=None, projectPosition=1)
        low = ticket(81, projectPriority="Low", projectPosition=100)

        returncode, output = run_ranker(
            [unset, low],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(81, output["selected"]["number"])

    def test_malformed_claimed_item_stops(self) -> None:
        malformed_claim = {
            "number": 90,
            "title": "Claimed but missing normalized fields",
            "assignees": [{"login": "chris"}],
        }

        returncode, output = run_ranker(
            [malformed_claim, ticket(91)],
            "--ready-status",
            "Ready",
        )

        self.assertEqual(2, returncode)
        self.assertEqual("claimed-item-ineligible", output["reason"])
        self.assertEqual(90, output["claimedButIneligible"][0]["number"])

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

        returncode, output = run_ranker(
            [claimed],
            "--ready-status",
            "Ready",
            "--in-progress-status",
            "In progress",
        )

        self.assertEqual(0, returncode)
        self.assertEqual(100, output["selected"]["number"])
        self.assertEqual("resume-implementation", output["reason"])

    def test_automated_ready_transition_is_not_approval(self) -> None:
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

        returncode, output = run_ranker([automated, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(111, output["selected"]["number"])
        self.assertEqual(
            [{"number": 110, "reasons": ["ready transition was automated"]}],
            output["excluded"],
        )

    def test_ready_transition_requires_configured_approver(self) -> None:
        unapproved = ticket(
            120,
            readyTransition={
                "id": "PVTE_120",
                "actor": "outsider",
                "createdAt": "2026-07-28T10:00:00Z",
                "status": "Ready",
                "wasAutomated": False,
            },
        )
        valid = ticket(121)

        returncode, output = run_ranker([unapproved, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(121, output["selected"]["number"])
        self.assertEqual(
            [{"number": 120, "reasons": ["ready transition actor 'outsider' is not approved"]}],
            output["excluded"],
        )

    def test_agent_brief_must_not_change_after_ready_approval(self) -> None:
        stale_approval = ticket(
            130,
            agentBrief={
                "commentId": "IC_130",
                "digest": "sha256:brief-130",
                "createdAt": "2026-07-28T09:00:00Z",
                "updatedAt": "2026-07-28T11:00:00Z",
            },
        )
        valid = ticket(131)

        returncode, output = run_ranker([stale_approval, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(131, output["selected"]["number"])
        self.assertEqual(
            [{"number": 130, "reasons": ["agent brief changed after ready approval"]}],
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

        returncode, output = run_ranker([wrong_base, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(141, output["selected"]["number"])
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

        returncode, output = run_ranker([ambiguous, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(151, output["selected"]["number"])
        self.assertEqual(150, output["excluded"][0]["number"])
        self.assertIn("assignee", output["excluded"][0]["reasons"][0])

    def test_non_finite_project_position_is_invalid(self) -> None:
        invalid = ticket(160, projectPosition=float("nan"))
        valid = ticket(161)

        returncode, output = run_ranker([invalid, valid], "--ready-status", "Ready")

        self.assertEqual(0, returncode)
        self.assertEqual(161, output["selected"]["number"])
        self.assertEqual(
            [{"number": 160, "reasons": ["ticket 160: projectPosition must be finite"]}],
            output["excluded"],
        )


if __name__ == "__main__":
    unittest.main()
