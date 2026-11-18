import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

from scripts import gitlab_code_host_live_check as check


SENTINEL = "glpat-SENTINEL-never-printed"
P = check.PREFIX


class FakeGitLab:
    """Minimal in-memory fixture project answering the calls the run makes."""

    def __init__(self, *, auto_delete_source=True, pipeline_ready_after=1, account=check.ACCOUNT_ID, trains=None):
        self.account = account
        self.trains = trains
        self.branches = {"main": "MAIN0"}
        self.mrs = {}
        self.discussions = {}
        self.pipeline_reads = {}
        self.auto_delete_source = auto_delete_source
        self.pipeline_ready_after = pipeline_ready_after
        self.log = []
        self.files = {}

    def request(self, method, path, body=None):
        self.log.append((method, path, body))
        path, _, query = path.partition("?")
        rest = path[len(P):] if path.startswith(P) else path
        if (method, path) == ("GET", "user"):
            return 200, {}, {"id": self.account, "username": "operator"}
        if (method, path) == ("GET", "version"):
            return 200, {}, {"version": "19.6.0-pre"}
        if method == "GET" and path in (f"projects/{check.PROJECT_ID}", check.ENCODED_PROJECT):
            return 200, {}, {
                "id": check.PROJECT_ID, "path_with_namespace": check.PROJECT_PATH, "default_branch": "main",
                "merge_method": "merge", "squash_option": "default_off", "merge_trains_enabled": self.trains,
                "only_allow_merge_if_pipeline_succeeds": False,
            }
        if method == "GET" and rest == "protected_branches":
            return 200, {}, [{"name": "main", "push_access_levels": [{"access_level": 40}], "merge_access_levels": [{"access_level": 40}]}]
        if method == "GET" and rest == "approval_rules":
            return 200, {}, []
        if method == "GET" and rest == "approvals":
            return 200, {}, {"approvals_before_merge": 0}
        match = re.fullmatch(r"repository/branches/(.+)", rest)
        if match:
            name = unquote(match.group(1))
            if method == "GET":
                return (200, {}, {"name": name, "commit": {"id": self.branches[name]}}) if name in self.branches else (404, {}, {"message": "404 Branch Not Found"})
            if method == "DELETE":
                return (204, {}, None) if self.branches.pop(name, None) else (404, {}, {"message": "404 Branch Not Found"})
        if method == "POST" and rest == "repository/branches":
            self.branches[body["branch"]] = self.branches[body["ref"]]
            return 201, {}, {"name": body["branch"]}
        if method == "POST" and rest == "repository/commits":
            sha = f"C{len(self.files) + 1}"
            self.files[sha] = [action["file_path"] for action in body["actions"]]
            self.branches[body["branch"]] = sha
            return 201, {}, {"id": sha}
        if rest == "merge_requests" and method == "GET":
            source = re.search(r"source_branch=([^&]+)", query)
            name = unquote(source.group(1)) if source else None
            return 200, {}, [mr for mr in self.mrs.values() if mr["source_branch"] == name]
        if rest == "merge_requests" and method == "POST":
            iid = len(self.mrs) + 1
            self.mrs[iid] = {
                "iid": iid, "title": body["title"], "source_branch": body["source_branch"],
                "target_branch": body["target_branch"], "sha": self.branches[body["source_branch"]],
                "draft": body["title"].startswith("Draft: "), "state": "opened", "has_conflicts": False,
                "source_project_id": check.PROJECT_ID, "target_project_id": check.PROJECT_ID,
            }
            return 201, {}, dict(self.mrs[iid])
        match = re.fullmatch(r"merge_requests/(\d+)(/.*)?", rest)
        if match:
            return self.merge_request(method, int(match.group(1)), match.group(2) or "", body)
        if method == "GET" and rest == "pipelines":
            return 200, {}, []
        return 404, {}, {"message": f"unhandled {method} {path}"}

    def status(self, mr):
        if mr["state"] != "opened":
            return "not_open"
        if mr["draft"]:
            return "draft_status"
        return "mergeable"

    def merge_request(self, method, iid, tail, body):
        mr = self.mrs[iid]
        if method == "GET" and tail == "":
            return 200, {}, dict(mr, detailed_merge_status=self.status(mr))
        if method == "PUT" and tail == "":
            if body.get("state_event") == "close":
                mr["state"] = "closed"
            if "title" in body:
                mr["title"] = body["title"]
                mr["draft"] = body["title"].startswith("Draft: ")
            return 200, {}, dict(mr)
        if method == "GET" and tail == "/closes_issues":
            return 200, {}, []
        if method == "GET" and tail == "/approvals":
            return 200, {}, {"approved_by": []}
        if method == "GET" and tail == "/pipelines":
            reads = self.pipeline_reads[iid] = self.pipeline_reads.get(iid, 0) + 1
            failing = "FAIL_PIPELINE" in self.files.get(mr["sha"], [])
            status = "running" if reads <= self.pipeline_ready_after else ("failed" if failing else "success")
            return 200, {}, [{"id": 500 + iid, "sha": mr["sha"], "status": status}]
        if method == "POST" and tail == "/discussions":
            did = f"d{len(self.discussions) + 1}"
            self.discussions[did] = {"id": did, "notes": [{"body": body["body"], "resolvable": True, "resolved": False}]}
            return 201, {}, self.discussions[did]
        match = re.fullmatch(r"/discussions/(\w+)(/notes)?", tail)
        if match and method == "POST":
            self.discussions[match.group(1)]["notes"].append({"body": body["body"], "resolvable": True, "resolved": False})
            return 201, {}, {}
        if match and method == "PUT":
            for note in self.discussions[match.group(1)]["notes"]:
                note["resolved"] = True
            return 200, {}, self.discussions[match.group(1)]
        if method == "GET" and tail == "/discussions":
            return 200, {}, list(self.discussions.values())
        if method == "PUT" and tail == "/merge":
            if self.status(mr) != "mergeable" or body["sha"] != mr["sha"]:
                return 405, {}, {"message": "405 Method Not Allowed"}
            mr.update(state="merged", merge_commit_sha="M1")
            self.branches[mr["target_branch"]] = "M1"
            if self.auto_delete_source:
                self.branches.pop(mr["source_branch"], None)
            return 200, {}, dict(mr)
        return 404, {}, {"message": f"unhandled {method} {tail}"}


