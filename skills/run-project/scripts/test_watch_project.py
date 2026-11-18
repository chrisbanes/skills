#!/usr/bin/env python3
"""Tests for the read-only GitHub Project watcher, using a fake `gh`."""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCRIPT = Path(__file__).with_name("watch_project.py")
COMMON = (
    "--project-id",
    "PVT_1",
    "--repository",
    "acme/repo",
    "--status-field",
    "Status",
)
FAKE_GH = f"""#!{sys.executable}
import json, os, sys, time
path = os.environ["FAKE_GH_STATE"]
with open(path) as handle:
    state = json.load(handle)
total = len(state["responses"])
start = state["loop_from"] if state["loop_from"] is not None else total - 1
calls = state["calls"]
index = calls if calls < total else start + (calls - total) % (total - start)
state["calls"] += 1
state["argv"].append(sys.argv[1:])
with open(path, "w") as handle:
    json.dump(state, handle)
response = state["responses"][index]
if "__sleep__" in response:
    time.sleep(response["__sleep__"])
if wake_at := response.pop("__sleep_until__", None):
    time.sleep(max(0, wake_at - time.time()))
if "__exit__" in response:
    sys.stderr.write(response.get("stderr", ""))
    sys.exit(response["__exit__"])
for alias, history in response.pop("__commit_history__", {{}}).items():
    query = next(arg for arg in sys.argv if arg.startswith("query="))
    count = int(query.split("commits(last: ", 1)[1].split(")", 1)[0])
    response["data"]["repository"][alias]["commits"]["nodes"] = history[-count:]
print(json.dumps(response))
"""
DEFAULT_RATE = {"cost": 1, "remaining": 4000, "resetAt": "2999-01-01T00:00:00Z"}


def item(
    item_id,
    status,
    *,
    assignees=(),
    labels=(),
    state="OPEN",
    blocked_by=None,
    total_blocked_by=None,
    parent=None,
    updated="2026-10-01T00:00:00Z",
    sub_completed=None,
    sub_total=None,
):
    content = {
        "state": state,
        "assignees": {"nodes": [{"login": name} for name in assignees]},
        "labels": {"nodes": [{"name": name} for name in labels]},
    }
    if blocked_by is not None:  # pull requests and drafts omit dependency fields
        content["issueDependenciesSummary"] = {
            "blockedBy": blocked_by,
            "totalBlockedBy": total_blocked_by if total_blocked_by is not None else blocked_by,
        }
        content["parent"] = {"id": parent} if parent else None
    if sub_total is not None:
        content["subIssuesSummary"] = {"completed": sub_completed, "total": sub_total}
    return {
        "id": item_id,
        "updatedAt": updated,
        "fieldValueByName": {"name": status},
        "content": content,
    }


def page(items, *, next_cursor=None, rate=None):
    return {
        "data": {
            "rateLimit": rate or DEFAULT_RATE,
            "node": {
                "items": {
                    "pageInfo": {
                        "hasNextPage": next_cursor is not None,
                        "endCursor": next_cursor,
                    },
                    "nodes": items,
                }
            },
        }
    }


def pull_request(
    sha="abc",
    mergeable="MERGEABLE",
    checks="SUCCESS",
    review="APPROVED",
    state="OPEN",
    review_id=None,
    comment_id=None,
    base="base1",
    contexts=(),
    next_cursor=None,
    total=None,
):
    rollup = None if checks is None else {
        "state": checks,
        "contexts": {
            "totalCount": len(contexts) if total is None else total,
            "nodes": list(contexts),
            "pageInfo": {"hasNextPage": next_cursor is not None, "endCursor": next_cursor},
        },
    }
    return {
        "baseRefOid": base,
        "reviews": {"nodes": [{"id": review_id}] if review_id else []},
        "comments": {"nodes": [{"id": comment_id}] if comment_id else []},
        "state": state,
        "headRefOid": sha,
        "mergeable": mergeable,
        "reviewDecision": review,
        "commits": {"nodes": [{"commit": {"oid": sha, "statusCheckRollup": rollup}}]},
    }


def check_run(check_id, status="IN_PROGRESS", conclusion=None, name="build"):
    return {"__typename": "CheckRun", "id": check_id, "name": name,
            "status": status, "conclusion": conclusion}


def status_context(context_id, state="PENDING"):
    return {"__typename": "StatusContext", "id": context_id, "context": "legacy", "state": state}


def issue(comment_id="IC_1", updated="2026-10-01T00:00:00Z", title="T", body="B"):
    return {
        "title": title,
        "body": body,
        "comments": {"nodes": [{"id": comment_id, "updatedAt": updated}]},
    }


def repository(*, prs=None, issues=None, rate=None):
    records = {f"pr{number}": {"id": f"PR_{number}", "number": number, **value}
               if value is not None else None for number, value in (prs or {}).items()}
    records.update({f"issue{number}": value for number, value in (issues or {}).items()})
    return {"data": {"rateLimit": rate or DEFAULT_RATE, "repository": records}}


def parent_page(node_id, *, children=(), blockers=(), state="OPEN", cursors=None,
                repository_name="acme/repo"):
    cursors = cursors or {}
    connections = {"subIssues": [{"id": x} for x in children],
                   "blockedBy": [{"id": x} for x in blockers],
                   "labels": [{"name": "ready-for-agent"}],
                   "assignees": []}
    return {"data": {"rateLimit": DEFAULT_RATE, "node0": {
        "id": node_id, "url": f"https://github.com/{repository_name}/issues/{int.from_bytes(node_id.encode(), 'big')}",
        "repository": {"nameWithOwner": repository_name}, "state": state,
        "updatedAt": "2026-11-17T00:00:00Z", "parent": None,
        "comments": {"nodes": []},
        **{name: {"nodes": nodes, "pageInfo": {
            "hasNextPage": name in cursors, "endCursor": cursors.get(name)}}
           for name, nodes in connections.items()}}}}


def parent_batch(*pages):
    return {"data": {"rateLimit": DEFAULT_RATE,
                     **{f"node{i}": page["data"]["node0"] for i, page in enumerate(pages)}}}


def iso(delta_seconds):
    moment = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return moment.isoformat()


class WatchProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        gh = root / "bin" / "gh"
        gh.parent.mkdir()
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.root = root
        self.env = {
            **os.environ,
            "PATH": f"{gh.parent}{os.pathsep}{os.environ['PATH']}",
            "FAKE_GH_STATE": str(root / "state.json"),
        }

    def run_script(self, args, responses, timeout=20, loop_from=None):
        state = self.root / "state.json"
        state.write_text(json.dumps(
                {"responses": responses, "calls": 0, "argv": [], "loop_from": loop_from}
            ))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=self.env,
            timeout=timeout,
        )
        self.calls = json.loads(state.read_text())
        return result

    def snapshot(self, responses, *extra):
        result = self.run_script(["snapshot", *COMMON, *extra], responses)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "baseline.json"
        path.write_text(result.stdout)
        return json.loads(result.stdout), path

    def wait(
        self, baseline, responses, *extra, deadline=None, interval="0", loop_from=None
    ):
        result = self.run_script(
            [
                "wait",
                *COMMON,
                "--baseline",
                str(baseline),
                "--deadline",
                deadline or iso(60),
                "--interval",
                interval,
                *extra,
            ],
            responses,
            loop_from=loop_from,
        )
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1, result.stdout + result.stderr)
        return result, json.loads(lines[0])

    def test_snapshot_follows_pagination_and_includes_backlog(self):
        fingerprint, _ = self.snapshot(
            [
                page([item("I1", "Todo", assignees=("zed", "amy"))], next_cursor="C1"),
                page([item("I2", "Backlog", labels=("b", "a"))]),
            ]
        )
        self.assertEqual(set(fingerprint["item"]), {"I1", "I2"})
        self.assertEqual(fingerprint["item"]["I2"]["status"], "Backlog")
        self.assertEqual(fingerprint["item"]["I1"]["assignees"], ["amy", "zed"])
        self.assertEqual(fingerprint["item"]["I2"]["labels"], ["a", "b"])
        self.assertEqual(len(self.calls["argv"]), 2)
        self.assertIn("after=C1", self.calls["argv"][1])

    def test_blocker_count_drop_is_reported(self):
        _, baseline = self.snapshot([page([item("I1", "Todo", blocked_by=1)])])
        _, report = self.wait(
            baseline, [page([item("I1", "Todo", blocked_by=0, total_blocked_by=1)])]
        )
        self.assertEqual(
            report["changes"], [{"kind": "item", "key": "I1", "fields": ["blocked_by"]}]
        )

    def test_total_blocked_by_change_is_reported(self):
        _, baseline = self.snapshot([page([item("I1", "Todo", blocked_by=1)])])
        _, report = self.wait(
            baseline, [page([item("I1", "Todo", blocked_by=1, total_blocked_by=2)])]
        )
        self.assertEqual(
            report["changes"],
            [{"kind": "item", "key": "I1", "fields": ["total_blocked_by"]}],
        )

    def test_parent_removal_is_reported(self):
        _, baseline = self.snapshot(
            [page([item("I1", "Todo", blocked_by=0, parent="P1")])]
        )
        _, report = self.wait(baseline, [page([item("I1", "Todo", blocked_by=0)])])
        self.assertEqual(
            report["changes"], [{"kind": "item", "key": "I1", "fields": ["parent"]}]
        )

    def test_item_without_dependency_fields_fingerprints_as_null(self):
        fingerprint, _ = self.snapshot([page([item("PR1", "Todo")])])
        record = fingerprint["item"]["PR1"]
        for field in ("blocked_by", "total_blocked_by", "parent", "sub_completed", "sub_total"):
            self.assertIsNone(record[field])

    def test_item_updated_at_change_is_reported(self):
        _, baseline = self.snapshot([page([item("I1", "Todo")])])
        _, report = self.wait(
            baseline, [page([item("I1", "Todo", updated="2026-10-02T00:00:00Z")])]
        )
        self.assertEqual(
            report["changes"], [{"kind": "item", "key": "I1", "fields": ["updated"]}]
        )

    def test_sub_issue_completed_change_is_reported(self):
        before = item("I1", "Todo", sub_completed=1, sub_total=3)
        after = item("I1", "Todo", sub_completed=2, sub_total=3)
        _, baseline = self.snapshot([page([before])])
        _, report = self.wait(baseline, [page([after])])
        self.assertEqual(
            report["changes"],
            [{"kind": "item", "key": "I1", "fields": ["sub_completed"]}],
        )

    def test_sub_issue_total_change_is_reported(self):
        before = item("I1", "Todo", sub_completed=1, sub_total=3)
        after = item("I1", "Todo", sub_completed=1, sub_total=4)
        _, baseline = self.snapshot([page([before])])
        _, report = self.wait(baseline, [page([after])])
        self.assertEqual(
            report["changes"],
            [{"kind": "item", "key": "I1", "fields": ["sub_total"]}],
        )

    def test_snapshot_board_from_keeps_prior_board_and_fresh_pull_requests(self):
        _, prior = self.snapshot(
            [page([item("I1", "Todo")]), repository(prs={7: pull_request()})],
            "--pr",
            "7",
        )
        fresh = [
            page([item("I1", "Done")]),
            repository(prs={7: pull_request(sha="new")}),
        ]
        result = self.run_script(
            ["snapshot", *COMMON, "--pr", "7", "--refresh-pr", "7", "--board-from", str(prior)],
            [fresh[1]],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls["calls"], 1)
        self.assertNotIn("ProjectV2", " ".join(self.calls["argv"][0]))
        merged = json.loads(result.stdout)
        self.assertEqual(merged["item"]["I1"]["status"], "Todo")
        self.assertEqual(merged["pullRequest"]["7"]["sha"], "new")
        path = self.root / "merged.json"
        path.write_text(result.stdout)
        _, report = self.wait(path, fresh, "--pr", "7")
        self.assertEqual(
            report["changes"], [{"kind": "item", "key": "I1", "fields": ["status"]}]
        )

    def test_snapshot_board_from_preserves_issue_drift_without_querying_it(self):
        _, prior = self.snapshot(
            [page([]), repository(prs={7: pull_request()}, issues={9: issue()})],
            "--pr", "7", "--issue", "9",
        )
        result = self.run_script(
            ["snapshot", *COMMON, "--pr", "7", "--refresh-pr", "7", "--issue", "9",
             "--board-from", str(prior)],
            [repository(prs={7: pull_request(sha="new")})],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls["calls"], 1)
        self.assertNotIn("issue(number:", " ".join(self.calls["argv"][0]))
        path = self.root / "merged.json"
        path.write_text(result.stdout)
        _, report = self.wait(
            path,
            [page([]), repository(prs={7: pull_request(sha="new")}, issues={9: issue("IC_2")})],
            "--pr", "7", "--issue", "9",
        )
        self.assertEqual(
            report["changes"], [{"kind": "issue", "key": "9", "fields": ["comment"]}]
        )

    def test_snapshot_board_from_without_prs_needs_no_queries(self):
        before, prior = self.snapshot([page([]), repository(issues={9: issue()})], "--issue", "9")
        result = self.run_script(
            ["snapshot", *COMMON, "--issue", "9", "--board-from", str(prior)],
            [{"__exit__": 1, "stderr": "must not query"}],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), before)
        self.assertEqual(self.calls["calls"], 0)

    def test_targeted_replacement_preserves_second_pr_change_for_next_wait(self):
        watch_set = ("--pr", "7", "--pr", "8")
        first = pull_request()
        changed = pull_request(review_id="new-review")
        before, prior = self.snapshot(
            [page([]), repository(prs={7: first, 8: first})], *watch_set
        )
        _, wake = self.wait(
            prior, [page([]), repository(prs={7: changed, 8: first})], *watch_set
        )
        self.assertEqual(wake["changes"], [
            {"kind": "pullRequest", "key": "7", "fields": ["review_id"]}
        ])
        merged, replacement = self.snapshot(
            [repository(prs={7: changed})], *watch_set, "--refresh-pr", "7",
            "--board-from", str(prior),
        )
        self.assertEqual(merged["pullRequest"]["8"], before["pullRequest"]["8"])
        self.assertEqual(self.calls["calls"], 1)
        query = " ".join(self.calls["argv"][0])
        self.assertIn("pullRequest(number: 7)", query)
        self.assertNotIn("pullRequest(number: 8)", query)
        self.assertNotIn("ProjectV2", query)
        _, wake = self.wait(
            replacement, [page([]), repository(prs={7: changed, 8: changed})], *watch_set
        )
        self.assertEqual(wake["changes"], [
            {"kind": "pullRequest", "key": "8", "fields": ["review_id"]}
        ])

    def test_targeted_replacement_reads_new_pr_and_retains_removed_pr(self):
        before, prior = self.snapshot(
            [page([]), repository(prs={7: pull_request(), 8: pull_request()})],
            "--pr", "7", "--pr", "8",
        )
        watch_set = ("--pr", "8", "--pr", "9")
        current = pull_request(sha="new")
        merged, replacement = self.snapshot(
            [repository(prs={9: current})], *watch_set, "--board-from", str(prior)
        )
        self.assertEqual(merged["pullRequest"]["7"], before["pullRequest"]["7"])
        self.assertEqual(merged["pullRequest"]["8"], before["pullRequest"]["8"])
        self.assertEqual(merged["pullRequest"]["9"]["sha"], "new")
        self.assertEqual(self.calls["calls"], 1)
        query = " ".join(self.calls["argv"][0])
        self.assertIn("pullRequest(number: 9)", query)
        self.assertNotIn("pullRequest(number: 8)", query)
        self.assertNotIn("pullRequest(number: 7)", query)
        _, wake = self.wait(
            replacement, [page([]), repository(prs={8: pull_request(), 9: current})], *watch_set
        )
        self.assertEqual(wake["changes"], [
            {"kind": "pullRequest", "key": "7", "fields": ["removed"]}
        ])

    def test_targeted_replacement_with_empty_refresh_set_keeps_existing_pr(self):
        before, prior = self.snapshot(
            [page([]), repository(prs={7: pull_request()})], "--pr", "7"
        )
        merged, _ = self.snapshot([], "--pr", "7", "--board-from", str(prior))
        self.assertEqual(merged, before)
        self.assertEqual(self.calls["calls"], 0)

    def test_refresh_pr_is_only_valid_for_watched_prs_in_targeted_snapshots(self):
        _, prior = self.snapshot([page([])])
        for options, message in (
            (["--pr", "7", "--refresh-pr", "7"], "--refresh-pr requires --board-from"),
            (["--pr", "7", "--board-from", str(prior), "--refresh-pr", "8"],
             "--refresh-pr must be in the --pr watch set"),
        ):
            with self.subTest(options=options):
                result = self.run_script(["snapshot", *COMMON, *options], [])
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout), {"status": "error", "message": message})
                self.assertEqual(self.calls["calls"], 0)
        result = self.run_script(
            ["wait", *COMMON, "--baseline", str(prior), "--deadline", iso(60), "--refresh-pr", "7"],
            [],
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments: --refresh-pr 7", result.stderr)
        self.assertEqual(self.calls["calls"], 0)

    def test_snapshot_board_from_rejects_a_bad_file(self):
        bad = self.root / "bad.json"
        bad.write_text(json.dumps({"status": "error", "message": "boom"}))
        result = self.run_script(
            ["snapshot", *COMMON, "--board-from", str(bad)], [page([])]
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "error")

    def test_agent_label_removal_and_human_restoration_are_wake_signals(self):
        for before, after in ((["ready-for-agent"], []), ([], ["ready-for-agent"])):
            with self.subTest(before=before, after=after):
                _, baseline = self.snapshot([page([item("I1", "In progress",
                    assignees=["chris"], labels=before)])])
                result, report = self.wait(baseline, [page([item("I1", "In progress",
                    assignees=["chris"], labels=after)])])
                self.assertEqual(0, result.returncode)
                self.assertEqual({"status": "changed", "changes": [
                    {"kind": "item", "key": "I1", "fields": ["labels"]}]}, report)

    def test_status_change_reports_changed_item_and_field(self):
        _, baseline = self.snapshot([page([item("I1", "Backlog")])])
        result, report = self.wait(
            baseline,
            [page([item("I1", "Backlog")]), page([item("I1", "Todo")])],
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            report,
            {
                "status": "changed",
                "changes": [{"kind": "item", "key": "I1", "fields": ["status"]}],
            },
        )

    def test_added_and_removed_items_are_reported(self):
        _, baseline = self.snapshot([page([item("I1", "Todo")])])
        _, report = self.wait(baseline, [page([item("I2", "Todo")])])
        self.assertEqual(
            report["changes"],
            [
                {"kind": "item", "key": "I1", "fields": ["removed"]},
                {"kind": "item", "key": "I2", "fields": ["added"]},
            ],
        )

    def test_assignee_order_is_not_a_change(self):
        _, baseline = self.snapshot([page([item("I1", "Todo", assignees=("a", "b"))])])
        _, report = self.wait(
            baseline,
            [
                page([item("I1", "Todo", assignees=("b", "a"))]),
                page([item("I1", "Todo", state="CLOSED", assignees=("a", "b"))]),
            ],
        )
        self.assertEqual(report["changes"][0]["fields"], ["state"])

    def test_unknown_mergeability_is_not_a_change(self):
        responses = [page([item("I1", "Todo")]), repository(prs={7: pull_request()})]
        _, baseline = self.snapshot(responses, "--pr", "7")
        unknown = [
            page([item("I1", "Todo")]),
            repository(prs={7: pull_request(mergeable="UNKNOWN")}),
        ]
        result, report = self.wait(
            baseline,
            [*unknown, *responses],
            "--pr",
            "7",
            deadline=iso(3),
            interval="0.1",
            loop_from=len(unknown),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report, {"status": "deadline"})
        self.assertGreater(self.calls["calls"], 4)

    def test_pull_request_fields_are_reported(self):
        responses = [page([]), repository(prs={7: pull_request()})]
        _, baseline = self.snapshot(responses, "--pr", "7")
        for field, changed in (
            ("state", pull_request(state="MERGED")),
            ("sha", pull_request(sha="new")),
            ("base", pull_request(base="base2")),
            ("checks", pull_request(checks="FAILURE")),
            ("review", pull_request(review="CHANGES_REQUESTED")),
            ("mergeable", pull_request(mergeable="CONFLICTING")),
        ):
            with self.subTest(field=field):
                _, report = self.wait(
                    baseline, [page([]), repository(prs={7: changed})], "--pr", "7"
                )
                self.assertEqual(
                    report["changes"],
                    [{"kind": "pullRequest", "key": "7", "fields": [field]}],
                )

    def test_current_head_check_change_on_later_page_wakes_with_pending_aggregate(self):
        for pending, finished in (
            (check_run("required"), check_run("required", "COMPLETED", "SUCCESS")),
            (status_context("required"), status_context("required", "SUCCESS")),
        ):
            with self.subTest(kind=pending["__typename"]):
                first = repository(prs={
                    7: pull_request(checks="PENDING", contexts=[check_run("optional", name="lint")],
                                    next_cursor="C1", total=2),
                    8: pull_request(),
                })
                before_page = repository(prs={7: pull_request(checks="PENDING", contexts=[pending], total=2)})
                after_page = repository(prs={7: pull_request(checks="PENDING", contexts=[finished], total=2)})
                watch_set = ("--pr", "7", "--pr", "8")
                before, baseline = self.snapshot([page([]), first, before_page], *watch_set)
                pr = before["pullRequest"]["7"]
                self.assertEqual(pr["sha"], "abc")
                self.assertEqual(pr["checks"], "PENDING")
                self.assertEqual(set(pr["check_contexts"]), {"optional", "required"})
                result, wake = self.wait(baseline, [page([]), first, after_page], *watch_set)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(wake, {"status": "changed", "changes": [
                    {"kind": "pullRequest", "key": "7", "fields": ["check_contexts"]}
                ]})
                self.assertEqual(self.calls["calls"], 3)
                self.assertIn("checkAfter=C1", self.calls["argv"][2])
                query = " ".join(self.calls["argv"][2])
                self.assertIn("pullRequest(number: 7)", query)
                self.assertNotIn("pullRequest(number: 8)", query)
                self.assertNotIn("reviews(", query)
                self.assertNotIn("isRequired", query)

    def test_reordered_and_older_head_checks_stay_quiet(self):
        required = check_run("required")
        optional = status_context("optional")

        def with_history(current, older):
            reading = repository(prs={7: current})
            reading["__commit_history__"] = {"pr7": older["commits"]["nodes"] + current["commits"]["nodes"]}
            return reading

        current = pull_request(checks="PENDING", contexts=[required, optional])
        before = with_history(current, pull_request(sha="old", checks="PENDING"))
        _, baseline = self.snapshot([page([]), before], "--pr", "7")
        after = with_history(
            pull_request(checks="PENDING", contexts=[optional, required]),
            pull_request(sha="old", checks="SUCCESS", contexts=[check_run("old", "COMPLETED", "SUCCESS")]),
        )
        wake_after = repository(prs={
            7: pull_request(checks="PENDING", contexts=[required, optional], review_id="new-review")
        })
        result, wake = self.wait(baseline, [page([]), after, page([]), wake_after], "--pr", "7")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(wake["changes"], [
            {"kind": "pullRequest", "key": "7", "fields": ["review_id"]}
        ])
        self.assertEqual(self.calls["calls"], 4)

    def test_empty_and_null_check_rollups_and_old_baseline(self):
        for aggregate in (None, "PENDING"):
            with self.subTest(aggregate=aggregate):
                before, baseline = self.snapshot(
                    [page([]), repository(prs={7: pull_request(checks=aggregate)})], "--pr", "7"
                )
                pr = before["pullRequest"]["7"]
                self.assertEqual(pr["checks"], aggregate)
                self.assertEqual(pr.pop("check_contexts"), {})
                baseline.write_text(json.dumps(before))
                result, wake = self.wait(baseline, [
                    page([]), repository(prs={7: pull_request(checks=aggregate)}),
                    page([]), repository(prs={7: pull_request(checks=aggregate, review_id="new-review")}),
                ], "--pr", "7")
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(wake["changes"], [
                    {"kind": "pullRequest", "key": "7", "fields": ["review_id"]}
                ])

    def test_missing_or_ambiguous_head_commit_returns_error(self):
        older = pull_request(sha="old")["commits"]["nodes"][0]
        latest = pull_request()["commits"]["nodes"][0]
        for nodes in ([], [older], [older, latest], [{"commit": {"statusCheckRollup": None}}]):
            with self.subTest(nodes=nodes):
                record = pull_request()
                record["commits"]["nodes"] = nodes
                result = self.run_script(
                    ["snapshot", *COMMON, "--pr", "7"], [page([]), repository(prs={7: record})]
                )
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(json.loads(result.stdout)["status"], "error")

    def test_rejects_incomplete_or_inconsistent_check_pages(self):
        first = repository(prs={
            7: pull_request(checks="PENDING", contexts=[check_run("optional")], next_cursor="C1", total=3)
        })
        _, baseline = self.snapshot([page([]), repository(prs={7: pull_request()})], "--pr", "7")
        for failure in ("head", "commit", "id", "number", "missing-pr", "missing-page-info",
                        "invalid-page-info", "missing-cursor", "repeated-cursor", "truncated",
                        "duplicate", "null-rollup"):
            with self.subTest(failure=failure):
                second = repository(prs={
                    7: pull_request(checks="PENDING", contexts=[status_context("legacy")],
                                    next_cursor="C2", total=3)
                })
                records = second["data"]["repository"]
                pr = records["pr7"]
                commit = pr["commits"]["nodes"][0]["commit"]
                connection = commit["statusCheckRollup"]["contexts"]
                info = connection["pageInfo"]
                if failure == "head":
                    pr["headRefOid"] = commit["oid"] = "new"
                elif failure == "commit":
                    commit["oid"] = "old"
                elif failure == "id":
                    pr["id"] = "OTHER_PR"
                elif failure == "number":
                    pr["number"] = 8
                elif failure == "missing-pr":
                    del records["pr7"]
                elif failure == "missing-page-info":
                    del connection["pageInfo"]
                elif failure == "invalid-page-info":
                    info["hasNextPage"] = "false"
                elif failure == "missing-cursor":
                    info["endCursor"] = None
                elif failure == "repeated-cursor":
                    info["endCursor"] = "C1"
                elif failure == "truncated":
                    info["hasNextPage"] = False
                elif failure == "duplicate":
                    connection["nodes"] = [check_run("optional")]
                else:
                    commit["statusCheckRollup"] = None
                result, wake = self.wait(baseline, [page([]), first, second], "--pr", "7")
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(wake["status"], "error")
                self.assertNotIn("changes", wake)
                self.assertEqual(self.calls["calls"], 3)

    def test_check_pagination_respects_rate_budget_and_deadline(self):
        first = repository(
            prs={7: pull_request(contexts=[check_run("first")], next_cursor="C1", total=2)},
            rate={"cost": 10, "remaining": 0, "resetAt": iso(3600)},
        )
        _, baseline = self.snapshot([page([]), repository(prs={7: pull_request()})], "--pr", "7")
        result = self.run_script(["snapshot", *COMMON, "--pr", "7"], [page([]), first])
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("rate limit exhausted", json.loads(result.stdout)["message"])
        self.assertEqual(self.calls["calls"], 2)
        result, wake = self.wait(baseline, [page([]), first], "--pr", "7", deadline=iso(2))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(wake, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 2)

    def test_wait_polls_again_after_rate_window_resets_between_check_pages(self):
        current = check_run("build")
        optional = status_context("optional")
        _, baseline = self.snapshot(
            [page([]), repository(prs={7: pull_request(checks="PENDING", contexts=[current, optional])})],
            "--pr", "7",
        )
        old_rate = {"cost": 10, "remaining": 0, "resetAt": iso(-1)}
        new_rate = {"cost": 1, "remaining": 2, "resetAt": iso(3600)}
        first = repository(prs={
            7: pull_request(checks="PENDING", contexts=[current], next_cursor="C1", total=2)
        }, rate=old_rate)
        continuation = repository(prs={
            7: pull_request(checks="PENDING", contexts=[optional], total=2)
        }, rate=new_rate)
        changed = repository(prs={
            7: pull_request(checks="PENDING", contexts=[check_run("build", "COMPLETED", "SUCCESS"), optional])
        }, rate=new_rate)
        result, wake = self.wait(baseline, [page([], rate=old_rate), first, continuation,
                                            page([], rate=new_rate), changed],
                                 "--pr", "7", deadline=iso(3))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(wake, {"status": "changed", "changes": [
            {"kind": "pullRequest", "key": "7", "fields": ["check_contexts"]}
        ]})
        self.assertEqual(self.calls["calls"], 5)

    def test_wait_discards_check_change_completed_after_deadline(self):
        first = repository(prs={
            7: pull_request(checks="PENDING", contexts=[check_run("optional")], next_cursor="C1", total=2)
        })
        pending = repository(prs={
            7: pull_request(checks="PENDING", contexts=[status_context("build")], total=2)
        })
        _, baseline = self.snapshot([page([]), first, pending], "--pr", "7")
        completed = repository(prs={
            7: pull_request(checks="PENDING", contexts=[status_context("build", "SUCCESS")], total=2)
        })
        deadline = datetime.now(timezone.utc) + timedelta(seconds=2)
        # Return the last page after the deadline, within the subprocess timeout floor.
        first["__sleep_until__"] = deadline.timestamp() - 0.7
        completed["__sleep_until__"] = deadline.timestamp() + 0.05
        result, wake = self.wait(baseline, [page([]), first, completed], "--pr", "7",
                                 deadline=deadline.isoformat())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(wake, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 3)

    def test_check_count_requires_an_integer_on_every_page(self):
        options = "--pr", "7"
        for initial, continuation in ((2.0, 2), (2, 2.0), (False, 2), (2, True)):
            with self.subTest(initial=initial, continuation=continuation):
                first = repository(prs={
                    7: pull_request(contexts=[check_run("first")], next_cursor="C1", total=initial)
                })
                second = repository(prs={
                    7: pull_request(contexts=[status_context("second")], total=continuation)
                })
                result = self.run_script(["snapshot", *COMMON, *options], [page([]), first, second])
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("invalid check context count", json.loads(result.stdout)["message"])

    def test_new_review_is_reported_when_decision_is_unchanged(self):
        before = pull_request(review="CHANGES_REQUESTED", review_id="R1")
        _, baseline = self.snapshot([page([]), repository(prs={7: before})], "--pr", "7")
        after = pull_request(review="CHANGES_REQUESTED", review_id="R2")
        _, report = self.wait(
            baseline, [page([]), repository(prs={7: after})], "--pr", "7"
        )
        self.assertEqual(
            report["changes"],
            [{"kind": "pullRequest", "key": "7", "fields": ["review_id"]}],
        )

    def test_new_conversation_comment_is_reported(self):
        before = pull_request(comment_id="C1")
        _, baseline = self.snapshot([page([]), repository(prs={7: before})], "--pr", "7")
        after = pull_request(comment_id="C2")
        _, report = self.wait(
            baseline, [page([]), repository(prs={7: after})], "--pr", "7"
        )
        self.assertEqual(
            report["changes"],
            [{"kind": "pullRequest", "key": "7", "fields": ["comment_id"]}],
        )

    def test_unchanged_polls_are_silent_until_an_actionable_change(self):
        quiet = [page([]), repository(prs={7: pull_request(checks="PENDING")})]
        _, baseline = self.snapshot(quiet, "--pr", "7")
        for field, changed in (
            ("checks", pull_request(checks="FAILURE")),
            ("checks", pull_request(checks="SUCCESS")),
            ("review_id", pull_request(checks="PENDING", review_id="R2")),
            ("comment_id", pull_request(checks="PENDING", comment_id="C2")),
            ("state", pull_request(checks="PENDING", state="MERGED")),
        ):
            with self.subTest(field=field, changed=changed):
                result, report = self.wait(
                    baseline,
                    quiet * 5 + [page([]), repository(prs={7: changed})],
                    "--pr", "7",
                )
                self.assertEqual(result.returncode, 0)
                self.assertEqual(
                    report,
                    {"status": "changed", "changes": [
                        {"kind": "pullRequest", "key": "7", "fields": [field]}
                    ]},
                )
                # One terminal line, on the first changed poll after five silent polls.
                self.assertEqual(self.calls["calls"], 12)

    def test_failure_after_unchanged_polls_reports_immediately(self):
        quiet = [page([])]
        _, baseline = self.snapshot(quiet)
        result, report = self.wait(
            baseline, quiet * 5 + [{"__exit__": 1, "stderr": "boom"}]
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "error")
        self.assertEqual(self.calls["calls"], 6)

    def test_pull_request_without_reviews_or_comments_fingerprints_as_null(self):
        fingerprint, _ = self.snapshot(
            [page([]), repository(prs={7: pull_request()})], "--pr", "7"
        )
        record = fingerprint["pullRequest"]["7"]
        self.assertIsNone(record["review_id"])
        self.assertIsNone(record["comment_id"])

    def test_new_last_comment_on_watched_issue_is_reported(self):
        responses = [page([]), repository(issues={9: issue()})]
        _, baseline = self.snapshot(responses, "--issue", "9")
        _, report = self.wait(
            baseline,
            [page([]), repository(issues={9: issue(comment_id="IC_2")})],
            "--issue",
            "9",
        )
        self.assertEqual(
            report["changes"], [{"kind": "issue", "key": "9", "fields": ["comment"]}]
        )

    def test_excluded_issue_fields_are_not_a_change(self):
        responses = [page([]), repository(issues={9: issue()})]
        _, baseline = self.snapshot(responses, "--issue", "9")
        _, report = self.wait(
            baseline,
            [
                page([]),
                repository(issues={9: issue(title="Renamed", body="Edited")}),
            ],
            "--issue",
            "9",
            deadline=iso(3),
            interval="0.1",
            loop_from=0,
        )
        self.assertEqual(report, {"status": "deadline"})

    def test_gh_failure_is_an_error_report(self):
        _, baseline = self.snapshot([page([])])
        result, report = self.wait(baseline, [{"__exit__": 1, "stderr": "boom"}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "error")
        self.assertIn("boom", report["message"])

    def test_graphql_errors_are_an_error_report(self):
        _, baseline = self.snapshot([page([])])
        result, report = self.wait(baseline, [{"errors": [{"message": "nope"}]}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "error")

    def test_expired_rate_limit_does_not_sleep(self):
        _, baseline = self.snapshot([page([item("I1", "Backlog")])])
        exhausted = {"cost": 5, "remaining": 1, "resetAt": iso(-60)}
        _, report = self.wait(
            baseline,
            [
                page([item("I1", "Backlog")], rate=exhausted),
                page([item("I1", "Todo")]),
            ],
            interval="0",
        )
        self.assertEqual(report["status"], "changed")

    def test_rate_limit_backs_off_until_reset_capped_at_deadline(self):
        _, baseline = self.snapshot([page([item("I1", "Backlog")])])
        exhausted = {"cost": 5, "remaining": 1, "resetAt": iso(3600)}
        _, report = self.wait(
            baseline,
            [
                page([item("I1", "Backlog")], rate=exhausted),
                page([item("I1", "Todo")]),
            ],
            deadline=iso(3),
            interval="0",
        )
        self.assertEqual(report, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 1)

    def test_past_deadline_reports_deadline_without_fetching(self):
        _, baseline = self.snapshot([page([])])
        _, report = self.wait(baseline, [page([])], deadline=iso(-5))
        self.assertEqual(report, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 0)

    def test_conflicting_after_unknown_baseline_is_reported(self):
        responses = [page([]), repository(prs={7: pull_request(mergeable="UNKNOWN")})]
        _, baseline = self.snapshot(responses, "--pr", "7")
        _, report = self.wait(
            baseline,
            [page([]), repository(prs={7: pull_request(mergeable="CONFLICTING")})],
            "--pr",
            "7",
        )
        self.assertEqual(
            report["changes"],
            [{"kind": "pullRequest", "key": "7", "fields": ["mergeable"]}],
        )

    def test_mergeable_after_unknown_baseline_is_reported(self):
        responses = [page([]), repository(prs={7: pull_request(mergeable="UNKNOWN")})]
        _, baseline = self.snapshot(responses, "--pr", "7")
        _, report = self.wait(
            baseline,
            [page([]), repository(prs={7: pull_request()})],
            "--pr",
            "7",
        )
        self.assertEqual(
            report["changes"],
            [{"kind": "pullRequest", "key": "7", "fields": ["mergeable"]}],
        )

    def test_hung_gh_is_bounded_by_the_deadline(self):
        _, baseline = self.snapshot([page([])])
        started = time.monotonic()
        result, report = self.wait(
            baseline, [{"__sleep__": 30}], deadline=iso(3), interval="0"
        )
        self.assertLess(time.monotonic() - started, 15)
        self.assertIn(report["status"], ("error", "deadline"))
        self.assertEqual(result.returncode, 1 if report["status"] == "error" else 0)

    def test_unknown_status_becoming_todo_is_reported(self):
        _, baseline = self.snapshot([page([item("I1", "UNKNOWN")])])
        _, report = self.wait(baseline, [page([item("I1", "Todo")])])
        self.assertEqual(
            report["changes"], [{"kind": "item", "key": "I1", "fields": ["status"]}]
        )

    def test_rate_limit_sums_cost_across_the_cycle(self):
        reset_at = iso(3600)
        responses = [
            page(
                [item("I1", "Backlog")],
                next_cursor="C1",
                rate={"cost": 1, "remaining": 2, "resetAt": reset_at},
            ),
            page([], rate={"cost": 1, "remaining": 1, "resetAt": reset_at}),
        ]
        _, baseline = self.snapshot(responses)
        _, report = self.wait(baseline, responses, deadline=iso(3), interval="0")
        self.assertEqual(report, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 2)

    def test_wait_stops_fetching_when_budget_resets_after_the_deadline(self):
        _, baseline = self.snapshot([page([item("I1", "Todo")])])
        exhausted = {"cost": 1, "remaining": 0, "resetAt": iso(3600)}
        _, report = self.wait(
            baseline,
            [
                page([item("I1", "Todo")], next_cursor="C1", rate=exhausted),
                page([item("I1", "Done")]),
            ],
            deadline=iso(3),
        )
        self.assertEqual(report, {"status": "deadline"})
        self.assertEqual(self.calls["calls"], 1)

    def test_expired_budget_mid_cycle_continues_without_error(self):
        _, baseline = self.snapshot([page([item("I1", "Todo")])])
        exhausted = {"cost": 1, "remaining": 0, "resetAt": iso(-60)}
        started = time.monotonic()
        _, report = self.wait(
            baseline,
            [
                page([item("I1", "Todo")], next_cursor="C1", rate=exhausted),
                page([item("I2", "Todo")]),
            ],
        )
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(report["status"], "changed")
        self.assertEqual(self.calls["calls"], 2)

    def test_snapshot_errors_instead_of_sleeping_for_the_budget(self):
        exhausted = {"cost": 1, "remaining": 0, "resetAt": iso(3600)}
        started = time.monotonic()
        result = self.run_script(
            ["snapshot", *COMMON],
            [page([item("I1", "Todo")], next_cursor="C1", rate=exhausted), page([])],
        )
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "error")
        self.assertEqual(self.calls["calls"], 1)

    def test_baseline_that_is_not_a_fingerprint_is_an_error(self):
        for content in (
            json.dumps({"status": "error", "message": "boom"}),
            json.dumps({"pullRequest": {}, "issue": {}}),
            "not json",
        ):
            with self.subTest(content=content):
                path = self.root / "bad.json"
                path.write_text(content)
                result, report = self.wait(path, [page([])])
                self.assertEqual(result.returncode, 1)
                self.assertEqual(report["status"], "error")
                self.assertEqual(self.calls["calls"], 0)

    def test_parent_scope_reads_descendants_without_a_project(self):
        responses = [parent_page("ROOT", children=["CHILD"]), parent_page("CHILD")]
        result = self.run_script(["snapshot", "--parent-id", "ROOT",
                                  "--repository", "acme/repo"], responses)
        self.assertEqual(0, result.returncode, result.stdout)
        snapshot = json.loads(result.stdout)
        self.assertEqual(["CHILD", "ROOT"], sorted(snapshot["item"]))
        self.assertEqual(["CHILD"], snapshot["item"]["ROOT"]["subIssues"])
        self.assertEqual([], snapshot["item"]["CHILD"]["blockedBy"])
        for argv in self.calls["argv"]:
            self.assertNotIn("ProjectV2", " ".join(argv))
            self.assertNotIn("mutation", " ".join(argv))

    def parent_snapshot(self, responses):
        return self.run_script(["snapshot", "--parent-id", "ROOT",
                                "--repository", "acme/repo"], responses)

    def test_parent_scope_paginates_graph_and_wakes_on_order_and_dependency_changes(self):
        first = parent_page("ROOT", children=["A"], cursors={"subIssues": "C1"})
        second = parent_page("ROOT", children=["B"])
        responses = [first, second, parent_batch(parent_page("A", blockers=["DEP"]),
                                  parent_page("B")), parent_page("DEP", repository_name="other/repo")]
        before = self.parent_snapshot(responses)
        self.assertEqual(0, before.returncode, before.stdout)
        self.assertIn("subIssues=C1", self.calls["argv"][1])
        baseline = self.root / "parent.json"
        baseline.write_text(before.stdout)
        changed = [parent_page("ROOT", children=["B", "A"]), parent_batch(parent_page("B"),
                                parent_page("A", blockers=["DEP"])),
                   parent_page("DEP", state="CLOSED", repository_name="other/repo")]
        result = self.run_script(["wait", "--parent-id", "ROOT", "--repository", "acme/repo",
                                  "--baseline", str(baseline), "--deadline", iso(60)], changed)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual({"status": "changed", "changes": [
            {"kind": "item", "key": "DEP", "fields": ["state"]},
            {"kind": "item", "key": "ROOT", "fields": ["subIssues"]}]}, json.loads(result.stdout))

    def test_parent_scope_rejects_partial_connections_and_ambiguous_identity(self):
        for connection in ("subIssues", "blockedBy", "labels", "assignees"):
            bad = parent_page("ROOT")
            del bad["data"]["node0"][connection]["pageInfo"]
            with self.subTest(connection=connection):
                result = self.parent_snapshot([bad])
                self.assertEqual(1, result.returncode)
                self.assertEqual("error", json.loads(result.stdout)["status"])
        for responses in (
            [{"data": {"rateLimit": DEFAULT_RATE, "node0": None}}],
            [parent_page("ROOT", repository_name="other/repo")],
            [parent_page("ROOT", children=["A"]), parent_page("A", repository_name="other/repo")],
            [parent_page("ROOT", cursors={"blockedBy": "C"}),
             parent_page("ROOT", cursors={"blockedBy": "C"})],
        ):
            with self.subTest(responses=responses):
                result = self.parent_snapshot(responses)
                self.assertEqual(1, result.returncode, result.stdout)
                self.assertEqual("error", json.loads(result.stdout)["status"])

    def test_parent_scope_paginates_labels_assignees_and_dependencies(self):
        first = parent_page("ROOT", blockers=["D1"], cursors={
            "blockedBy": "D", "labels": "L", "assignees": "A"})
        second = parent_page("ROOT", blockers=["D2"])
        first["data"]["node0"]["assignees"]["nodes"] = [{"login": "chris"}]
        second["data"]["node0"]["labels"]["nodes"] = [{"name": "agent:in-progress"}]
        result = self.parent_snapshot([first, second, parent_batch(parent_page("D1"), parent_page("D2"))])
        self.assertEqual(0, result.returncode, result.stdout)
        root = json.loads(result.stdout)["item"]["ROOT"]
        self.assertEqual(["D1", "D2"], root["blockedBy"])
        self.assertEqual(["agent:in-progress", "ready-for-agent"], root["labels"])
        self.assertEqual(["chris"], root["assignees"])

    def test_parent_scope_detects_membership_replacement_and_authority_changes(self):
        for before, after, expected in (
            (parent_page("ROOT", children=["A"]), parent_page("ROOT", children=["B"]), "subIssues"),
            (parent_page("ROOT", blockers=["A"]), parent_page("ROOT", blockers=["B"]), "blockedBy"),
            (parent_page("ROOT"), parent_page("ROOT"), "labels"),
        ):
            if expected == "labels":
                after["data"]["node0"]["labels"]["nodes"] = []
            initial = self.parent_snapshot([before, parent_page("A")])
            self.assertEqual(0, initial.returncode, initial.stdout)
            baseline = self.root / "parent-change.json"
            baseline.write_text(initial.stdout)
            result = self.run_script(["wait", "--parent-id", "ROOT", "--repository", "acme/repo",
                                      "--baseline", str(baseline), "--deadline", iso(60)],
                                     [after, parent_page("B")])
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertIn({"kind": "item", "key": "ROOT", "fields": [expected]},
                          json.loads(result.stdout)["changes"])

    def test_parent_scope_reads_through_closed_intermediates_and_shared_dependencies(self):
        responses = [parent_page("ROOT", children=["A"], blockers=["B"]),
                     parent_batch(parent_page("B", children=["C"]),
                                  parent_page("A", state="CLOSED", children=["B"])), parent_page("C")]
        result = self.parent_snapshot(responses)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(["A", "B", "C", "ROOT"], sorted(json.loads(result.stdout)["item"]))

    def test_parent_scope_rejects_subissue_cycles_and_duplicate_parent_edges(self):
        for responses in (
            [parent_page("ROOT", children=["A"]), parent_page("A", children=["ROOT"])],
            [parent_page("ROOT", children=["A", "B"]),
             parent_batch(parent_page("A", children=["B"]), parent_page("B"))],
        ):
            result = self.parent_snapshot(responses)
            self.assertEqual(1, result.returncode, result.stdout)
            self.assertEqual("error", json.loads(result.stdout)["status"])

    def test_parent_scope_rejects_missing_readback_and_changed_pagination(self):
        for field in ("comments", "parent", "updatedAt"):
            bad = parent_page("ROOT")
            del bad["data"]["node0"][field]
            result = self.parent_snapshot([bad])
            self.assertEqual(1, result.returncode, (field, result.stdout))
        first = parent_page("ROOT", children=["A"], cursors={"subIssues": "C"})
        second = parent_page("ROOT", children=["B"])
        second["data"]["node0"]["updatedAt"] = "2026-11-18T00:00:00Z"
        result = self.parent_snapshot([first, second])
        self.assertEqual(1, result.returncode)
        self.assertEqual("error", json.loads(result.stdout)["status"])

    def test_parent_scope_batches_wide_graph(self):
        children = [f"CHILD{i}" for i in range(100)]
        responses = [parent_page("ROOT", children=children)]
        responses.extend(parent_batch(*(parent_page(child) for child in children[i:i + 20]))
                         for i in range(0, len(children), 20))
        result = self.parent_snapshot(responses)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(101, len(json.loads(result.stdout)["item"]))
        self.assertEqual(6, self.calls["calls"])
        for argv in self.calls["argv"]:
            query = next(value for value in argv if value.startswith("query="))
            self.assertLessEqual(query.count(": node(id:"), 20)

    def test_parent_scope_batch_preserves_individual_pagination(self):
        result = self.parent_snapshot([
            parent_page("ROOT", children=["A", "B"]),
            parent_batch(parent_page("A", children=["C"], cursors={"subIssues": "NEXT"}),
                         parent_page("B")),
            parent_page("A", children=["D"]),
            parent_batch(parent_page("C"), parent_page("D")),
        ])
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(["C", "D"], json.loads(result.stdout)["item"]["A"]["subIssues"])
        self.assertIn("subIssues=NEXT", self.calls["argv"][2])
        self.assertEqual(4, self.calls["calls"])

    def test_parent_scope_checks_budget_after_batch(self):
        batch = parent_batch(parent_page("A", children=["C"]), parent_page("B"))
        batch["data"]["rateLimit"] = {"cost": 20, "remaining": 0, "resetAt": iso(3600)}
        result = self.parent_snapshot([
            parent_page("ROOT", children=["A", "B"]), batch, parent_page("C"),
        ])
        self.assertEqual(1, result.returncode)
        self.assertIn("rate limit exhausted", json.loads(result.stdout)["message"])
        self.assertEqual(2, self.calls["calls"])

    def test_parent_scope_rejects_missing_batch_member(self):
        result = self.parent_snapshot([
            parent_page("ROOT", children=["A", "B"]), parent_page("A"),
        ])
        self.assertEqual(1, result.returncode)
        self.assertIn("issue B missing", json.loads(result.stdout)["message"])

    def test_queries_are_read_only(self):
        self.snapshot([page([]), repository(prs={7: pull_request()})], "--pr", "7")
        for argv in self.calls["argv"]:
            self.assertEqual(argv[:2], ["api", "graphql"])
            self.assertNotIn("mutation", " ".join(argv))


if __name__ == "__main__":
    unittest.main()
