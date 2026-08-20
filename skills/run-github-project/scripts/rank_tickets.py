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
AGENT_WORK_LABEL = "ready-for-agent"
CLAIM_ACTION_RANK = {
    "resume-backlog-cleanup": 0,
    "resume-pr": 1,
    "resume-implementation": 1,
    "resume-wayfinder-reconciliation": 2,
}
CANDIDATE_ACTION_RANK = {
    "resume-pr": 0,
    "resume-implementation": 1,
    "plan": 2,
    "wayfind": 2,
}
CANDIDATE_OUTPUT_ACTIONS = {"resume-implementation": "claim"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate claims and rank eligible GitHub Project tickets.",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=("next", "drain"),
        help="Invocation mode; next may select HITL Wayfinder work, drain may not.",
    )
    parser.add_argument(
        "--wayfinder-ticket",
        type=int,
        help="Explicit Wayfinder child number selected by the user in next mode.",
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
        "--configuration-digest",
        required=True,
        help="Digest of the committed Project configuration for recovery leases.",
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
        "--backlog-status",
        default="Backlog",
        help="Configured Project status display name for untriaged or human work.",
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
        "--needs-triage-label",
        default="needs-triage",
        help="Configured issue label that queues an unblocked Backlog item for triage.",
    )
    parser.add_argument(
        "--epic-label",
        required=True,
        help="Configured issue label that identifies a non-implementation parent.",
    )
    parser.add_argument(
        "--human-work-label",
        required=True,
        help="Configured issue label that identifies work a human must perform.",
    )
    parser.add_argument(
        "--wayfinder-map-label",
        help="Configured label for an open Wayfinder map parent.",
    )
    parser.add_argument(
        "--wayfinder-research-label",
        help="Configured label for an AFK Wayfinder research ticket.",
    )
    parser.add_argument(
        "--wayfinder-prototype-label",
        help="Configured label for a HITL Wayfinder prototype ticket.",
    )
    parser.add_argument(
        "--wayfinder-grilling-label",
        help="Configured label for a HITL Wayfinder grilling ticket.",
    )
    parser.add_argument(
        "--wayfinder-task-label",
        help="Configured label for an AFK-or-HITL Wayfinder task ticket.",
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


def configured_wayfinder_labels(args: argparse.Namespace) -> dict[str, str] | None:
    labels = {
        "map": args.wayfinder_map_label,
        "research": args.wayfinder_research_label,
        "prototype": args.wayfinder_prototype_label,
        "grilling": args.wayfinder_grilling_label,
        "task": args.wayfinder_task_label,
    }
    supplied = [name for name, label in labels.items() if label is not None]
    if not supplied:
        return None
    if len(supplied) != len(labels):
        missing = sorted(name for name, label in labels.items() if label is None)
        raise InputError(
            "Wayfinder labels must be configured together; missing "
            + ", ".join(missing),
        )
    if any(not isinstance(label, str) or not label for label in labels.values()):
        raise InputError("Wayfinder labels must be non-empty strings")
    if len(set(labels.values())) != len(labels):
        raise InputError("Wayfinder labels must be unique")
    return labels


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


def pull_request_values(
    values: Any,
    number: Any,
    *,
    require_execution_fields: bool,
) -> list[dict[str, Any]]:
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
        nonempty_string(value.get("url"), "pull request url", number)
        if not isinstance(value.get("closesIssue"), bool):
            raise InputError(
                f"ticket {number}: pull request closesIssue must be a boolean",
            )
        if not require_execution_fields:
            result.append(value)
            continue
        for field in (
            "author",
            "headRepository",
            "headRefName",
            "headSha",
            "baseRepository",
            "baseRefName",
        ):
            nonempty_string(value.get(field), f"pull request {field}", number)
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


def project_priority_rank(
    project_priority: str | None,
    priorities: tuple[str, ...],
) -> tuple[int, str | None]:
    if project_priority is not None and project_priority not in priorities:
        return len(priorities), f"unknown project priority {project_priority!r}"
    return (
        priorities.index(project_priority)
        if project_priority is not None
        else len(priorities)
    ), None


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
    }
    missing = sorted(required - ticket.keys())
    if missing:
        raise InputError(f"ticket {ticket.get('number', '?')}: missing {', '.join(missing)}")
    if "implementationPlan" not in ticket and "implementationPlans" not in ticket:
        raise InputError(
            f"ticket {ticket.get('number', '?')}: missing implementationPlans",
        )
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


def parse_replan_request(value: Any, number: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"ticket {number}: replanRequest must be an object")
    result = {
        field: nonempty_string(
            value.get(field),
            f"replanRequest.{field}",
            number,
        )
        for field in (
            "commentId",
            "permalink",
            "author",
            "disposition",
            "previousPlanPermalink",
            "previousPlanDigest",
            "baseSha",
        )
    }
    result["createdAt"] = timestamp(
        value.get("createdAt"),
        "replanRequest.createdAt",
        number,
    )
    for field in ("implementationHeadSha", "pullRequestUrl"):
        optional = value.get(field)
        if optional is not None and (not isinstance(optional, str) or not optional):
            raise InputError(
                f"ticket {number}: replanRequest.{field} "
                "must be a non-empty string or null",
            )
        result[field] = optional
    if result["disposition"] not in ("autonomous-replan", "human-required"):
        raise InputError(
            f"ticket {number}: replanRequest.disposition must be "
            "'autonomous-replan' or 'human-required'",
        )
    return result