def run(fake, **kwargs):
    client = check.Client(fake, check.Guard("RUN"), sleep=lambda _: None)
    return check.Run(client, "RUN", polls=5, interval=0, **kwargs).execute(), client


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.guard = check.Guard("RUN")
        self.guard.merge_requests.add(5)

    def assert_denied(self, method, path, body=None):
        with self.assertRaises(check.GuardDenied):
            self.guard.check(method, path, body)

    def test_denies_other_projects_main_and_unrecorded_targets(self):
        self.assert_denied("GET", "projects/1/merge_requests")
        self.assert_denied("POST", "projects/1/repository/branches", {"branch": self.guard.base, "ref": "main"})
        self.assert_denied("DELETE", f"{P}repository/branches/main")
        self.assert_denied("POST", f"{P}repository/commits", {"branch": "main", "start_branch": self.guard.base, "commit_message": "x", "actions": []})
        self.assert_denied("POST", f"{P}repository/branches", {"branch": "qual/other", "ref": "main"})
        self.assert_denied("PUT", f"{P}merge_requests/6", {"title": "x"})
        self.assert_denied("POST", f"{P}merge_requests", {"source_branch": "qual/RUN-a", "target_branch": "main", "title": "Draft: x", "description": ""})
        self.assert_denied("GET", f"{P}../1/merge_requests")
        self.assertEqual(0, self.guard.writes)

    def test_denies_auto_merge_merge_trains_and_a_second_merge(self):
        self.assert_denied("PUT", f"{P}merge_requests/5/merge", {"sha": "H", "merge_when_pipeline_succeeds": True})
        self.assert_denied("PUT", f"{P}merge_requests/5/merge", {"sha": "H", "auto_merge": True})
        self.assert_denied("GET", f"{P}merge_trains/merge_requests/5")
        self.assert_denied("POST", f"{P}merge_trains/merge_requests/5", {})
        self.assert_denied("PUT", f"{P}merge_requests/5/merge", {"squash": False})
        self.guard.check("PUT", f"{P}merge_requests/5/merge", {"sha": "H", "squash": False})
        self.assert_denied("PUT", f"{P}merge_requests/5/merge", {"sha": "H"})

    def test_caps_writes_at_sixteen(self):
        for _ in range(check.MAX_WRITES):
            self.guard.check("POST", f"{P}merge_requests/5/discussions", {"body": "x"})
        self.assert_denied("POST", f"{P}merge_requests/5/discussions", {"body": "x"})
        self.assertEqual(check.MAX_WRITES, self.guard.writes)


