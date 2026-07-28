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
        "--ready-approver",
        action="append",
        dest="ready_approvers",
        required=True,
        help="GitHub login allowed to approve Ready transitions. Repeat as needed.",
    )
    parser.add_argument(
        "--ready-status",
        default="Ready for agent",
        help="Configured GitHub Project status value that marks an item ready.",
    )
    parser.add_argument(
        "--in-progress-status",
        default="In progress",
        help="Configured GitHub Project status value that marks an item active.",
    )
    parser.add_argument(
        "--priority",
        action="append",
        dest="priorities",
        required=True,
        help="GitHub Project priority value in descending order. Repeat for each rank.",
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
        "assignees",
        "blockedBy",
        "openDescendants",
        "openPullRequests",
        "readyTransition",
        "agentBrief",
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


def analyze_ticket(
    ticket: dict[str, Any],
    *,
    current_user: str,
    ready_status: str,
    in_progress_status: str,
    priorities: tuple[str, ...],
    repository: str,
    base_branch: str,
    ready_approvers: tuple[str, ...],
) -> dict[str, Any]:
    number = ticket["number"]
    assignees = assignee_values(ticket["assignees"], number)
    blockers = string_values(ticket["blockedBy"], "blockedBy", number)
    open_descendants = string_values(
        ticket["openDescendants"],
        "openDescendants",
        number,
    )
    pull_requests = pull_request_values(ticket["openPullRequests"], number)
    project_position = parse_project_position(ticket["projectPosition"], number)

    errors: list[str] = []
    exclusions: list[str] = []

    ready_transition = ticket["readyTransition"]
    if not isinstance(ready_transition, dict):
        raise InputError(f"ticket {number}: readyTransition must be an object")
    nonempty_string(
        ready_transition.get("id"),
        "readyTransition.id",
        number,
    )
    transition_actor = nonempty_string(
        ready_transition.get("actor"),
        "readyTransition.actor",
        number,
    )
    transition_created_at = timestamp(
        ready_transition.get("createdAt"),
        "readyTransition.createdAt",
        number,
    )
    transition_status = nonempty_string(
        ready_transition.get("status"),
        "readyTransition.status",
        number,
    )
    transition_was_automated = ready_transition.get("wasAutomated")
    if not isinstance(transition_was_automated, bool):
        raise InputError(
            f"ticket {number}: readyTransition.wasAutomated must be a boolean",
        )

    agent_brief = ticket["agentBrief"]
    if not isinstance(agent_brief, dict):
        raise InputError(f"ticket {number}: agentBrief must be an object")
    nonempty_string(
        agent_brief.get("commentId"),
        "agentBrief.commentId",
        number,
    )
    nonempty_string(
        agent_brief.get("digest"),
        "agentBrief.digest",
        number,
    )
    brief_created_at = timestamp(
        agent_brief.get("createdAt"),
        "agentBrief.createdAt",
        number,
    )
    brief_updated_at = timestamp(
        agent_brief.get("updatedAt"),
        "agentBrief.updatedAt",
        number,
    )
    if brief_updated_at < brief_created_at:
        raise InputError(
            f"ticket {number}: agentBrief.updatedAt precedes agentBrief.createdAt",
        )
    if transition_status != ready_status:
        errors.append(
            f"latest ready transition status {transition_status!r} "
            f"does not match {ready_status!r}",
        )
    if transition_was_automated:
        exclusions.append("ready transition was automated")
    elif transition_actor not in ready_approvers:
        exclusions.append(
            f"ready transition actor {transition_actor!r} is not approved",
        )
    if brief_created_at > transition_created_at:
        exclusions.append("agent brief was posted after ready approval")
    elif brief_updated_at > transition_created_at:
        exclusions.append("agent brief changed after ready approval")

    if str(ticket["state"]).upper() != "OPEN":
        exclusions.append("not open")

    project_status = ticket["projectStatus"]
    if project_status not in (ready_status, in_progress_status):
        errors.append(
            f"expected project status {ready_status!r} or {in_progress_status!r}, "
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
        and not own_pull_requests
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
        ready_approvers = tuple(args.ready_approvers)
        if len(set(ready_approvers)) != len(ready_approvers):
            raise InputError("ready approvers must be unique")
        if not 1 <= args.max_claims <= 3:
            raise InputError("max claims must be between 1 and 3")

        seen_numbers: set[int] = set()
        analyses: list[dict[str, Any]] = []
        invalid_unclaimed: list[dict[str, Any]] = []
        invalid_claimed: list[dict[str, Any]] = []
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
                        ready_status=args.ready_status,
                        in_progress_status=args.in_progress_status,
                        priorities=priorities,
                        repository=args.repository,
                        base_branch=args.base_branch,
                        ready_approvers=ready_approvers,
                    ),
                )
            except InputError as error:
                number = raw_ticket.get("number", "?") if isinstance(raw_ticket, dict) else "?"
                invalid = {
                    "number": number,
                    "reasons": [str(error)],
                }
                if has_current_user_assignment(raw_ticket, args.current_user):
                    invalid_claimed.append(invalid)
                else:
                    invalid_unclaimed.append(invalid)

        blocked_claims = invalid_claimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in analyses
            if item["assignedToCurrentUser"] and (item["errors"] or item["exclusions"])
        ]

        eligible = [
            item for item in analyses if not item["errors"] and not item["exclusions"]
        ]
        claimed = [item for item in eligible if item["assignedToCurrentUser"]]
        claimed.sort(key=ticket_rank)
        claim_numbers = [
            item["ticket"]["number"] for item in claimed
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
                item["resumeAction"] != "resume-pr",
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
                    "action": (
                        "resume-pr"
                        if item["resumeAction"] == "resume-pr"
                        else "claim"
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
