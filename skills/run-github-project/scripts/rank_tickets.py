#!/usr/bin/env python3
"""Validate and rank a normalized live GitHub Project run."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from typing import Any


class InputError(ValueError):
    """Raised when a normalized query violates the queue contract."""


IMPLEMENTATION_ACTIONS = {"resume-pr", "resume-implementation"}
CANDIDATE_ACTION_ORDER = ("resume-pr", "resume-implementation", "plan")
CANDIDATE_OUTPUT_ACTIONS = {"resume-implementation": "claim"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate claims and rank eligible GitHub Project tickets.",
    )
    parser.add_argument(
        "--current-user",
        required=True,
        help="Authenticated GitHub login used to detect resumable claims.",
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="Configured owner/repository targeted by resumable pull requests.",
    )
    parser.add_argument(
        "--base-branch",
        required=True,
        help="Configured base branch targeted by resumable pull requests.",
    )
    parser.add_argument(
        "--execution-approver",
        action="append",
        dest="execution_approvers",
        required=True,
        help="GitHub login allowed to authorize Planning transitions. Repeat as needed.",
    )
    parser.add_argument(
        "--planning-status",
        default="Planning",
        help="Configured GitHub Project status display name that queues planning.",
    )
    parser.add_argument(
        "--ready-status",
        default="Ready to implement",
        help="Configured Project status display name that marks implementation-ready work.",
    )
    parser.add_argument(
        "--in-progress-status",
        default="In progress",
        help="Configured GitHub Project status display name that marks an item active.",
    )
    parser.add_argument(
        "--priority",
        action="append",
        dest="priorities",
        required=True,
        help="Project priority display name in descending order. Repeat for each rank.",
    )
    parser.add_argument(
        "--max-claims",
        type=int,
        default=1,
        help="Maximum current-user claims allowed in this run, from 1 to 3.",
    )
    return parser.parse_args()


def string_values(values: Any, field: str, number: Any) -> list[str]:
    if not isinstance(values, list):
        raise InputError(f"ticket {number}: {field} must be an array")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (str, int))
        or value == ""
        for value in values
    ):
        raise InputError(
            f"ticket {number}: {field} entries must be strings or integers",
        )
    return [str(value) for value in values]


def assignee_values(values: Any, number: Any) -> list[str]:
    if not isinstance(values, list):
        raise InputError(f"ticket {number}: assignees must be an array")
    result: list[str] = []
    for value in values:
        if isinstance(value, str) and value:
            result.append(value)
            continue
        if isinstance(value, dict):
            login = value.get("login")
            if isinstance(login, str) and login:
                result.append(login)
                continue
        raise InputError(
            f"ticket {number}: assignee entries must contain a non-empty login",
        )
    return result


def nonempty_string(value: Any, field: str, number: Any) -> str:
    if not isinstance(value, str) or not value:
        raise InputError(f"ticket {number}: {field} must be a non-empty string")
    return value


def timestamp(value: Any, field: str, number: Any) -> datetime:
    text = nonempty_string(value, field, number)
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise InputError(
            f"ticket {number}: {field} must be an ISO 8601 timestamp",
        ) from error
    if result.tzinfo is None:
        raise InputError(f"ticket {number}: {field} must include a timezone")
    return result


def pull_request_values(values: Any, number: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise InputError(f"ticket {number}: openPullRequests must be an array")
    result: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            raise InputError(
                f"ticket {number}: openPullRequests entries must be objects",
            )
        pr_number = value.get("number")
        if (
            not isinstance(pr_number, int)
            or isinstance(pr_number, bool)
            or pr_number <= 0
        ):
            raise InputError(
                f"ticket {number}: pull request number must be a positive integer",
            )
        for field in (
            "url",
            "author",
            "headRepository",
            "headRefName",
            "headSha",
            "baseRepository",
            "baseRefName",
        ):
            nonempty_string(value.get(field), f"pull request {field}", number)
        if not isinstance(value.get("closesIssue"), bool):
            raise InputError(
                f"ticket {number}: pull request closesIssue must be a boolean",
            )
        if not isinstance(value.get("isDraft"), bool):
            raise InputError(
                f"ticket {number}: pull request isDraft must be a boolean",
            )
        result.append(value)
    return result


def parse_project_position(value: Any, number: Any) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InputError(f"ticket {number}: projectPosition must be a non-negative number")
    if not math.isfinite(value):
        raise InputError(f"ticket {number}: projectPosition must be finite")
    if value < 0:
        raise InputError(f"ticket {number}: projectPosition must be a non-negative number")
    return float(value)


def require_ticket_shape(ticket: Any) -> dict[str, Any]:
    if not isinstance(ticket, dict):
        raise InputError(f"ticket entry must be an object, got {ticket!r}")
    required = {
        "number",
        "title",
        "url",
        "state",
        "projectItemId",
        "projectStatus",
        "projectPriority",
        "projectPosition",
        "labels",
        "assignees",
        "blockedBy",
        "openDescendants",
        "openPullRequests",
        "planningTransition",
        "readyTransition",
        "implementationPlan",
    }
    missing = sorted(required - ticket.keys())
    if missing:
        raise InputError(f"ticket {ticket.get('number', '?')}: missing {', '.join(missing)}")
    number = ticket["number"]
    if not isinstance(number, int) or isinstance(number, bool):
        raise InputError(f"ticket {number!r}: number must be an integer")
    if not isinstance(ticket["title"], str) or not isinstance(ticket["url"], str):
        raise InputError(f"ticket {number}: title and url must be strings")
    if not isinstance(ticket["projectItemId"], str) or not ticket["projectItemId"]:
        raise InputError(f"ticket {number}: projectItemId must be a non-empty string")
    if not isinstance(ticket["projectStatus"], str) or not ticket["projectStatus"]:
        raise InputError(f"ticket {number}: projectStatus must be a non-empty string")
    project_priority = ticket["projectPriority"]
    if project_priority is not None and (
        not isinstance(project_priority, str) or not project_priority
    ):
        raise InputError(f"ticket {number}: projectPriority must be a string or null")
    return ticket


def has_current_user_assignment(ticket: Any, current_user: str) -> bool:
    if not isinstance(ticket, dict):
        return False
    assignees = ticket.get("assignees")
    if not isinstance(assignees, list):
        return False
    return any(
        assignee == current_user
        or isinstance(assignee, dict)
        and assignee.get("login") == current_user
        for assignee in assignees
    )


def parse_transition(value: Any, field: str, number: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"ticket {number}: {field} must be an object")
    result = {
        "id": nonempty_string(value.get("id"), f"{field}.id", number),
        "actor": nonempty_string(value.get("actor"), f"{field}.actor", number),
        "createdAt": timestamp(value.get("createdAt"), f"{field}.createdAt", number),
        "status": nonempty_string(value.get("status"), f"{field}.status", number),
        "wasAutomated": value.get("wasAutomated"),
    }
    if not isinstance(result["wasAutomated"], bool):
        raise InputError(
            f"ticket {number}: {field}.wasAutomated must be a boolean",
        )
    return result


def analyze_ticket(
    ticket: dict[str, Any],
    *,
    current_user: str,
    planning_status: str,
    ready_status: str,
    in_progress_status: str,
    priorities: tuple[str, ...],
    repository: str,
    base_branch: str,
    execution_approvers: tuple[str, ...],
) -> dict[str, Any]:
    number = ticket["number"]
    assignees = assignee_values(ticket["assignees"], number)
    labels = string_values(ticket["labels"], "labels", number)
    blockers = string_values(ticket["blockedBy"], "blockedBy", number)
    open_descendants = string_values(
        ticket["openDescendants"],
        "openDescendants",
        number,
    )
    pull_requests = pull_request_values(ticket["openPullRequests"], number)
    project_position = parse_project_position(ticket["projectPosition"], number)
    project_status = ticket["projectStatus"]

    errors: list[str] = []
    exclusions: list[str] = []
    if "ready-for-agent" not in labels:
        exclusions.append("missing ready-for-agent label")

    planning_transition = parse_transition(
        ticket["planningTransition"],
        "planningTransition",
        number,
    )
    if planning_transition["status"] != planning_status:
        errors.append(
            f"latest planning transition status {planning_transition['status']!r} "
            f"does not match {planning_status!r}",
        )
    planning_actor_is_approver = (
        not planning_transition["wasAutomated"]
        and planning_transition["actor"] in execution_approvers
    )
    planning_actor_is_runner = (
        not planning_transition["wasAutomated"]
        and planning_transition["actor"] == current_user
    )
    if planning_transition["wasAutomated"]:
        exclusions.append("planning transition was automated")
    elif not planning_actor_is_approver and not planning_actor_is_runner:
        exclusions.append(
            "planning transition actor "
            f"{planning_transition['actor']!r} is not approved",
        )

    implementation_plan = ticket["implementationPlan"]
    plan_is_usable = False
    plan_is_current_in_planning = False
    plan_updated_at: datetime | None = None
    if implementation_plan is not None:
        if not isinstance(implementation_plan, dict):
            raise InputError(
                f"ticket {number}: implementationPlan must be an object or null",
            )
        for field in (
            "commentId",
            "permalink",
            "author",
            "digest",
            "plannedBranch",
            "plannedSha",
        ):
            nonempty_string(
                implementation_plan.get(field),
                f"implementationPlan.{field}",
                number,
            )
        plan_created_at = timestamp(
            implementation_plan.get("createdAt"),
            "implementationPlan.createdAt",
            number,
        )
        plan_updated_at = timestamp(
            implementation_plan.get("updatedAt"),
            "implementationPlan.updatedAt",
            number,
        )
        if plan_updated_at < plan_created_at:
            raise InputError(
                f"ticket {number}: implementationPlan.updatedAt "
                "precedes implementationPlan.createdAt",
            )
        plan_targets_base = implementation_plan["plannedBranch"] == base_branch
        plan_authored_by_runner = implementation_plan["author"] == current_user
        if not plan_targets_base and project_status != planning_status:
            exclusions.append(
                "implementation plan targets "
                f"{implementation_plan['plannedBranch']!r}, expected {base_branch!r}",
            )
        if not plan_authored_by_runner:
            exclusions.append(
                "implementation plan author "
                f"{implementation_plan['author']!r} does not match "
                f"current user {current_user!r}",
            )
        plan_is_usable = (
            plan_targets_base
            and plan_authored_by_runner
        )
        plan_is_current_in_planning = (
            plan_updated_at >= planning_transition["createdAt"]
            and plan_is_usable
        )

    valid_ready_handoff = False
    ready_transition = (
        parse_transition(ticket["readyTransition"], "readyTransition", number)
        if ticket["readyTransition"] is not None
        else None
    )
    if project_status != planning_status and ready_transition is None:
        raise InputError(f"ticket {number}: readyTransition must be an object")

    ready_has_runner_provenance = (
        ready_transition is not None
        and ready_transition["status"] == ready_status
        and not ready_transition["wasAutomated"]
        and ready_transition["actor"] == current_user
    )
    ready_follows_plan = (
        ready_transition is not None
        and plan_updated_at is not None
        and ready_transition["createdAt"] >= plan_updated_at
    )
    valid_prior_ready_handoff = (
        ready_has_runner_provenance
        and ready_follows_plan
        and plan_is_usable
        and ready_transition["createdAt"] < planning_transition["createdAt"]
    )
    planning_is_runner_requeue = (
        project_status == planning_status
        and planning_actor_is_runner
        and valid_prior_ready_handoff
    )
    planning_is_human_authority = (
        planning_actor_is_approver
        and not planning_is_runner_requeue
    )
    if (
        project_status != planning_status
        and planning_actor_is_runner
        and not planning_actor_is_approver
    ):
        exclusions.append(
            "planning transition actor "
            f"{planning_transition['actor']!r} is not approved",
        )
    if (
        project_status == planning_status
        and planning_actor_is_runner
        and not planning_is_runner_requeue
        and not planning_is_human_authority
    ):
        exclusions.append(
            "runner Planning requeue lacks a verified prior Ready handoff",
        )
    if planning_is_runner_requeue:
        plan_is_current_in_planning = False

    if project_status != planning_status and ready_transition is not None:
        if ready_transition["status"] != ready_status:
            errors.append(
                f"latest ready transition status {ready_transition['status']!r} "
                f"does not match {ready_status!r}",
            )
        if ready_transition["wasAutomated"]:
            exclusions.append("ready transition came from Project workflow automation")
        elif ready_transition["actor"] != current_user:
            exclusions.append(
                f"ready transition actor {ready_transition['actor']!r} "
                f"does not match current user {current_user!r}",
            )
        if plan_updated_at is None:
            exclusions.append("missing current implementation plan")
        elif plan_is_usable:
            if ready_transition["createdAt"] < plan_updated_at:
                exclusions.append(
                    "ready transition predates the current implementation plan",
                )
            elif ready_transition["createdAt"] < planning_transition["createdAt"]:
                exclusions.append(
                    "ready transition predates the latest planning authorization",
                )
            else:
                valid_ready_handoff = ready_has_runner_provenance

    if str(ticket["state"]).upper() != "OPEN":
        exclusions.append("not open")

    if project_status not in (planning_status, ready_status, in_progress_status):
        errors.append(
            "expected project status "
            f"{planning_status!r}, {ready_status!r}, or {in_progress_status!r}, "
            f"found {project_status!r}",
        )

    project_priority = ticket["projectPriority"]
    if project_priority is not None and project_priority not in priorities:
        errors.append(f"unknown project priority {project_priority!r}")
    priority_rank = (
        priorities.index(project_priority)
        if project_priority is not None and project_priority in priorities
        else len(priorities)
    )

    if blockers:
        exclusions.append(f"blocked by {blockers}")
    if open_descendants:
        exclusions.append(f"open descendants {open_descendants}")

    assigned_to_current_user = current_user in assignees
    other_assignees = [assignee for assignee in assignees if assignee != current_user]
    if other_assignees:
        exclusions.append(f"assigned to {other_assignees}")
    if project_status == in_progress_status and not assignees:
        exclusions.append("in progress without an assignee")

    own_pull_requests = [
        pull_request for pull_request in pull_requests
        if pull_request["author"] == current_user
    ]
    own_closing_pull_requests = [
        pull_request for pull_request in own_pull_requests
        if pull_request["closesIssue"]
    ]
    wrong_target_pull_requests = [
        pull_request for pull_request in own_closing_pull_requests
        if (
            pull_request["baseRepository"] != repository
            or pull_request["baseRefName"] != base_branch
        )
    ]
    resumable_pull_requests = [
        pull_request for pull_request in own_closing_pull_requests
        if (
            pull_request["baseRepository"] == repository
            and pull_request["baseRefName"] == base_branch
        )
    ]
    own_nonclosing_pull_requests = [
        pull_request for pull_request in own_pull_requests
        if not pull_request["closesIssue"]
    ]
    other_pull_requests = [
        pull_request for pull_request in pull_requests
        if pull_request["author"] != current_user
    ]
    if (
        assigned_to_current_user
        and project_status == ready_status
        and not valid_ready_handoff
    ):
        errors.append(
            "assigned to current user while project status is still ready",
        )
    if other_pull_requests:
        exclusions.append(
            "has implementation PRs by other users "
            f"{[pull_request['url'] for pull_request in other_pull_requests]}",
        )
    for pull_request in own_nonclosing_pull_requests:
        exclusions.append(
            "current user's PR does not close the issue "
            f"{pull_request['url']}",
        )
    for pull_request in wrong_target_pull_requests:
        exclusions.append(
            "current user's PR targets "
            f"{pull_request['baseRepository']}:{pull_request['baseRefName']}, "
            f"expected {repository}:{base_branch}",
        )
    if len(pull_requests) > 1:
        errors.append(
            "multiple open implementation PRs "
            f"{[pull_request['url'] for pull_request in pull_requests]}",
        )

    if project_status == planning_status:
        action = (
            "resume-planning-handoff"
            if assigned_to_current_user and plan_is_current_in_planning
            else ("resume-planning" if assigned_to_current_user else "plan")
        )
    elif (
        project_status == ready_status
        and assigned_to_current_user
        and valid_ready_handoff
    ):
        action = "resume-planning-handoff"
    else:
        action = "resume-pr" if resumable_pull_requests else "resume-implementation"
    return {
        "ticket": ticket,
        "priorityRank": priority_rank,
        "projectPosition": project_position,
        "assignedToCurrentUser": assigned_to_current_user,
        "resumeAction": action,
        "errors": errors,
        "exclusions": exclusions,
    }


def ticket_rank(item: dict[str, Any]) -> tuple[int, float, int]:
    return (
        item["priorityRank"],
        item["projectPosition"],
        item["ticket"]["number"],
    )


def main() -> int:
    args = parse_args()
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, list):
            raise InputError("input must be a JSON array")

        priorities = tuple(args.priorities)
        if len(set(priorities)) != len(priorities):
            raise InputError("project priorities must be unique")
        execution_approvers = tuple(args.execution_approvers)
        if len(set(execution_approvers)) != len(execution_approvers):
            raise InputError("execution approvers must be unique")
        if not 1 <= args.max_claims <= 3:
            raise InputError("max claims must be between 1 and 3")

        seen_numbers: set[int] = set()
        analyses: list[dict[str, Any]] = []
        invalid_unclaimed: list[dict[str, Any]] = []
        invalid_claimed: list[dict[str, Any]] = []
        invalid_planning_claimed: list[dict[str, Any]] = []
        for raw_ticket in payload:
            try:
                ticket = require_ticket_shape(raw_ticket)
                if ticket["number"] in seen_numbers:
                    raise InputError(f"duplicate ticket number {ticket['number']}")
                seen_numbers.add(ticket["number"])
                analyses.append(
                    analyze_ticket(
                        ticket,
                        current_user=args.current_user,
                        planning_status=args.planning_status,
                        ready_status=args.ready_status,
                        in_progress_status=args.in_progress_status,
                        priorities=priorities,
                        repository=args.repository,
                        base_branch=args.base_branch,
                        execution_approvers=execution_approvers,
                    ),
                )
            except InputError as error:
                number = raw_ticket.get("number", "?") if isinstance(raw_ticket, dict) else "?"
                invalid = {
                    "number": number,
                    "reasons": [str(error)],
                }
                if has_current_user_assignment(raw_ticket, args.current_user):
                    if (
                        isinstance(raw_ticket, dict)
                        and raw_ticket.get("projectStatus")
                        in (args.planning_status, args.ready_status)
                    ):
                        invalid_planning_claimed.append(invalid)
                    else:
                        invalid_claimed.append(invalid)
                else:
                    invalid_unclaimed.append(invalid)

        blocked_claims = invalid_claimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in analyses
            if (
                item["assignedToCurrentUser"]
                and item["ticket"]["projectStatus"] == args.in_progress_status
                and (item["errors"] or item["exclusions"])
            )
        ]
        blocked_planning_claims = invalid_planning_claimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in analyses
            if (
                item["assignedToCurrentUser"]
                and item["ticket"]["projectStatus"]
                in (args.planning_status, args.ready_status)
                and (item["errors"] or item["exclusions"])
            )
        ]

        eligible = [
            item for item in analyses if not item["errors"] and not item["exclusions"]
        ]
        claimed = [item for item in eligible if item["assignedToCurrentUser"]]
        claimed.sort(
            key=lambda item: (
                item["resumeAction"] not in IMPLEMENTATION_ACTIONS,
                *ticket_rank(item),
            ),
        )
        claim_numbers = [
            item["ticket"]["number"]
            for item in claimed
            if item["resumeAction"] in IMPLEMENTATION_ACTIONS
        ] + [
            item["number"] for item in blocked_claims
        ]
        claim_numbers.sort(
            key=lambda number: (
                (0, number)
                if isinstance(number, int) and not isinstance(number, bool)
                else (1, str(number))
            ),
        )
        if len(claim_numbers) > args.max_claims:
            print(
                json.dumps(
                    {
                        "reason": "over-capacity-claims",
                        "claimLimit": args.max_claims,
                        "claimed": claim_numbers,
                    },
                    indent=2,
                    sort_keys=True,
                ),
            )
            return 2

        candidates = sorted(
            (item for item in eligible if not item["assignedToCurrentUser"]),
            key=lambda item: (
                CANDIDATE_ACTION_ORDER.index(item["resumeAction"]),
                *ticket_rank(item),
            ),
        )

        excluded = invalid_unclaimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in analyses
            if (
                not item["assignedToCurrentUser"]
                and (item["errors"] or item["exclusions"])
            )
        ]
        output = {
            "claimLimit": args.max_claims,
            "blockedClaims": blocked_claims,
            "blockedPlanningClaims": blocked_planning_claims,
            "claims": [
                {
                    "ticket": item["ticket"],
                    "action": item["resumeAction"],
                }
                for item in claimed
            ],
            "candidates": [
                {
                    "ticket": item["ticket"],
                    "action": CANDIDATE_OUTPUT_ACTIONS.get(
                        item["resumeAction"],
                        item["resumeAction"],
                    ),
                }
                for item in candidates
            ],
            "excluded": excluded,
        }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (InputError, json.JSONDecodeError) as error:
        print(json.dumps({"reason": "invalid-input", "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
