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
from collections import deque
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

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
"""
PR_CHECK_FIELDS = """
  id
  number
  headRefOid
  commits(last: 1) {
    nodes {
      commit {
        oid
        statusCheckRollup {
          state
          contexts(first: 100, after: $checkAfter) {
            totalCount
            pageInfo { hasNextPage endCursor }
            nodes {
              __typename
              ... on CheckRun { id name status conclusion }
              ... on StatusContext { id context state }
            }
          }
        }
      }
    }
  }
"""
ISSUE_FIELDS = "comments(last: 1) { nodes { id updatedAt } }"
KINDS = ("item", "pullRequest", "issue")


class WatchError(RuntimeError):
    """Raised when the watcher cannot obtain a trustworthy reading."""


def repository_query(prs: list[int], issues: list[int], *, checks_only: bool = False) -> str:
    fields = PR_CHECK_FIELDS if checks_only else PR_FIELDS + PR_CHECK_FIELDS
    aliases = [f"pr{n}: pullRequest(number: {n}) {{ {fields} }}" for n in prs]
    aliases += [f"issue{n}: issue(number: {n}) {{ {ISSUE_FIELDS} }}" for n in issues]
    cursor = ", $checkAfter: String" if prs else ""
    return (
        f"query($owner: String!, $name: String!{cursor}) {{"
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


PARENT_CONNECTIONS = {"subIssues": "id", "blockedBy": "id",
                      "labels": "name", "assignees": "login"}
PARENT_FIELDS = """
  ... on Issue {
    id url state updatedAt repository { nameWithOwner } parent { id }
    comments(last: 1) { nodes { id updatedAt } }
    CONNECTIONS
  }
