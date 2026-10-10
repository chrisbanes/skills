#!/usr/bin/env python3
"""Read-only GitHub Project watcher: fingerprint the board, wait for a change.

A report is a hint to refresh, never authority. Only `gh api graphql` queries
run here; nothing is mutated.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ITEMS_QUERY = """
query($id: ID!, $status: String!, $after: String) {
  rateLimit { cost remaining resetAt }
  node(id: $id) {
    ... on ProjectV2 {
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          updatedAt
          fieldValueByName(name: $status) {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
          content {
            ... on Issue {
              state
              issueDependenciesSummary { blockedBy totalBlockedBy }
              parent { id }
              subIssuesSummary { completed total }
              assignees(first: 20) { nodes { login } }
              labels(first: 50) { nodes { name } }
            }
            ... on PullRequest {
              state
              assignees(first: 20) { nodes { login } }
              labels(first: 50) { nodes { name } }
            }
          }
        }
      }
    }
  }
}
"""
# Inline review comments and thread replies are submitted as reviews, so the
# latest review ID catches them; comments are PR conversation comments only.
PR_FIELDS = """
  state
  headRefOid
  baseRefOid
  mergeable
  reviewDecision
  reviews(last: 1) { nodes { id } }
  comments(last: 1) { nodes { id } }
  commits(last: 1) { nodes { commit { statusCheckRollup { state } } } }