class TrackerProtocolTest(unittest.TestCase):
    """Check the issue #163 write ledger with an in-memory transport only."""

    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "evals/artifacts/issue-163/r1/qualification-writes.json"
        self.protocol = json.loads(path.read_text())
        self.forward = self.protocol["forward"]
        self.cleanup = self.protocol["cleanup"]
        self.manifest = {
            "targetTitle": "qual/test target", "blockerTitle": "qual/test blocker",
            "stopTitle": "qual/test stop", "fixtureLabels": "autumn,ready-for-agent",
            "claimLabel": "agent:in-progress", "runnerIds": [7],
            "planNote": "approved plan", "baseName": "qual/test-base",
            "sourceName": "qual/test-source", "mainSha": "MAIN", "baseSha": "MAIN",
            "commitMessage": "Qualification sample", "reviewedSha": "H1",
            "createFileAction": [{"action": "create", "file_path": "qualification-test", "content": "test"}],
            "mrTitle": "Qualification", "nonClosingDescription": "Source: https://gitlab.com/banes3/Banes-project/-/issues/42",
            "squash": False,
        }
        self.receipts = {}
        self.attempts = []
        self.confirmed = set()
        self.granted = False
        self.cleaning = False
        self.responses = {}
        self.sent = []
        self.client = check.Client(self, self, sleep=lambda _: None)

    def render(self, row):
        _, method, path, payload = row
        values = self.manifest | self.receipts
        body = None if payload is None else {
            key: values[value[1:]] if isinstance(value, str) and value.startswith("$") else value
            for key, value in payload.items()
        }
        return method, P + path.format_map(self.receipts), body

    def check(self, method, path, body):
        attempted = {name for name in self.attempts}
        if not self.granted or len(attempted) >= self.protocol["maximumAttempts"]:
            raise check.GuardDenied("missing grant or no write allowance")
        if self.cleaning:
            rows = (row for row in self.cleanup if row[0] not in attempted)
        else:
            next_row = len(attempted)
            rows = self.forward[next_row:next_row + 1] if attempted <= self.confirmed else ()
        for row in rows:
            try:
                allowed = self.render(row)
            except KeyError:
                continue  # an unverified creation receipt authorizes no target
            if (method, path, body) == allowed:
                self.attempts.append(row[0])
                return
        raise check.GuardDenied("request has no eligible ledger row")

    def request(self, method, path, body):
        self.sent.append((method, path, body, len(self.attempts)))
        return self.responses.get(path, (204, {}, None))

    def send(self, row):
        return self.client.write(*self.render(row))

    def confirm(self, row):
        self.confirmed.add(row[0])
        created = {
            "create-target": ("target", 42), "create-blocker": ("blocker", 43),
            "create-stop": ("stop", 44), "create-base": ("base", "qual%2Ftest-base"),
            "create-source": ("source", "qual%2Ftest-source"), "open-mr": ("mr", 9),
        }
        if row[0] in created:
            name, identity = created[row[0]]
            self.receipts[name] = identity

    def test_tracker_ledger_refuses_ungranted_and_out_of_scope_writes(self):
        self.assertEqual((check.HOST, check.PROJECT_ID, check.PROJECT_PATH, check.PROTECTED_BASE),
                         tuple(self.protocol[key] for key in ("host", "projectId", "projectPath", "protectedBase")))
        self.assertEqual(0, self.protocol["authorizedWrites"])
        with self.assertRaises(check.GuardDenied):
            self.send(self.forward[0])
        self.granted = True
        for row in self.forward[:2]:
            self.send(row)
            self.confirm(row)
        method, path, body = self.render(self.forward[2])
        for request in [
            (method, path.replace(str(check.PROJECT_ID), "1"), body),
            (method, path.replace("/42/", "/99/"), body),
            (method, path, body | {"target_project_id": 1}),
            (method, path, body | {"target_issue_iid": 99}),
        ]:
            with self.subTest(request=request), self.assertRaises(check.GuardDenied):
                self.client.write(*request)
        self.assertEqual(2, len(self.sent))

    def test_full_forward_ledger_reserves_cleanup_and_refuses_unsafe_merge(self):
        self.granted = True
        for row in self.forward:
            if row[0] in ("open-mr", "merge-at-head"):
                method, path, body = self.render(row)
                if row[0] == "open-mr":
                    extra = ({"target_branch": check.PROTECTED_BASE}, {"source_branch": "existing"})
                else:
                    extra = ({"auto_merge": True}, {"merge_when_pipeline_succeeds": True}, {"sha": "stale"})
                for fields in extra:
                    with self.subTest(fields=fields), self.assertRaises(check.GuardDenied):
                        self.client.write(method, path, body | fields)
            self.send(row)
            self.confirm(row)
        self.assertEqual(15, len(self.attempts))
        self.assertEqual(15, self.protocol["forwardLimit"])
        self.assertEqual(6, self.protocol["cleanupReserve"])
        self.cleaning = True
        with self.assertRaises(check.GuardDenied):
            self.client.write("DELETE", P + "repository/branches/main")
        for row in self.cleanup:
            self.send(row)
        self.assertEqual(21, self.protocol["maximumAttempts"])
        self.assertEqual(list(range(1, 22)), [count for *_, count in self.sent])
        with self.assertRaises(check.GuardDenied):
            self.send(self.cleanup[-1])

    def test_ambiguous_create_halts_forward_and_failed_cleanup_is_not_retried(self):
        self.granted = True
        self.send(self.forward[0])
        self.confirm(self.forward[0])
        self.responses[P + "issues"] = (503, {}, {"message": "unknown create"})
        with self.assertRaises(check.ProviderError):
            self.send(self.forward[1])
        with self.assertRaises(check.GuardDenied):
            self.send(self.forward[1])
        self.assertEqual(["create-target", "create-blocker"], self.attempts)
        self.cleaning = True
        with self.assertRaises(check.GuardDenied):
            self.client.write("DELETE", P + "issues/43")
        self.responses[P + "issues/42"] = (503, {}, {"message": "unknown deletion"})
        with self.assertRaises(check.ProviderError):
            self.send(self.cleanup[-2])
        with self.assertRaises(check.GuardDenied):
            self.send(self.cleanup[-2])
        self.assertEqual(["create-target", "create-blocker", "delete-target"], self.attempts)