""".replace("CONNECTIONS", "\n".join(
    f"{name}(first: 100, after: ${name}) {{ pageInfo {{ hasNextPage endCursor }} nodes {{ {field} }} }}"
    for name, field in PARENT_CONNECTIONS.items()
))

PARENT_BATCH_SIZE = 20


def parent_query(node_ids: list[str], cursors: dict[str, str]) -> tuple[str, dict[str, str]]:
    variables = {f"id{i}": node_id for i, node_id in enumerate(node_ids)}
    declarations = [f"$id{i}: ID!" for i in range(len(node_ids))]
    declarations.extend(f"${name}: String" for name in PARENT_CONNECTIONS)
    aliases = [f"node{i}: node(id: $id{i}) {{ {PARENT_FIELDS} }}"
               for i in range(len(node_ids))]
    return (f"query({', '.join(declarations)}) {{ rateLimit {{ cost remaining resetAt }} "
            + " ".join(aliases) + " }", {**variables, **cursors})


def fetch_parent(args: argparse.Namespace, deadline: datetime | None) -> dict[str, Any] | None:
    """Read every descendant and transitive blocker, including closed nodes."""
    pending = deque([args.parent_id])
    prefetched = {}
    scope = {args.parent_id}
    expanded = set()
    records = {}
    limits = []
    identities = {}
    while pending:
        node_id = pending.popleft()
        if node_id in records:
            if node_id in scope and node_id not in expanded:
                children = records[node_id]["subIssues"]
                scope.update(children)
                pending.extend(children)
                expanded.add(node_id)
            continue
        cursors = {}
        active = set(PARENT_CONNECTIONS)
        connections = {name: [] for name in active}
        seen_cursors = {name: set() for name in active}
        metadata = None
        while active:
            if node_id in prefetched and metadata is None:
                node = prefetched.pop(node_id)
            else:
                batch = [node_id]
                if metadata is None:
                    for candidate in pending:
                        if candidate not in records and candidate not in prefetched and candidate not in batch:
                            batch.append(candidate)
                            if len(batch) == PARENT_BATCH_SIZE:
                                break
                if limits and not await_budget(limits[-1], deadline):
                    return None
                query, variables = parent_query(batch, cursors)
                data = graphql(query, deadline, **variables)
                limits.append(data["rateLimit"])
                for index, identity in enumerate(batch):
                    prefetched[identity] = data.get(f"node{index}")
                node = prefetched.pop(node_id)
            if not isinstance(node, dict) or node.get("id") != node_id:
                raise WatchError(f"issue {node_id} missing or identity changed")
            if not {"id", "url", "state", "updatedAt", "repository", "parent", "comments"} <= node.keys():
                raise WatchError(f"issue {node_id}: incomplete readback")
            if not isinstance(node["comments"]["nodes"], list) or not node["updatedAt"]:
                raise WatchError(f"issue {node_id}: incomplete marker readback")
            current = {k: v for k, v in node.items() if k not in PARENT_CONNECTIONS}
            if metadata is not None and metadata != current:
                raise WatchError(f"issue {node_id} changed during pagination; refresh required")
            metadata = current
            for name in list(active):
                connection = node[name]
                nodes, info = connection["nodes"], connection["pageInfo"]
                if not isinstance(nodes, list) or any(not n or not n.get(PARENT_CONNECTIONS[name]) for n in nodes):
                    raise WatchError(f"issue {node_id}: incomplete {name}")
                values = [n[PARENT_CONNECTIONS[name]] for n in nodes]
                if len(set(connections[name] + values)) != len(connections[name]) + len(values):
                    raise WatchError(f"issue {node_id}: duplicate {name} page")
                connections[name].extend(values)
                if info["hasNextPage"] is False:
                    active.remove(name)
                elif info["hasNextPage"] is True and info["endCursor"] and info["endCursor"] not in seen_cursors[name]:
                    cursors[name] = info["endCursor"]
                    seen_cursors[name].add(info["endCursor"])
                else:
                    raise WatchError(f"issue {node_id}: incomplete {name} pagination")
        repository = metadata["repository"]["nameWithOwner"]
        url = urlparse(metadata["url"])
        prefix = f"/{repository}/issues/"
        if (not url.netloc or url.scheme != "https" or not url.path.startswith(prefix)
                or not url.path[len(prefix):].isdigit() or metadata["state"] not in ("OPEN", "CLOSED")):
            raise WatchError(f"issue {node_id}: ambiguous repository identity or state")
        if metadata["url"] in identities and identities[metadata["url"]] != node_id:
            raise WatchError("conflicting issue identities")
        identities[metadata["url"]] = node_id
        if node_id == args.parent_id and repository.casefold() != args.repository.casefold():
            raise WatchError("parent issue belongs to a different repository")
        for name in ("blockedBy", "labels", "assignees"):
            connections[name].sort()
        records[node_id] = {**metadata, **connections}
        pending.extend(connections["blockedBy"])
        if node_id in scope:
            expanded.add(node_id)
            scope.update(connections["subIssues"])
            pending.extend(connections["subIssues"])
    # A dependency may have been fetched before becoming a discovered descendant.
    frontier = [args.parent_id]
    visited = set()
    while frontier:
        node_id = frontier.pop()
        if node_id in visited:
            raise WatchError("cyclic or duplicate sub-issue graph; refresh required")
        visited.add(node_id)
        if node_id not in records:
            raise WatchError("descendant graph changed or is incomplete; refresh required")
        if records[node_id]["repository"]["nameWithOwner"].casefold() != args.repository.casefold():
            raise WatchError("cross-repository descendant scope requires explicit reconciliation")
        frontier.extend(records[node_id]["subIssues"])
    return {"records": records, "limits": limits}


def check_rollup(record: Any, number: int, pr_id: Any, head: Any) -> dict[str, Any] | None:
    """Validate the PR and selected commit before accepting a page."""
    if (not isinstance(record, dict) or record.get("number") != number
            or not isinstance(pr_id, str) or not pr_id or record.get("id") != pr_id
            or not isinstance(head, str) or not head or record.get("headRefOid") != head):
        raise WatchError(f"PR {number}: missing or changed PR/head identity")
    commits = record["commits"]["nodes"]
    if not isinstance(commits, list) or len(commits) != 1:
        raise WatchError(f"PR {number}: missing or ambiguous head commit")
    commit = commits[0]["commit"]
    if commit["oid"] != head:
        raise WatchError(f"PR {number}: selected commit does not match PR head")
    return commit["statusCheckRollup"]


def fetch_checks(
    number: int, record: Any, owner: str, name: str,
    limits: list[dict[str, Any]], deadline: datetime | None,
) -> dict[str, Any] | None:
    """Collect every check context on one observed head, or stop at the deadline."""
    pr_id = record.get("id") if isinstance(record, dict) else None
    head = record.get("headRefOid") if isinstance(record, dict) else None
    rollup = check_rollup(record, number, pr_id, head)
    if rollup is None:
        return {"checks": None, "check_contexts": {}}
    state = rollup["state"]
    if not isinstance(state, str) or not state:
        raise WatchError(f"PR {number}: incomplete check rollup")
    total = None
    contexts = {}
    seen_cursors = set()
    while True:
        if rollup is None or rollup["state"] != state:
            raise WatchError(f"PR {number}: check rollup changed during pagination")
        connection = rollup["contexts"]
        count = connection["totalCount"]
        if type(count) is not int or count < 0:
            raise WatchError(f"PR {number}: invalid check context count")
        if total is not None and count != total:
            raise WatchError(f"PR {number}: check context count changed during pagination")
        total = count
        nodes = connection["nodes"]
        if not isinstance(nodes, list):
            raise WatchError(f"PR {number}: incomplete check contexts")
        for node in nodes:
            context_id = node["id"]
            kind = node["__typename"]
            if not isinstance(context_id, str) or not context_id or context_id in contexts:
                raise WatchError(f"PR {number}: missing or duplicate check context identity")
            if kind == "CheckRun":
                fields = ("name", "status")
            elif kind == "StatusContext":
                fields = ("context", "state")
            else:
                raise WatchError(f"PR {number}: unknown check context type")
            if any(not isinstance(node[field], str) or not node[field] for field in fields):
                raise WatchError(f"PR {number}: incomplete check context")
            context = {"type": kind, **{field: node[field] for field in fields}}
            if kind == "CheckRun":
                conclusion = node["conclusion"]
                if conclusion is not None and (not isinstance(conclusion, str) or not conclusion):
                    raise WatchError(f"PR {number}: invalid check run conclusion")
                context["conclusion"] = conclusion
            contexts[context_id] = context
        info = connection["pageInfo"]
        cursor = info["endCursor"]
        more = info["hasNextPage"]
        if cursor is not None and (not isinstance(cursor, str) or not cursor or cursor in seen_cursors):
            raise WatchError(f"PR {number}: invalid check context cursor")
        if more is False and len(contexts) == total:
            return {"checks": state, "check_contexts": contexts}
        if more is not True or not nodes or len(contexts) >= total or cursor is None:
            raise WatchError(f"PR {number}: incomplete check context pagination")
        seen_cursors.add(cursor)
        if (deadline is not None and now() >= deadline) or not await_budget(limits[-1], deadline):
            return None
        data = graphql(repository_query([number], [], checks_only=True), deadline,
                       owner=owner, name=name, checkAfter=cursor)
        limits.append(data["rateLimit"])
        records = data.get("repository")
        record = records.get(f"pr{number}") if isinstance(records, dict) else None
        rollup = check_rollup(record, number, pr_id, head)


def fetch(
    args: argparse.Namespace, deadline: datetime | None = None, *, replacement_prs: list[int] | None = None
) -> dict[str, Any] | None:
    """Return the complete scope graph plus watched repository records.

    `replacement_prs` limits a board-preserving snapshot to selected PRs.
    `rate` aggregates cost and remaining budget within the latest rate window.
    Returns None if the deadline arrives while waiting out the rate budget.
    """
    pr_only = replacement_prs is not None
    prs = replacement_prs if pr_only else args.pr
    pages: list[dict[str, Any]] = []
    parent = fetch_parent(args, deadline) if args.parent_id and not pr_only else None
    if args.parent_id and not pr_only and parent is None:
        return None
    after = ""
    while not pr_only and not args.parent_id:
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
    checks = {}
    limits = [*(parent["limits"] if parent else []), *(page["rateLimit"] for page in pages)]
    issues = [] if pr_only else args.issue
    if prs or issues:
        owner, _, name = args.repository.partition("/")
        if limits and not await_budget(limits[-1], deadline):
            return None
        repo = graphql(
            repository_query(prs, issues), deadline, owner=owner, name=name
        )
        records = repo.get("repository")
        if not isinstance(records, dict):
            raise WatchError(f"repository {args.repository} not found")
        limits.append(repo["rateLimit"])
        for number in dict.fromkeys(prs):
            fields = fetch_checks(number, records.get(f"pr{number}"), owner, name, limits, deadline)
            if fields is None:
                return None
            checks[f"pr{number}"] = fields
    reset_at = max(parse_time(r["resetAt"]) for r in limits)
    window = [r for r in limits if parse_time(r["resetAt"]) == reset_at]
    rate = {"cost": sum(r["cost"] for r in window),
            "remaining": min(r["remaining"] for r in window),
            "resetAt": reset_at.isoformat()}
    return {"pages": pages, "repository": repo, "checks": checks, "rate": rate,
            "parent": parent["records"] if parent else {}}


def fingerprint(responses: dict[str, Any]) -> dict[str, Any]:
    """Reduce raw responses to the fields whose change should wake the controller."""
    items: dict[str, Any] = dict(responses.get("parent", {}))
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
            prs[alias[2:]] = {
                "state": record["state"],
                "sha": record["headRefOid"],
                "base": record["baseRefOid"],
                **responses["checks"][alias],
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
                prior = before[key]
                if kind == "pullRequest" and "check_contexts" not in prior:
                    prior = {"check_contexts": {}, **prior}
                fields = [
                    field
                    for field in sorted(after[key])
                    if prior.get(field) != after[key][field]
                    and not recomputing(field, prior.get(field), after[key][field])
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
    scope = common.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project-id", help="Project node ID (PVT_...)")
    scope.add_argument("--parent-id", help="Resolved parent issue node ID")
    common.add_argument("--repository", required=True, help="owner/name")
    common.add_argument("--status-field", default="Status")
    common.add_argument("--pr", type=int, action="append", default=[], help="PR in the complete watch set")
    common.add_argument("--issue", type=int, action="append", default=[])
    commands = parser.add_subparsers(dest="command", required=True)
    snapshot_command = commands.add_parser(
        "snapshot", parents=[common], help="print the current fingerprint as one JSON line"
    )
    snapshot_command.add_argument(
        "--board-from",
        help="preserve prior fingerprints outside the targeted PR refresh",
    )
    snapshot_command.add_argument(
        "--refresh-pr", type=int, action="append", default=[],
        help="watched PR covered by the following targeted read (requires --board-from)",
    )
    wait_command = commands.add_parser(
        "wait", parents=[common], help="exit on the first difference from --baseline, or at --deadline"
    )
    wait_command.add_argument("--baseline", required=True, help="file written by snapshot")
    wait_command.add_argument("--deadline", required=True, help="ISO-8601 timestamp")
    wait_command.add_argument("--interval", type=float, default=120.0, help="seconds")
    return parser.parse_args()


def load_baseline(path: str) -> dict[str, Any]:
    with open(path) as handle:
        baseline = json.load(handle)
    if not isinstance(baseline, dict) or not all(isinstance(baseline.get(k), dict) for k in KINDS):
        raise WatchError(f"{path} is not a snapshot fingerprint")
    return baseline


def wait(args: argparse.Namespace) -> int:
    baseline = load_baseline(args.baseline)
    deadline = parse_time(args.deadline)
    while now() < deadline:
        responses = fetch(args, deadline)
        if responses is None:
            break
        current = fingerprint(responses)
        changes = diff(baseline, current)
        if now() >= deadline:
            break
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
            refresh = set(args.refresh_pr)
            if refresh and not args.board_from:
                raise WatchError("--refresh-pr requires --board-from")
            if refresh.difference(args.pr):
                raise WatchError("--refresh-pr must be in the --pr watch set")
            prior = load_baseline(args.board_from) if args.board_from else None
            if prior is not None:
                old_prs = prior["pullRequest"]
                selected = sorted({n for n in args.pr if n in refresh or str(n) not in old_prs})
                fresh = fingerprint(fetch(args, replacement_prs=selected))["pullRequest"] if selected else {}
                # Keep unrefreshed and removed PRs visible as drift on the next wait.
                current = {**prior, "pullRequest": {**old_prs, **fresh}}
            else:
                current = fingerprint(fetch(args))
            report(current)
            return 0
        return wait(args)
    except (WatchError, OSError, ValueError, KeyError, TypeError) as error:
        report({"status": "error", "message": str(error) or type(error).__name__})
        return 1


if __name__ == "__main__":
    sys.exit(main())