"""
ISSUE_FIELDS = "comments(last: 1) { nodes { id updatedAt } }"
KINDS = ("item", "pullRequest", "issue")


class WatchError(RuntimeError):
    """Raised when the watcher cannot obtain a trustworthy reading."""


def repository_query(prs: list[int], issues: list[int]) -> str:
    aliases = [f"pr{n}: pullRequest(number: {n}) {{ {PR_FIELDS} }}" for n in prs]
    aliases += [f"issue{n}: issue(number: {n}) {{ {ISSUE_FIELDS} }}" for n in issues]
    return (
        "query($owner: String!, $name: String!) {"
        " rateLimit { cost remaining resetAt }"
        f" repository(owner: $owner, name: $name) {{ {' '.join(aliases)} }} }}"
    )


def seconds_left(deadline: datetime | None) -> float:
    """Subprocess timeout: at most 60s, never past the deadline."""
    if deadline is None:
        return 60.0
    return max(1.0, min(60.0, (deadline - now()).total_seconds()))


def graphql(query: str, deadline: datetime | None, **variables: str) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        command += ["-f", f"{key}={value}"]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=seconds_left(deadline)
        )
    except subprocess.TimeoutExpired as error:
        raise WatchError(f"gh timed out after {error.timeout:g}s") from error
    except OSError as error:
        raise WatchError(f"cannot run gh: {error}") from error
    if result.returncode != 0:
        raise WatchError(f"gh exited {result.returncode}: {result.stderr.strip()}")
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise WatchError(f"gh returned invalid JSON: {error}") from error
    if not isinstance(response, dict) or response.get("errors") or "data" not in response:
        errors = response.get("errors") if isinstance(response, dict) else response
        raise WatchError(f"GraphQL error: {json.dumps(errors)}")
    return response["data"]


def await_budget(rate: dict[str, Any], deadline: datetime | None) -> bool:
    """Sleep out an exhausted rate budget before the next request.

    Returns False when the deadline arrives first. Without a deadline there is
    nothing to cap the sleep, so fail instead.
    """
    if rate["remaining"] >= rate["cost"]:
        return True
    reset_in = (parse_time(rate["resetAt"]) - now()).total_seconds()
    if reset_in <= 0:
        return True
    if deadline is None:
        raise WatchError(f"rate limit exhausted until {rate['resetAt']}")
    left = max(0.0, (deadline - now()).total_seconds())
    time.sleep(min(reset_in, left))
    return reset_in < left


def fetch(
    args: argparse.Namespace, deadline: datetime | None = None
) -> dict[str, Any] | None:
    """Return raw responses: all Project item pages plus one repository query.

    `rate` aggregates the cycle: summed cost, lowest remaining, latest reset.
    Returns None if the deadline arrives while waiting out the rate budget.
    """
    pages: list[dict[str, Any]] = []
    after = ""
    while True:
        variables = {"id": args.project_id, "status": args.status_field}
        if after:
            variables["after"] = after
        if pages and not await_budget(pages[-1]["rateLimit"], deadline):
            return None
        data = graphql(ITEMS_QUERY, deadline, **variables)
        pages.append(data)
        items = (data.get("node") or {}).get("items")
        if items is None:
            raise WatchError(f"Project {args.project_id} returned no items")
        if not items["pageInfo"]["hasNextPage"]:
            break
        after = items["pageInfo"]["endCursor"]
    repo = None
    if args.pr or args.issue:
        owner, _, name = args.repository.partition("/")
        if not await_budget(pages[-1]["rateLimit"], deadline):
            return None
        repo = graphql(
            repository_query(args.pr, args.issue), deadline, owner=owner, name=name
        )
        if repo.get("repository") is None:
            raise WatchError(f"repository {args.repository} not found")
    limits = [r["rateLimit"] for r in (*pages, *([repo] if repo else []))]
    rate = {
        "cost": sum(r["cost"] for r in limits),
        "remaining": min(r["remaining"] for r in limits),
        "resetAt": max((r["resetAt"] for r in limits), key=parse_time),
    }
    return {"pages": pages, "repository": repo, "rate": rate}


def fingerprint(responses: dict[str, Any]) -> dict[str, Any]:
    """Reduce raw responses to the fields whose change should wake the controller."""
    items: dict[str, Any] = {}
    for data in responses["pages"]:
        for node in data["node"]["items"]["nodes"]:
            content = node.get("content") or {}
            items[node["id"]] = {
                # Catches custom-field edits (e.g. Priority) the other fields miss.
                "updated": node.get("updatedAt"),
                "status": (node.get("fieldValueByName") or {}).get("name"),
                "assignees": sorted(n["login"] for n in (content.get("assignees") or {}).get("nodes", [])),
                "labels": sorted(n["name"] for n in (content.get("labels") or {}).get("nodes", [])),
                "state": content.get("state"),
                "blocked_by": (content.get("issueDependenciesSummary") or {}).get("blockedBy"),
                "total_blocked_by": (content.get("issueDependenciesSummary") or {}).get("totalBlockedBy"),
                "parent": (content.get("parent") or {}).get("id"),
                "sub_completed": (content.get("subIssuesSummary") or {}).get("completed"),
                "sub_total": (content.get("subIssuesSummary") or {}).get("total"),
            }
    prs: dict[str, Any] = {}
    issues: dict[str, Any] = {}
    records = (responses["repository"] or {}).get("repository") or {}
    for alias, record in records.items():
        if record is None:
            raise WatchError(f"{alias} not found")
        if alias.startswith("pr"):
            commits = record["commits"]["nodes"]
            rollup = commits[0]["commit"]["statusCheckRollup"] if commits else None
            prs[alias[2:]] = {
                "state": record["state"],
                "sha": record["headRefOid"],
                "base": record["baseRefOid"],
                "checks": rollup["state"] if rollup else None,
                "review": record["reviewDecision"],
                "review_id": (record["reviews"]["nodes"] or [{}])[-1].get("id"),
                "comment_id": (record["comments"]["nodes"] or [{}])[-1].get("id"),
                "mergeable": record["mergeable"],
            }
        else:
            comments = record["comments"]["nodes"]
            issues[alias[5:]] = {"comment": comments[-1] if comments else None}
    return {"item": items, "pullRequest": prs, "issue": issues}


def recomputing(field: str, before: Any, after: Any) -> bool:
    """GitHub reports mergeable UNKNOWN while recomputing; that is not a change."""
    return field == "mergeable" and after == "UNKNOWN"


def diff(baseline: dict[str, Any], current: dict[str, Any]) -> list[dict[str, Any]]:
    """List changed records by kind, key and field name (never values)."""
    changes = []
    for kind in KINDS:
        before, after = baseline.get(kind, {}), current.get(kind, {})
        for key in sorted(set(before) | set(after)):
            if key not in after:
                fields = ["removed"]
            elif key not in before:
                fields = ["added"]
            else:
                fields = [
                    field
                    for field in sorted(after[key])
                    if before[key].get(field) != after[key][field]
                    and not recomputing(field, before[key].get(field), after[key][field])
                ]
            if fields:
                changes.append({"kind": kind, "key": key, "fields": fields})
    return changes


def parse_time(value: str) -> datetime:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def now() -> datetime:
    return datetime.now(timezone.utc)


def report(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project-id", required=True, help="Project node ID (PVT_...)")
    common.add_argument("--repository", required=True, help="owner/name")
    common.add_argument("--status-field", required=True)
    common.add_argument("--pr", type=int, action="append", default=[])
    common.add_argument("--issue", type=int, action="append", default=[])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "snapshot", parents=[common], help="print the current fingerprint as one JSON line"
    )
    wait_command = commands.add_parser(
        "wait", parents=[common], help="exit on the first difference from --baseline, or at --deadline"
    )
    wait_command.add_argument("--baseline", required=True, help="file written by snapshot")
    wait_command.add_argument("--deadline", required=True, help="ISO-8601 timestamp")
    wait_command.add_argument("--interval", type=float, default=120.0, help="seconds")
    return parser.parse_args()


def wait(args: argparse.Namespace) -> int:
    with open(args.baseline) as handle:
        baseline = json.load(handle)
    if not isinstance(baseline, dict) or not all(isinstance(baseline.get(k), dict) for k in KINDS):
        raise WatchError(f"{args.baseline} is not a snapshot fingerprint")
    deadline = parse_time(args.deadline)
    while now() < deadline:
        responses = fetch(args, deadline)
        if responses is None:
            break
        current = fingerprint(responses)
        changes = diff(baseline, current)
        if changes:
            report({"status": "changed", "changes": changes})
            return 0
        pause = args.interval
        rate = responses["rate"]
        if rate["remaining"] < rate["cost"]:
            pause = max(pause, (parse_time(rate["resetAt"]) - now()).total_seconds())
        time.sleep(max(0.0, min(pause, (deadline - now()).total_seconds())))
    report({"status": "deadline"})
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.command == "snapshot":
            report(fingerprint(fetch(args)))
            return 0
        return wait(args)
    except (WatchError, OSError, ValueError, KeyError, TypeError) as error:
        report({"status": "error", "message": str(error) or type(error).__name__})
        return 1


if __name__ == "__main__":
    sys.exit(main())