def parse_implementation_plan_chain(
    ticket: dict[str, Any],
    number: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    values = ticket.get("implementationPlans")
    if values is None:
        legacy = ticket.get("implementationPlan")
        if legacy is None:
            return [], None
        if not isinstance(legacy, dict):
            raise InputError(
                f"ticket {number}: implementationPlan must be an object or null",
            )
        values = [
            {
                **legacy,
                "markerVersion": 1,
                "revision": 1,
                "supersedes": None,
                "replanRequest": None,
                "publishedAt": legacy.get("updatedAt"),
                "isMinimized": False,
            },
        ]
    if not isinstance(values, list):
        raise InputError(f"ticket {number}: implementationPlans must be an array")

    plans: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            raise InputError(
                f"ticket {number}: implementationPlans entries must be objects",
            )
        plan = dict(value)
        for field in (
            "commentId",
            "permalink",
            "author",
            "digest",
            "plannedBranch",
            "plannedSha",
        ):
            nonempty_string(plan.get(field), f"implementationPlan.{field}", number)
        created_at = timestamp(
            plan.get("createdAt"),
            "implementationPlan.createdAt",
            number,
        )
        published_at = timestamp(
            plan.get("publishedAt"),
            "implementationPlan.publishedAt",
            number,
        )
        updated_at = timestamp(
            plan.get("updatedAt"),
            "implementationPlan.updatedAt",
            number,
        )
        if published_at < created_at or updated_at < published_at:
            raise InputError(
                f"ticket {number}: implementation plan timestamps are out of order",
            )
        marker_version = plan.get("markerVersion")
        revision = plan.get("revision")
        if marker_version not in (1, 2):
            raise InputError(
                f"ticket {number}: implementationPlan.markerVersion must be 1 or 2",
            )
        if (
            not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision <= 0
        ):
            raise InputError(
                f"ticket {number}: implementationPlan.revision "
                "must be a positive integer",
            )
        for field in ("supersedes", "replanRequest"):
            optional = plan.get(field)
            if optional is not None and (
                not isinstance(optional, str) or not optional
            ):
                raise InputError(
                    f"ticket {number}: implementationPlan.{field} "
                    "must be a non-empty string or null",
                )
        if not isinstance(plan.get("isMinimized"), bool):
            raise InputError(
                f"ticket {number}: implementationPlan.isMinimized "
                "must be a boolean",
            )
        if marker_version == 1 and (
            revision != 1
            or plan.get("supersedes") is not None
            or plan.get("replanRequest") is not None
        ):
            raise InputError(
                f"ticket {number}: a v1 implementation plan must be a revision-one root",
            )
        plans.append(plan)

    if not plans:
        return [], None

    permalinks = [plan["permalink"] for plan in plans]
    comment_ids = [plan["commentId"] for plan in plans]
    revisions = [plan["revision"] for plan in plans]
    if len(set(permalinks)) != len(permalinks):
        raise InputError(f"ticket {number}: duplicate implementation plan permalink")
    if len(set(comment_ids)) != len(comment_ids):
        raise InputError(f"ticket {number}: duplicate implementation plan comment ID")
    if len(set(revisions)) != len(revisions):
        raise InputError(f"ticket {number}: duplicate implementation plan revision")

    chain = sorted(plans, key=lambda plan: plan["revision"])
    if (
        chain[0]["supersedes"] is not None
        or any(plan["supersedes"] is None for plan in chain[1:])
    ):
        raise InputError(
            f"ticket {number}: implementation plan chain must have exactly one root",
        )
    if [plan["revision"] for plan in chain] != list(range(1, len(chain) + 1)):
        raise InputError(
            f"ticket {number}: implementation plan revisions must be contiguous",
        )
    for parent, child in zip(chain, chain[1:]):
        if child["supersedes"] == parent["permalink"]:
            continue
        if child["supersedes"] not in permalinks:
            raise InputError(
                f"ticket {number}: implementation plan revision "
                f"{child['revision']} has a missing predecessor",
            )
        raise InputError(f"ticket {number}: implementation plan chain forks")
    active = chain[-1]
    if active["isMinimized"]:
        raise InputError(
            f"ticket {number}: active implementation plan is minimized",
        )
    return plans, active


def analyze_common_ticket(
    ticket: dict[str, Any],
    priorities: tuple[str, ...],
    *,
    require_execution_pr_fields: bool,
) -> dict[str, Any]:
    number = ticket["number"]
    priority_rank, priority_error = project_priority_rank(
        ticket["projectPriority"],
        priorities,
    )
    return {
        "assignees": assignee_values(ticket["assignees"], number),
        "labels": string_values(ticket["labels"], "labels", number),
        "blockers": string_values(ticket["blockedBy"], "blockedBy", number),
        "openDescendants": string_values(
            ticket["openDescendants"],
            "openDescendants",
            number,
        ),
        "pullRequests": pull_request_values(
            ticket["openPullRequests"],
            number,
            require_execution_fields=require_execution_pr_fields,
        ),
        "projectPosition": parse_project_position(
            ticket["projectPosition"],
            number,
        ),
        "priorityRank": priority_rank,
        "errors": [priority_error] if priority_error is not None else [],
        "exclusions": [],
    }


def analyze_ticket(
    ticket: dict[str, Any],
    *,
    current_user: str,
    backlog_status: str,
    planning_status: str,
    ready_status: str,
    in_progress_status: str,
    priorities: tuple[str, ...],
    repository: str,
    base_branch: str,
    execution_approvers: tuple[str, ...],
) -> dict[str, Any]:
    number = ticket["number"]
    common = analyze_common_ticket(
        ticket,
        priorities,
        require_execution_pr_fields=True,
    )
    assignees = common["assignees"]
    labels = common["labels"]
    blockers = common["blockers"]
    open_descendants = common["openDescendants"]
    pull_requests = common["pullRequests"]
    project_position = common["projectPosition"]
    priority_rank = common["priorityRank"]
    project_status = ticket["projectStatus"]
    assigned_to_current_user = current_user in assignees
    recovering_backlog_cleanup = (
        project_status == backlog_status and assigned_to_current_user
    )

    errors = common["errors"]
    exclusions = common["exclusions"]
    if AGENT_WORK_LABEL not in labels and not recovering_backlog_cleanup:
        exclusions.append(f"missing {AGENT_WORK_LABEL} label")

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

    implementation_plans, implementation_plan = parse_implementation_plan_chain(
        ticket,
        number,
    )
    ticket = {
        **ticket,
        "implementationPlan": implementation_plan,
        "implementationPlans": implementation_plans,
    }
    plan_is_usable = False
    plan_is_current_in_planning = False
    plan_published_at: datetime | None = None
    plan_updated_at: datetime | None = None
    if implementation_plan is not None:
        plan_published_at = timestamp(
            implementation_plan.get("publishedAt"),
            "implementationPlan.publishedAt",
            number,
        )
        plan_updated_at = timestamp(
            implementation_plan.get("updatedAt"),
            "implementationPlan.updatedAt",
            number,
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
            plan_published_at >= planning_transition["createdAt"]
            and plan_is_usable
        )
        foreign_plan_authors = sorted(
            {
                plan["author"]
                for plan in implementation_plans
                if plan["author"] != current_user
            },
        )
        if foreign_plan_authors and plan_authored_by_runner:
            exclusions.append(
                "implementation plan history authors "
                f"{foreign_plan_authors} do not match current user {current_user!r}",
            )

    replan_request = (
        parse_replan_request(ticket.get("replanRequest"), number)
        if ticket.get("replanRequest") is not None
        else None
    )
    backlog_transition = (
        parse_transition(ticket.get("backlogTransition"), "backlogTransition", number)
        if ticket.get("backlogTransition") is not None
        else None
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
    prior_plan = implementation_plan
    if replan_request is not None:
        prior_plan = next(
            (
                plan for plan in implementation_plans
                if (
                    plan["permalink"]
                    == replan_request["previousPlanPermalink"]
                    and plan["digest"] == replan_request["previousPlanDigest"]
                )
            ),
            None,
        )
    prior_plan_published_at = (
        timestamp(
            prior_plan.get("publishedAt"),
            "implementationPlan.publishedAt",
            number,
        )
        if prior_plan is not None
        else None
    )
    prior_plan_is_usable = (
        prior_plan is not None
        and prior_plan["plannedBranch"] == base_branch
        and prior_plan["author"] == current_user
    )
    valid_prior_ready_handoff = (
        ready_has_runner_provenance
        and ready_transition is not None
        and prior_plan_published_at is not None
        and ready_transition["createdAt"] >= prior_plan_published_at
        and prior_plan_is_usable
        and ready_transition["createdAt"] < planning_transition["createdAt"]
    )
    valid_autonomous_replan_report = (
        replan_request is not None
        and prior_plan is not None
        and replan_request["author"] == current_user
        and replan_request["disposition"] == "autonomous-replan"
        and ready_transition is not None
        and replan_request["createdAt"] >= ready_transition["createdAt"]
        and replan_request["createdAt"] <= planning_transition["createdAt"]
    )
    own_pull_requests = [
        pull_request for pull_request in pull_requests
        if pull_request["author"] == current_user
    ]
    own_closing_pull_requests = [
        pull_request for pull_request in own_pull_requests
        if pull_request["closesIssue"]
    ]
    retained_pr_matches_report = (
        replan_request is not None
        and (
            (
                replan_request["pullRequestUrl"] is None
                and not own_closing_pull_requests
            )
            or (
                len(own_closing_pull_requests) == 1
                and replan_request["pullRequestUrl"]
                == own_closing_pull_requests[0]["url"]
                and replan_request["implementationHeadSha"]
                == own_closing_pull_requests[0]["headSha"]
            )
        )
    )
    planning_is_runner_requeue = (
        project_status == planning_status
        and planning_actor_is_runner
        and valid_prior_ready_handoff
        and valid_autonomous_replan_report
        and retained_pr_matches_report
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
        if not valid_prior_ready_handoff:
            exclusions.append(
                "runner Planning requeue lacks a verified prior Ready handoff",
            )
        elif not valid_autonomous_replan_report:
            exclusions.append(
                "runner Planning requeue lacks a verified replan report",
            )
        elif not retained_pr_matches_report:
            exclusions.append(
                "runner Planning requeue lacks verified retained PR evidence",
            )
    if (
        planning_is_runner_requeue
        and plan_is_current_in_planning
        and implementation_plan is not None
        and prior_plan is not None
    ):
        replan_revisions = [
            plan for plan in implementation_plans
            if plan["revision"] > prior_plan["revision"]
        ]
        if (
            not replan_revisions
            or any(
                plan["replanRequest"] != replan_request["permalink"]
                for plan in replan_revisions
            )
        ):
            exclusions.append(
                "active plan revision does not link the verified replan report",
            )
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

    if (
        str(ticket["state"]).upper() != "OPEN"
        and not recovering_backlog_cleanup
    ):
        exclusions.append("not open")

    if project_status not in (
        backlog_status,
        planning_status,
        ready_status,
        in_progress_status,
    ):
        errors.append(
            "expected project status "
            f"{backlog_status!r}, {planning_status!r}, {ready_status!r}, "
            f"or {in_progress_status!r}, "
            f"found {project_status!r}",
        )

    if blockers and not recovering_backlog_cleanup:
        exclusions.append(f"blocked by {blockers}")
    if open_descendants and not recovering_backlog_cleanup:
        exclusions.append(f"open descendants {open_descendants}")

    other_assignees = [assignee for assignee in assignees if assignee != current_user]
    if other_assignees:
        exclusions.append(f"assigned to {other_assignees}")
    if project_status == in_progress_status and not assignees:
        exclusions.append("in progress without an assignee")
    if project_status == backlog_status:
        if backlog_transition is None:
            exclusions.append("missing verified Backlog transition")
        elif backlog_transition["status"] != backlog_status:
            errors.append(
                f"latest backlog transition status {backlog_transition['status']!r} "
                f"does not match {backlog_status!r}",
            )
        elif (
            backlog_transition["wasAutomated"]
            or backlog_transition["actor"] != current_user
        ):
            exclusions.append(
                "Backlog transition lacks current-runner provenance",
            )
        if replan_request is None:
            exclusions.append("missing verified human-work report")
        else:
            if replan_request["author"] != current_user:
                exclusions.append(
                    "human-work report author "
                    f"{replan_request['author']!r} does not match "
                    f"current user {current_user!r}",
                )
            if replan_request["disposition"] != "human-required":
                exclusions.append(
                    "Backlog replan report is not marked human-required",
                )
            if implementation_plan is not None and (
                replan_request["previousPlanPermalink"]
                != implementation_plan["permalink"]
                or replan_request["previousPlanDigest"]
                != implementation_plan["digest"]
            ):
                exclusions.append(
                    "human-work report does not identify the current plan",
                )
            if (
                backlog_transition is not None
                and backlog_transition["createdAt"] < replan_request["createdAt"]
            ):
                exclusions.append(
                    "Backlog transition predates the human-work report",
                )
        if not assigned_to_current_user:
            exclusions.append("human work required in Backlog")

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

    if project_status == backlog_status and assigned_to_current_user:
        action = "resume-backlog-cleanup"
    elif project_status == planning_status:
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


def analyze_backlog_ticket(
    ticket: dict[str, Any],
    *,
    needs_triage_label: str,
    epic_label: str,
    human_work_label: str,
    priorities: tuple[str, ...],
) -> dict[str, Any]:
    common = analyze_common_ticket(
        ticket,
        priorities,
        require_execution_pr_fields=False,
    )
    assignees = common["assignees"]
    labels = common["labels"]
    blockers = common["blockers"]
    open_descendants = common["openDescendants"]
    pull_requests = common["pullRequests"]
    project_position = common["projectPosition"]
    priority_rank = common["priorityRank"]

    errors = common["errors"]
    exclusions = common["exclusions"]
    blocker_reasons: list[str] = []
    if str(ticket["state"]).upper() != "OPEN":
        exclusions.append("not open")
    is_epic = epic_label in labels
    is_agent_work = AGENT_WORK_LABEL in labels
    is_human_work = human_work_label in labels
    needs_triage = needs_triage_label in labels
    action_roles = [is_agent_work, is_human_work, needs_triage]
    if sum(action_roles) > 1:
        exclusions.append("conflicting Backlog action labels")
    if is_epic and is_agent_work:
        exclusions.append("epic cannot be ready for agent implementation")

    role: str | None = None
    action: str | None = None
    if not exclusions:
        if is_human_work:
            role = "human-epic" if is_epic else "human"
            action = "perform-human-work"
        elif needs_triage:
            role = "triage"
            action = "triage"
        elif is_agent_work:
            role = "agent"
            action = "move-to-planning"
        elif is_epic:
            role = "epic"
            action = "close-epic"
        else:
            exclusions.append("unclassified Backlog work")

    if assignees and role not in ("human", "human-epic"):
        exclusions.append(f"assigned to {assignees}")
    if pull_requests and role not in ("human", "human-epic"):
        exclusions.append(
            "has open implementation PRs "
            f"{[pull_request['url'] for pull_request in pull_requests]}",
        )
    if blockers:
        blocker_reasons.append(f"blocked by {blockers}")
    if open_descendants:
        blocker_reasons.append(f"open descendants {open_descendants}")

    return {
        "ticket": ticket,
        "priorityRank": priority_rank,
        "projectPosition": project_position,
        "role": role,
        "action": action,
        "blockerReasons": blocker_reasons,
        "errors": errors,
        "exclusions": exclusions,
    }


def parse_wayfinder_parent(
    ticket: dict[str, Any],
    *,
    map_label: str,
    allow_closed: bool = False,
) -> int:
    number = ticket["number"]
    parent = ticket.get("parentIssue")
    if not isinstance(parent, dict):
        raise InputError(f"ticket {number}: missing Wayfinder map parent")
    parent_number = parent.get("number")
    if (
        not isinstance(parent_number, int)
        or isinstance(parent_number, bool)
        or parent_number <= 0
    ):
        raise InputError(f"ticket {number}: parent issue number must be a positive integer")
    parent_state = parent.get("state")
    parent_labels = string_values(
        parent.get("labels"),
        "parentIssue.labels",
        number,
    )
    accepted_states = {"OPEN", "CLOSED"} if allow_closed else {"OPEN"}
    if (
        str(parent_state).upper() not in accepted_states
        or map_label not in parent_labels
    ):
        raise InputError("parent is not an open Wayfinder map")
    return parent_number


def parse_wayfinder_reconciliation(
    value: Any,
    *,
    number: int,
    current_user: str,
    project_item_id: str,
    configuration_digest: str,
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise InputError(
            f"ticket {number}: wayfinderReconciliation must be an object or null",
        )
    marker_version = value.get("markerVersion")
    if marker_version != 1 or isinstance(marker_version, bool):
        raise InputError(
            f"ticket {number}: wayfinderReconciliation.markerVersion must be 1",
        )
    result = {
        field: nonempty_string(
            value.get(field),
            f"wayfinderReconciliation.{field}",
            number,
        )
        for field in (
            "commentId",
            "permalink",
            "author",
            "disposition",
            "projectItemId",
            "outcomePermalink",
            "configurationDigest",
            "planDigest",
        )
    }
    result["markerVersion"] = marker_version
    result["createdAt"] = timestamp(
        value.get("createdAt"),
        "wayfinderReconciliation.createdAt",
        number,
    )
    map_number = value.get("mapNumber")
    if (
        not isinstance(map_number, int)
        or isinstance(map_number, bool)
        or map_number <= 0
    ):
        raise InputError(
            f"ticket {number}: wayfinderReconciliation.mapNumber "
            "must be a positive integer",
        )
    result["mapNumber"] = map_number
    if result["disposition"] not in ("resolved", "out-of-scope"):
        raise InputError(
            f"ticket {number}: wayfinderReconciliation.disposition must be "
            "'resolved' or 'out-of-scope'",
        )
    if result["author"] != current_user:
        raise InputError(
            f"ticket {number}: Wayfinder reconciliation marker is not runner-authored",
        )
    if result["projectItemId"] != project_item_id:
        raise InputError(
            f"ticket {number}: Wayfinder reconciliation Project item changed",
        )
    if result["configurationDigest"] != configuration_digest:
        raise InputError(
            f"ticket {number}: Wayfinder reconciliation configuration changed",
        )
    return result


def analyze_wayfinder_ticket(
    ticket: dict[str, Any],
    *,
    current_user: str,
    planning_status: str,
    priorities: tuple[str, ...],
    execution_approvers: tuple[str, ...],
    configuration_digest: str,
    wayfinder_map_label: str,
    wayfinder_child_labels: dict[str, str],
) -> dict[str, Any]:
    number = ticket["number"]
    common = analyze_common_ticket(
        ticket,
        priorities,
        require_execution_pr_fields=False,
    )
    assignees = common["assignees"]
    labels = common["labels"]
    blockers = common["blockers"]
    open_descendants = common["openDescendants"]
    pull_requests = common["pullRequests"]
    errors = common["errors"]
    exclusions = common["exclusions"]

    reconciliation = parse_wayfinder_reconciliation(
        ticket.get("wayfinderReconciliation"),
        number=number,
        current_user=current_user,
        project_item_id=ticket["projectItemId"],
        configuration_digest=configuration_digest,
    )

    types = [
        ticket_type
        for ticket_type, label in wayfinder_child_labels.items()
        if label in labels
    ]
    if len(types) != 1:
        raise InputError("expected exactly one Wayfinder type label")
    ticket_type = types[0]
    parent_number = parse_wayfinder_parent(
        ticket,
        map_label=wayfinder_map_label,
        allow_closed=reconciliation is not None,
    )

    assigned_to_current_user = current_user in assignees
    if reconciliation is not None:
        if reconciliation["mapNumber"] != parent_number:
            raise InputError(
                f"ticket {number}: Wayfinder reconciliation map does not match parent",
            )
        if not assigned_to_current_user or len(assignees) != 1:
            exclusions.append(
                "Wayfinder reconciliation is not assigned only to current user",
            )
        if str(ticket["state"]).upper() not in ("OPEN", "CLOSED"):
            exclusions.append("Wayfinder reconciliation issue state is unknown")
        if pull_requests:
            exclusions.append(
                "has open implementation PRs "
                f"{[pull_request['url'] for pull_request in pull_requests]}",
            )
        return {
            "ticket": ticket,
            "priorityRank": common["priorityRank"],
            "projectPosition": common["projectPosition"],
            "assignedToCurrentUser": assigned_to_current_user,
            "resumeAction": "resume-wayfinder-reconciliation",
            "wayfinderType": ticket_type,
            "resolutionMode": "afk",
            "errors": errors,
            "exclusions": exclusions,
        }

    if str(ticket["state"]).upper() != "OPEN":
        exclusions.append("not open")
    if ticket["projectStatus"] != planning_status:
        exclusions.append(f"not in {planning_status!r}")
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
    if planning_transition["wasAutomated"]:
        exclusions.append("planning transition was automated")
    elif planning_transition["actor"] not in execution_approvers:
        exclusions.append(
            "planning transition actor "
            f"{planning_transition['actor']!r} is not approved",
        )
    other_assignees = [assignee for assignee in assignees if assignee != current_user]
    if other_assignees:
        exclusions.append(f"assigned to {other_assignees}")
    if blockers:
        exclusions.append(f"blocked by {blockers}")
    if open_descendants:
        exclusions.append(f"open descendants {open_descendants}")
    if pull_requests:
        exclusions.append(
            "has open implementation PRs "
            f"{[pull_request['url'] for pull_request in pull_requests]}",
        )

    resolution_mode = "afk"
    if ticket_type in ("prototype", "grilling"):
        resolution_mode = "hitl"
    elif ticket_type == "task":
        task_mode = ticket.get("wayfinderTaskMode")
        if task_mode in (None, "hitl"):
            resolution_mode = "hitl"
        elif task_mode == "afk":
            evidence = ticket.get("wayfinderAfkEvidence")
            if not isinstance(evidence, str) or not evidence:
                raise InputError(
                    f"ticket {number}: AFK Wayfinder task needs non-empty evidence",
                )
        else:
            raise InputError(
                f"ticket {number}: wayfinderTaskMode must be 'afk', 'hitl', or null",
            )
    elif ticket.get("wayfinderTaskMode") is not None:
        raise InputError(
            f"ticket {number}: wayfinderTaskMode applies only to Wayfinder tasks",
        )

    return {
        "ticket": ticket,
        "priorityRank": common["priorityRank"],
        "projectPosition": common["projectPosition"],
        "assignedToCurrentUser": assigned_to_current_user,
        "resumeAction": "resume-wayfind" if assigned_to_current_user else "wayfind",
        "wayfinderType": ticket_type,
        "resolutionMode": resolution_mode,
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
        wayfinder_labels = configured_wayfinder_labels(args)
        wayfinder_child_labels = (
            {
                ticket_type: label
                for ticket_type, label in wayfinder_labels.items()
                if ticket_type != "map"
            }
            if wayfinder_labels is not None
            else {}
        )
        statuses = (
            args.backlog_status,
            args.planning_status,
            args.ready_status,
            args.in_progress_status,
        )
        if len(set(statuses)) != len(statuses):
            raise InputError("project statuses must be unique")
        role_labels = (
            args.needs_triage_label,
            args.epic_label,
            args.human_work_label,
            AGENT_WORK_LABEL,
        )
        if any(not label for label in role_labels):
            raise InputError("role labels must be non-empty")
        if len(set(role_labels)) != len(role_labels):
            raise InputError("role labels must be unique")
        if wayfinder_labels is not None and (
            set(role_labels) & set(wayfinder_labels.values())
        ):
            raise InputError("Wayfinder labels cannot overlap existing role labels")
        if not args.configuration_digest:
            raise InputError("configuration digest must be a non-empty string")
        if args.wayfinder_ticket is not None:
            if args.wayfinder_ticket <= 0:
                raise InputError("Wayfinder ticket must be a positive integer")
            if args.mode != "next":
                raise InputError("an explicit Wayfinder ticket requires next mode")
            if wayfinder_labels is None:
                raise InputError(
                    "an explicit Wayfinder ticket requires Wayfinder configuration",
                )
        if not 1 <= args.max_claims <= 3:
            raise InputError("max claims must be between 1 and 3")

        seen_numbers: set[int] = set()
        execution_analyses: list[dict[str, Any]] = []
        wayfinder_analyses: list[dict[str, Any]] = []
        backlog_analyses: list[dict[str, Any]] = []
        invalid_unclaimed: list[dict[str, Any]] = []
        invalid_claimed: list[dict[str, Any]] = []
        invalid_planning_claimed: list[dict[str, Any]] = []
        for raw_ticket in payload:
            try:
                ticket = require_ticket_shape(raw_ticket)
                if ticket["number"] in seen_numbers:
                    raise InputError(f"duplicate ticket number {ticket['number']}")
                seen_numbers.add(ticket["number"])
                labels = ticket["labels"]
                has_wayfinder_map_label = (
                    wayfinder_labels is not None
                    and isinstance(labels, list)
                    and wayfinder_labels["map"] in labels
                )
                is_wayfinder = (
                    wayfinder_labels is not None
                    and isinstance(labels, list)
                    and any(
                        label in wayfinder_child_labels.values()
                        for label in labels
                        if isinstance(label, str)
                    )
                )
                if has_wayfinder_map_label:
                    invalid = {
                        "number": ticket["number"],
                        "reasons": [
                            (
                                "Wayfinder map cannot carry a child type label"
                                if is_wayfinder
                                else "Wayfinder map is not a child candidate"
                            ),
                        ],
                    }
                    if is_wayfinder and has_current_user_assignment(
                        ticket,
                        args.current_user,
                    ):
                        invalid_planning_claimed.append(invalid)
                    else:
                        invalid_unclaimed.append(invalid)
                elif is_wayfinder:
                    wayfinder_analyses.append(
                        analyze_wayfinder_ticket(
                            ticket,
                            current_user=args.current_user,
                            planning_status=args.planning_status,
                            priorities=priorities,
                            execution_approvers=execution_approvers,
                            configuration_digest=args.configuration_digest,
                            wayfinder_map_label=wayfinder_labels["map"],
                            wayfinder_child_labels=wayfinder_child_labels,
                        ),
                    )
                elif (
                    ticket["projectStatus"] == args.backlog_status
                    and (
                        not has_current_user_assignment(
                            ticket,
                            args.current_user,
                        )
                        or (
                            isinstance(ticket["labels"], list)
                            and args.human_work_label in ticket["labels"]
                        )
                    )
                ):
                    backlog_analyses.append(
                        analyze_backlog_ticket(
                            ticket,
                            needs_triage_label=args.needs_triage_label,
                            epic_label=args.epic_label,
                            human_work_label=args.human_work_label,
                            priorities=priorities,
                        ),
                    )
                else:
                    execution_analyses.append(
                        analyze_ticket(
                            ticket,
                            current_user=args.current_user,
                            backlog_status=args.backlog_status,
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
                is_human_frontier_item = (
                    isinstance(raw_ticket, dict)
                    and raw_ticket.get("projectStatus") == args.backlog_status
                    and isinstance(raw_ticket.get("labels"), list)
                    and args.human_work_label in raw_ticket["labels"]
                )
                is_wayfinder_claim = (
                    isinstance(raw_ticket, dict)
                    and isinstance(raw_ticket.get("labels"), list)
                    and any(
                        label in wayfinder_child_labels.values()
                        for label in raw_ticket["labels"]
                        if isinstance(label, str)
                    )
                    and has_current_user_assignment(raw_ticket, args.current_user)
                )
                if is_human_frontier_item:
                    invalid_unclaimed.append(invalid)
                elif is_wayfinder_claim:
                    invalid_planning_claimed.append(invalid)
                elif has_current_user_assignment(raw_ticket, args.current_user):
                    if (
                        isinstance(raw_ticket, dict)
                        and raw_ticket.get("projectStatus")
                        in (
                            args.backlog_status,
                            args.planning_status,
                            args.ready_status,
                        )
                    ):
                        invalid_planning_claimed.append(invalid)
                    else:
                        invalid_claimed.append(invalid)
                elif (
                    isinstance(raw_ticket, dict)
                    and raw_ticket.get("projectStatus") == args.backlog_status
                ):
                    invalid_unclaimed.append(invalid)
                else:
                    invalid_unclaimed.append(invalid)

        blocked_claims = invalid_claimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in execution_analyses
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
            for item in execution_analyses
            if (
                item["assignedToCurrentUser"]
                and item["ticket"]["projectStatus"]
                in (
                    args.backlog_status,
                    args.planning_status,
                    args.ready_status,
                )
                and (item["errors"] or item["exclusions"])
            )
        ]
        blocked_planning_claims.extend(
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in wayfinder_analyses
            if (
                item["assignedToCurrentUser"]
                and (item["errors"] or item["exclusions"])
            )
        )

        eligible = [
            item
            for item in execution_analyses
            if not item["errors"] and not item["exclusions"]
        ]
        eligible_wayfinder = [
            item
            for item in wayfinder_analyses
            if not item["errors"] and not item["exclusions"]
        ]

        selection_pool = [*eligible, *eligible_wayfinder]
        if args.wayfinder_ticket is not None:
            selected = [
                item
                for item in wayfinder_analyses
                if item["ticket"]["number"] == args.wayfinder_ticket
            ]
            if not selected:
                raise InputError(
                    f"selected Wayfinder ticket {args.wayfinder_ticket} "
                    "is not a configured child contender",
                )
            selected_item = selected[0]
            selected_reasons = selected_item["errors"] + selected_item["exclusions"]
            if selected_reasons:
                raise InputError(
                    f"selected Wayfinder ticket {args.wayfinder_ticket} is ineligible: "
                    + "; ".join(selected_reasons),
                )
            other_claims = list(
                dict.fromkeys(
                    [
                        item["ticket"]["number"]
                        for item in selection_pool
                        if item["assignedToCurrentUser"]
                        and item["ticket"]["number"] != args.wayfinder_ticket
                    ]
                    + [
                        item["number"]
                        for item in [*blocked_claims, *blocked_planning_claims]
                        if item["number"] != args.wayfinder_ticket
                    ],
                ),
            )
            other_claims.sort(
                key=lambda number: (
                    (0, number)
                    if isinstance(number, int) and not isinstance(number, bool)
                    else (1, str(number))
                ),
            )
            if other_claims:
                raise InputError(
                    f"selected Wayfinder ticket {args.wayfinder_ticket} cannot bypass "
                    f"existing claims {other_claims}",
                )
            selection_pool = [selected_item]

        claimed = [
            item
            for item in selection_pool
            if (
                item["assignedToCurrentUser"]
                and (
                    args.mode == "next"
                    or item.get("resolutionMode", "afk") == "afk"
                )
            )
        ]
        claimed.sort(
            key=lambda item: (
                CLAIM_ACTION_RANK.get(item["resumeAction"], 2),
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
            (
                item
                for item in selection_pool
                if not item["assignedToCurrentUser"]
                and (
                    args.mode == "next"
                    or item.get("resolutionMode", "afk") == "afk"
                )
            ),
            key=lambda item: (
                CANDIDATE_ACTION_RANK[item["resumeAction"]],
                *ticket_rank(item),
            ),
        )

        excluded = invalid_unclaimed + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in execution_analyses
            if (
                not item["assignedToCurrentUser"]
                and (item["errors"] or item["exclusions"])
            )
        ] + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in wayfinder_analyses
            if (
                not item["assignedToCurrentUser"]
                and (item["errors"] or item["exclusions"])
            )
        ] + [
            {
                "number": item["ticket"]["number"],
                "reasons": item["errors"] + item["exclusions"],
            }
            for item in backlog_analyses
            if item["errors"] or item["exclusions"]
        ]
        eligible_backlog = [
            item
            for item in backlog_analyses
            if not item["errors"] and not item["exclusions"]
        ]
        triage_candidates = sorted(
            (
                item for item in eligible_backlog
                if item["action"] == "triage" and not item["blockerReasons"]
            ),
            key=ticket_rank,
        )
        ready_epics = sorted(
            (
                item for item in eligible_backlog
                if item["action"] == "close-epic" and not item["blockerReasons"]
            ),
            key=ticket_rank,
        )
        human_actions = sorted(
            (
                item for item in eligible_backlog
                if item["action"] in ("move-to-planning", "perform-human-work")
                and not item["blockerReasons"]
            ),
            key=ticket_rank,
        )
        parked_blocked = sorted(
            (item for item in eligible_backlog if item["blockerReasons"]),
            key=ticket_rank,
        )
        wayfinder_human_frontier = sorted(
            (
                item
                for item in eligible_wayfinder
                if args.mode == "drain"
                and item["resolutionMode"] == "hitl"
                and not item["assignedToCurrentUser"]
            ),
            key=ticket_rank,
        )
        wayfinder_claimed_hitl = sorted(
            (
                item
                for item in eligible_wayfinder
                if args.mode == "drain"
                and item["resolutionMode"] == "hitl"
                and item["assignedToCurrentUser"]
            ),
            key=ticket_rank,
        )
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
            "triageCandidates": [
                {
                    "ticket": item["ticket"],
                    "action": item["action"],
                }
                for item in triage_candidates
            ],
            "readyEpics": [
                {
                    "ticket": item["ticket"],
                    "action": item["action"],
                }
                for item in ready_epics
            ],
            "humanActions": [
                {
                    "ticket": item["ticket"],
                    "action": item["action"],
                }
                for item in human_actions
            ],
            "parkedBlocked": [
                {
                    "ticket": item["ticket"],
                    "role": item["role"],
                    "reasons": item["blockerReasons"],
                }
                for item in parked_blocked
            ],
            "excluded": excluded,
        }
        if wayfinder_labels is not None:
            output["wayfinderHumanFrontier"] = [
                {
                    "ticket": item["ticket"],
                    "action": "resolve-wayfinder-hitl",
                    "type": item["wayfinderType"],
                }
                for item in wayfinder_human_frontier
            ]
            output["wayfinderClaimedHitl"] = [
                {
                    "ticket": item["ticket"],
                    "action": "resume-wayfinder-hitl",
                    "type": item["wayfinderType"],
                }
                for item in wayfinder_claimed_hitl
            ]
        if args.wayfinder_ticket is not None:
            output["selectedWayfinderTicket"] = args.wayfinder_ticket
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (InputError, json.JSONDecodeError) as error:
        print(json.dumps({"reason": "invalid-input", "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
