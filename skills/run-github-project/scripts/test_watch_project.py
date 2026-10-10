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
if "__exit__" in response:
    sys.stderr.write(response.get("stderr", ""))
    sys.exit(response["__exit__"])
print(json.dumps(response))
"""
DEFAULT_RATE = {"cost": 1, "remaining": 4000, "resetAt": "2999-01-01T00:00:00Z"}


def item(item_id, status, *, assignees=(), labels=(), state="OPEN"):
    return {
        "id": item_id,
        "fieldValueByName": {"name": status},
        "content": {
            "state": state,
            "assignees": {"nodes": [{"login": name} for name in assignees]},
            "labels": {"nodes": [{"name": name} for name in labels]},
        },
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
    sha="abc", mergeable="MERGEABLE", checks="SUCCESS", review="APPROVED", state="OPEN"
):
    return {
        "state": state,
        "headRefOid": sha,
        "mergeable": mergeable,
        "reviewDecision": review,
        "commits": {"nodes": [{"commit": {"statusCheckRollup": {"state": checks}}}]},
    }


def issue(comment_id="IC_1", updated="2026-10-01T00:00:00Z", title="T", body="B"):
    return {
        "title": title,
        "body": body,
        "comments": {"nodes": [{"id": comment_id, "updatedAt": updated}]},
    }


def repository(*, prs=None, issues=None, rate=None):
    records = {f"pr{number}": value for number, value in (prs or {}).items()}
    records.update({f"issue{number}": value for number, value in (issues or {}).items()})
    return {"data": {"rateLimit": rate or DEFAULT_RATE, "repository": records}}


def iso(delta_seconds):
    moment = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


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
            deadline=iso(2),
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
            deadline=iso(1),
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
            deadline=iso(1),
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
            baseline, [{"__sleep__": 30}], deadline=iso(2), interval="0"
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
        responses = [
            page(
                [item("I1", "Backlog")],
                next_cursor="C1",
                rate={"cost": 1, "remaining": 2, "resetAt": iso(3600)},
            ),
            page([], rate={"cost": 1, "remaining": 1, "resetAt": iso(3600)}),
        ]
        _, baseline = self.snapshot(responses)
        _, report = self.wait(baseline, responses, deadline=iso(1), interval="0")
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
            deadline=iso(1),
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

    def test_queries_are_read_only(self):
        self.snapshot([page([]), repository()], "--pr", "7")
        for argv in self.calls["argv"]:
            self.assertEqual(argv[:2], ["api", "graphql"])
            self.assertNotIn("mutation", " ".join(argv))


if __name__ == "__main__":
    unittest.main()