class RunTest(unittest.TestCase):
    def test_journeys_pass_within_budget_and_cleanup_tolerates_removed_source(self):
        fake = FakeGitLab(auto_delete_source=True)
        result, _ = run(fake)
        self.assertTrue(result["passed"], result["error"])
        self.assertLessEqual(result["writes"], 14)
        self.assertEqual([], result["guard"]["denied"])
        self.assertTrue(result["cleanup"]["verified"])
        self.assertTrue(result["cleanup"]["main_unchanged"])
        self.assertEqual({"!1": "closed", "!2": "merged"}, {k: v for k, v in result["cleanup"]["outcome"].items() if k.startswith("!")})
        self.assertFalse(result["protected_branch_merge_live_qualified"])
        self.assertEqual(0, result["model_turns"])
        self.assertEqual("MAIN0", fake.branches["main"])
        refused = [step for step in result["steps"] if step["step"] == "merge-refused-while-draft"][0]
        merges = [entry for entry in fake.log if entry[1].endswith("/merge")]
        self.assertEqual(1, len(merges))
        self.assertEqual({"sha": "C2", "squash": False}, merges[0][2])
        self.assertIn("draft_status", refused["reason"])
        deletes = [entry for entry in fake.log if entry[0] == "DELETE"]
        self.assertEqual(2, len(deletes))  # task A and the run base; B was already removed

    def test_cleanup_deletes_source_branch_when_gitlab_keeps_it(self):
        result, _ = run(FakeGitLab(auto_delete_source=False))
        self.assertTrue(result["passed"], result["error"])
        self.assertTrue(all(v != "present" for v in result["cleanup"]["outcome"].values()))

    def test_failure_still_cleans_up_and_reports(self):
        fake = FakeGitLab(pipeline_ready_after=99)
        result, _ = run(fake)
        self.assertFalse(result["passed"])
        self.assertIn("timed out", result["error"])
        self.assertTrue(result["cleanup"]["verified"])
        self.assertEqual({"main"}, set(fake.branches))

    def test_fingerprint_records_tier_gaps_as_unavailable(self):
        digest, inputs = check.fingerprint({"merge_method": "merge", "merge_trains_enabled": None}, [], [], {})
        self.assertEqual("unavailable", inputs["settings"]["merge_trains_enabled"])
        self.assertEqual("unavailable", inputs["settings"]["squash_option"])
        self.assertEqual(64, len(digest))
        changed, _ = check.fingerprint({"merge_method": "ff", "merge_trains_enabled": None}, [], [], {})
        self.assertNotEqual(digest, changed)

    def test_read_failure_is_unknown_not_absent(self):
        class Failing(FakeGitLab):
            def request(self, method, path, body=None):
                if path.endswith("approval_rules?per_page=100&page=1"):
                    return 500, {}, {"message": "boom"}
                return super().request(method, path, body)

        result, client = run(Failing())
        self.assertFalse(result["passed"])
        self.assertIn("HTTP 500", result["error"])
        self.assertEqual(0, result["writes"])
        self.assertEqual(4, len(client.rate_limited))  # four attempts, three retries


class SafetyTest(unittest.TestCase):
    def test_wrong_account_or_merge_trains_refuse_before_any_write(self):
        for fake in (FakeGitLab(account=1), FakeGitLab(trains=True)):
            with self.subTest(fake=fake.account):
                result, _ = run(fake)
                self.assertFalse(result["passed"])
                self.assertEqual(0, result["writes"])
                self.assertEqual({"main": "MAIN0"}, fake.branches)

    def test_unexpected_exception_after_writes_still_cleans_up(self):
        class Breaking(FakeGitLab):
            def request(self, method, path, body=None):
                if method == "POST" and path.endswith("/discussions"):
                    raise KeyError("unexpected response shape")
                return super().request(method, path, body)

        fake = Breaking()
        result, _ = run(fake)
        self.assertFalse(result["passed"])
        self.assertIn("KeyError", result["error"])
        self.assertTrue(result["cleanup"]["verified"])
        self.assertEqual({"main"}, set(fake.branches))
        self.assertEqual("closed", fake.mrs[1]["state"])

    def test_cleanup_continues_after_a_failed_close(self):
        class FailingClose(FakeGitLab):
            def request(self, method, path, body=None):
                if body == {"state_event": "close"}:
                    return 500, {}, {"message": "boom"}
                if method == "POST" and path.endswith("/discussions"):
                    return 500, {}, {"message": "stop the journey early"}
                return super().request(method, path, body)

        fake = FailingClose()
        result, _ = run(fake)
        cleanup = result["cleanup"]
        self.assertFalse(cleanup["verified"])
        self.assertEqual("unknown", cleanup["outcome"]["!1"])
        self.assertIn("HTTP 500", cleanup["failures"]["!1"])
        self.assertEqual({"main"}, set(fake.branches))  # branches still deleted after the failed close
        self.assertTrue(cleanup["main_unchanged"])

    def test_transport_keeps_only_rate_limit_headers_and_maps_timeouts(self):
        output = (
            "HTTP/2.0 429 Too Many Requests\r\nSet-Cookie: session=" + SENTINEL + "\r\n"
            "RateLimit-Remaining: 0\r\nRetry-After: Wed, 21 Oct 2026 07:28:00 GMT\r\n\r\n{\"message\": \"slow down\"}"
        )
        transport = check.GlabTransport("glab")
        completed = check.subprocess.CompletedProcess([], 1, stdout=output, stderr="")
        with patch.object(check.subprocess, "run", return_value=completed):
            status, headers, body = transport.request("GET", "user")
        self.assertEqual(429, status)
        self.assertNotIn(SENTINEL, json.dumps(headers))
        self.assertEqual("0", headers["ratelimit-remaining"])
        client = check.Client(type("T", (), {"request": lambda *_: (status, headers, body)})(), check.Guard("RUN"), sleep=lambda _: None)
        with self.assertRaises(check.ProviderError):
            client.get("user")  # an HTTP-date Retry-After falls back to backoff instead of crashing
        created = check.subprocess.CompletedProcess([], 0, stdout="HTTP/2.0 201 Created\n\n{}", stderr="")
        with patch.object(check.subprocess, "run", return_value=created) as run_glab:
            transport.request("POST", "x", {"body": "note"})
        self.assertEqual(["--input", "-"], run_glab.call_args.args[0][-2:])
        self.assertEqual({"body": "note"}, json.loads(run_glab.call_args.kwargs["input"]))
        with patch.object(check.subprocess, "run", side_effect=check.subprocess.TimeoutExpired("glab", 120)):
            with self.assertRaises(check.CheckError):
                transport.request("GET", "user")


class PreconditionTest(unittest.TestCase):
    def arguments(self, *extra, result=None):
        return ["--result", result or "/nonexistent/result.json", *extra]

    def test_refuses_without_live_relative_path_and_override_variables(self):
        self.assertEqual(2, check.main(self.arguments(), environ={}))
        self.assertEqual(2, check.main(["--live", "--result", "relative.json"], environ={}))
        for name in check.OVERRIDE_VARIABLES:
            with self.subTest(name=name):
                self.assertEqual(2, check.main(self.arguments("--live"), environ={name: SENTINEL}))

    def test_refuses_a_third_write_attempt(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(check.shutil, "which", return_value="/usr/bin/glab"):
            argv = ["--live", "--result", str(Path(directory) / "result.json")]
            for _ in range(check.MAX_ATTEMPTS):
                self.assertEqual(0, check.main(argv, environ={}, transport=FakeGitLab(), sleep=lambda _: None))
            self.assertEqual(2, check.main(argv, environ={}, transport=FakeGitLab(), sleep=lambda _: None))
            self.assertEqual(2, len(json.loads((Path(directory) / "gitlab-live-attempts.json").read_text())))


if __name__ == "__main__":
    unittest.main()
