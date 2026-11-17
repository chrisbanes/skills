"""Bounded live check of the GitLab code-host binding (issue #158).

Runs the binding's REST operations through `glab api` against cab's fixture
project only, merging only into a base branch this run creates. Every request
passes a guard that caps writes and refuses anything outside the run's own
branches and merge requests. Requires explicit maintainer authorization and
`--live`; it makes no model calls.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from urllib.parse import quote


HOST = "gitlab.com"
PROJECT_ID = 88319115
PROJECT_PATH = "banes3/Banes-project"
PROTECTED_BASE = "main"
OVERRIDE_VARIABLES = ("GITLAB_TOKEN", "GITLAB_ACCESS_TOKEN", "OAUTH_TOKEN", "GLAB_CONFIG_DIR")
ACCOUNT_ID = 43935395  # fixture operator account from cab's GitLab evidence
MAX_WRITES = 16
MAX_ATTEMPTS = 2
PREFIX = f"projects/{PROJECT_ID}/"
ENCODED_PROJECT = "projects/" + quote(PROJECT_PATH, safe="")
FORBIDDEN_KEYS = ("auto_merge", "merge_when_pipeline_succeeds")
FINGERPRINT_FIELDS = (
    "merge_method", "squash_option", "only_allow_merge_if_pipeline_succeeds",
    "allow_merge_on_skipped_pipeline", "only_allow_merge_if_all_discussions_are_resolved",
    "merge_trains_enabled", "merge_pipelines_enabled",
)


class CheckError(Exception):
    """The run cannot continue; state is preserved for cleanup."""


class GuardDenied(CheckError):
    pass


class ProviderError(CheckError):
    def __init__(self, method, path, status, message):
        super().__init__(f"{method} {path}: HTTP {status}: {message}")
        self.status = status


class Guard:
    """Allow only reads under the fixture and writes to run-recorded targets."""

    def __init__(self, run_id):
        self.base = f"qual/{run_id}-base"
        self.task_branches = {f"qual/{run_id}-a", f"qual/{run_id}-b"}
        self.merge_requests = set()
        self.writes = 0
        self.merges = 0
        self.denied = []

    def deny(self, method, path, reason):
        self.denied.append({"method": method, "path": path, "reason": reason})
        raise GuardDenied(f"guard denied {method} {path}: {reason}")

    def check(self, method, path, body):
        if "merge_trains" in path:
            self.deny(method, path, "merge-train request")
        if ".." in path or "%2e" in path.lower():
            self.deny(method, path, "path traversal")
        if method == "GET":
            if path in ("user", "version", PREFIX.rstrip("/"), ENCODED_PROJECT) or path.startswith(PREFIX):
                return
            self.deny(method, path, "read outside the fixture project")
        if not path.startswith(PREFIX):
            self.deny(method, path, "write outside the fixture project")
        body = body or {}
        if any(key in body for key in FORBIDDEN_KEYS):
            self.deny(method, path, "auto-merge option")
        if self.writes >= MAX_WRITES:
            self.deny(method, path, "write budget exhausted")
        rest = path[len(PREFIX):]
        if not self._allowed(method, rest, body):
            self.deny(method, path, "not a run-recorded target")
        # Counted before sending: a write that errors or is rate-limited still counts.
        self.writes += 1

    def _mr(self, iid):
        return iid.isdigit() and int(iid) in self.merge_requests

    def _allowed(self, method, rest, body):
        if method == "POST" and rest == "repository/branches":
            return body.get("branch") == self.base and body.get("ref") == PROTECTED_BASE and set(body) == {"branch", "ref"}
        if method == "POST" and rest == "repository/commits":
            return (
                set(body) == {"branch", "start_branch", "commit_message", "actions"}
                and body["branch"] in self.task_branches
                and body["start_branch"] == self.base
            )
        if method == "POST" and rest == "merge_requests":
            return (
                set(body) == {"source_branch", "target_branch", "title", "description"}
                and body["source_branch"] in self.task_branches
                and body["target_branch"] == self.base
                and str(body["title"]).startswith("Draft: ")
            )
        if method == "DELETE" and rest.startswith("repository/branches/"):
            branch = rest[len("repository/branches/"):]
            return branch in {quote(name, safe="") for name in (*self.task_branches, self.base)}
        match = re.fullmatch(r"merge_requests/(\d+)(/.*)?", rest)
        if not match or not self._mr(match.group(1)):
            return False
        tail = match.group(2) or ""
        if method == "PUT" and tail == "":
            return set(body) == {"title"} or body == {"state_event": "close"}
        if method == "POST" and tail == "/discussions":
            return set(body) == {"body"}
        if method == "POST" and re.fullmatch(r"/discussions/\w+/notes", tail):
            return set(body) == {"body"}
        if method == "PUT" and re.fullmatch(r"/discussions/\w+", tail):
            return body == {"resolved": True}
        if method == "PUT" and tail == "/merge":
            if self.merges or set(body) - {"sha", "squash"} or "sha" not in body:
                return False
            self.merges += 1
            return True
        return False


class GlabTransport:
    """Send one REST request through `glab api` and return (status, headers, body)."""

    def __init__(self, executable):
        self.executable = executable

    def request(self, method, path, body=None):
        command = [self.executable, "api", "--hostname", HOST, "-i", "-X", method, path]
        with tempfile.TemporaryDirectory() as directory:
            if body is not None:
                payload = Path(directory) / "body.json"
                payload.write_text(json.dumps(body), encoding="utf-8")
                command += ["--input", str(payload), "-H", "Content-Type: application/json"]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as error:
                raise CheckError(f"{method} {path}: glab failed: {type(error).__name__}") from None
        head, _, text = result.stdout.replace("\r\n", "\n").partition("\n\n")
        lines = head.split("\n")
        status_match = re.match(r"HTTP/\S+ (\d{3})", lines[0]) if lines else None
        if not status_match:
            raise CheckError(f"{method} {path}: glab returned no HTTP status (exit {result.returncode})")
        headers = {}
        for line in lines[1:]:
            name, _, value = line.partition(":")
            if name.lower().startswith("ratelimit") or name.lower() in ("retry-after", "x-next-page"):
                headers[name.lower()] = value.strip()
        try:
            parsed = json.loads(text) if text.strip() else None
        except json.JSONDecodeError:
            parsed = {"message": text.strip()[:200]}
        return int(status_match.group(1)), headers, parsed


class Client:
    def __init__(self, transport, guard, sleep=time.sleep):
        self.transport = transport
        self.guard = guard
        self.sleep = sleep
        self.requests = 0
        self.rate_limited = []

    def call(self, method, path, body=None, allow=(200, 201, 202, 204)):
        self.guard.check(method, path, body)
        attempts = 4 if method == "GET" else 1
        for attempt in range(attempts):
            self.requests += 1
            status, headers, parsed = self.transport.request(method, path, body)
            if status in allow:
                return status, parsed, headers
            if status == 429 or status >= 500:
                self.rate_limited.append({"path": path, "status": status, "headers": headers})
                if attempt + 1 < attempts:
                    delay = headers.get("retry-after", "")
                    self.sleep(float(delay) if delay.isdigit() else 2 ** (attempt + 2))
                    continue
            message = parsed.get("message") if isinstance(parsed, dict) else parsed
            raise ProviderError(method, path, status, message)
        raise AssertionError("unreachable")

    def get(self, path, allow=(200,)):
        return self.call("GET", path, allow=allow)[1]

    def get_all(self, path):
        items, page = [], "1"
        separator = "&" if "?" in path else "?"
        while page:
            _, parsed, headers = self.call("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(parsed, list):
                raise CheckError(f"GET {path}: expected a list")
            items += parsed
            page = headers.get("x-next-page", "")
        return items

    def write(self, method, path, body=None, allow=(200, 201, 202, 204)):
        return self.call(method, path, body, allow=allow)[1]


def fingerprint(project, protected, approval_rules, approvals):
    def stable(value):
        return "unavailable" if value is None else value

    rules = [
        {
            "name": rule.get("name"),
            "push": sorted(level.get("access_level") for level in rule.get("push_access_levels", [])),
            "merge": sorted(level.get("access_level") for level in rule.get("merge_access_levels", [])),
            "allow_force_push": stable(rule.get("allow_force_push")),
            "code_owner_approval_required": stable(rule.get("code_owner_approval_required")),
        }
        for rule in protected
        if rule.get("name") == PROTECTED_BASE
    ]
    payload = {
        "base": PROTECTED_BASE,
        "settings": {field: stable(project.get(field)) for field in FINGERPRINT_FIELDS},
        "protection": rules,
        "approval_rules": sorted(
            (
                {
                    "name": rule.get("name"),
                    "rule_type": rule.get("rule_type"),
                    "approvals_required": rule.get("approvals_required"),
                    "eligible": sorted(user.get("id") for user in rule.get("eligible_approvers", [])),
                }
                for rule in approval_rules
            ),
            key=lambda rule: json.dumps(rule, sort_keys=True),
        ),
        "approvals": {
            key: stable(approvals.get(key))
            for key in ("approvals_before_merge", "reset_approvals_on_push", "merge_requests_author_approval")
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), payload


def wait_for(read, done, *, polls, interval, sleep, what):
    for _ in range(polls):
        value = read()
        if done(value):
            return value
        sleep(interval)
    raise CheckError(f"timed out waiting for {what}")


class Run:
    def __init__(self, client, run_id, *, sleep=time.sleep, polls=60, interval=20):
        self.client = client
        self.guard = client.guard
        self.run_id = run_id
        self.sleep = sleep
        self.polls = polls
        self.interval = interval
        self.result = {"run_id": run_id, "host": HOST, "project_id": PROJECT_ID, "model_turns": 0, "steps": []}

    def step(self, name, **facts):
        self.result["steps"].append({"step": name, **facts})

    def mr_path(self, iid, tail=""):
        return f"{PREFIX}merge_requests/{iid}{tail}"

    def preflight(self):
        user = self.client.get("user")
        self.result["account_id"] = user["id"]
        if user["id"] != ACCOUNT_ID:
            raise CheckError(f"glab:{HOST} login is account {user['id']}, not the fixture operator")
        project = self.client.get(f"projects/{PROJECT_ID}")
        by_path = self.client.get(f"projects/{quote(PROJECT_PATH, safe='')}")
        if project["id"] != PROJECT_ID or by_path["id"] != PROJECT_ID or project["path_with_namespace"] != PROJECT_PATH:
            raise CheckError("fixture project identity mismatch")
        if project.get("merge_trains_enabled"):
            raise CheckError("fixture has merge trains enabled; a merge would join a train")
        protected = self.client.get_all(f"{PREFIX}protected_branches")
        approval_rules = self.client.get_all(f"{PREFIX}approval_rules")
        approvals = self.client.get(f"{PREFIX}approvals")
        digest, inputs = fingerprint(project, protected, approval_rules, approvals)
        main = self.client.get(f"{PREFIX}repository/branches/{PROTECTED_BASE}")
        self.result.update(
            version=self.client.get("version").get("version"),
            fingerprint=digest,
            fingerprint_inputs=inputs,
            main_tip_before=main["commit"]["id"],
            protected_branch_merge_live_qualified=False,
        )
        self.step("preflight", writes=self.guard.writes)

    def task(self, branch, file_name, fail):
        actions = [{"action": "create", "file_path": f"qual/{self.run_id}-{file_name}.md", "content": f"{self.run_id}\n"}]
        if fail:
            actions.append({"action": "create", "file_path": "FAIL_PIPELINE", "content": "fail on purpose\n"})
        commit = self.client.write("POST", f"{PREFIX}repository/commits", {
            "branch": branch, "start_branch": self.guard.base,
            "commit_message": f"Qualification {self.run_id} {file_name}", "actions": actions,
        })
        lookup = (
            f"{PREFIX}merge_requests?source_branch={quote(branch, safe='')}"
            f"&target_branch={quote(self.guard.base, safe='')}&state=all"
        )
        if self.client.get_all(lookup):
            raise CheckError(f"unexpected existing merge request for {branch}")
        try:
            mr = self.client.write("POST", f"{PREFIX}merge_requests", {
                "source_branch": branch, "target_branch": self.guard.base,
                "title": f"Draft: Qualification {self.run_id} {file_name}",
                "description": "Source: https://github.com/chrisbanes/skills/issues/158",
            })
        except CheckError:
            # Reconcile an ambiguous create so cleanup can close what exists; never resend it.
            for found in self.client.get_all(lookup):
                self.guard.merge_requests.add(found["iid"])
            raise
        self.guard.merge_requests.add(mr["iid"])
        mr = self.read_mr(mr["iid"])
        if mr["sha"] != commit["id"] or mr["source_project_id"] != PROJECT_ID or mr["target_project_id"] != PROJECT_ID or not mr["draft"]:
            raise CheckError(f"merge request !{mr['iid']} readback mismatch")
        self.check_no_closures(mr["iid"])
        return mr

    def read_mr(self, iid):
        return self.client.get(self.mr_path(iid))

    def check_no_closures(self, iid):
        closes = self.client.get_all(self.mr_path(iid, "/closes_issues"))
        if closes:
            raise CheckError(f"!{iid} would close issues: {[item.get('iid') for item in closes]}")

    def pipeline(self, mr):
        def read():
            pipelines = [p for p in self.client.get_all(self.mr_path(mr["iid"], "/pipelines")) if p.get("sha") == mr["sha"]]
            source = "merge_request"
            if not pipelines:
                source = "sha"
                pipelines = self.client.get_all(f"{PREFIX}pipelines?sha={mr['sha']}")
            return source, pipelines[0] if pipelines else None

        def finished(value):
            return value[1] is not None and value[1]["status"] in ("success", "failed", "canceled", "skipped")

        return wait_for(read, finished, polls=self.polls, interval=self.interval, sleep=self.sleep, what="pipeline")

    def journey_a(self):
        branch = f"qual/{self.run_id}-a"
        mr = self.task(branch, "a", fail=True)
        source, pipeline = self.pipeline(mr)
        if pipeline["status"] != "failed":
            raise CheckError(f"journey A pipeline {pipeline['status']}, expected failed")
        discussion = self.client.write("POST", self.mr_path(mr["iid"], "/discussions"), {"body": "Qualification review note."})
        did = discussion["id"]
        self.client.write("POST", self.mr_path(mr["iid"], f"/discussions/{did}/notes"), {"body": "Addressed in the qualification run."})
        self.client.write("PUT", self.mr_path(mr["iid"], f"/discussions/{did}"), {"resolved": True})
        discussions = self.client.get_all(self.mr_path(mr["iid"], "/discussions"))
        resolved = [d for d in discussions if d["id"] == did and all(n.get("resolved") for n in d["notes"] if n.get("resolvable"))]
        if not resolved or len(resolved[0]["notes"]) != 2:
            raise CheckError("journey A discussion reply/resolve readback failed")
        self.client.get(self.mr_path(mr["iid"], "/approvals"))
        self.step("journey-a", mr=mr["iid"], pipeline=pipeline["id"], pipeline_status="failed", pipeline_source=source, writes=self.guard.writes)
        return mr

    def journey_b(self):
        branch = f"qual/{self.run_id}-b"
        mr = self.task(branch, "b", fail=False)
        refusal = merge_refusal(mr)
        if refusal is None:
            raise CheckError("draft merge request was not refused")
        self.step("merge-refused-while-draft", mr=mr["iid"], reason=refusal, writes=self.guard.writes)
        self.client.write("PUT", self.mr_path(mr["iid"]), {"title": mr["title"].removeprefix("Draft: ")})
        mr = self.read_mr(mr["iid"])
        if mr["draft"]:
            raise CheckError("ready readback still draft")
        source, pipeline = self.pipeline(mr)
        if pipeline["status"] != "success":
            raise CheckError(f"journey B pipeline {pipeline['status']}, expected success")
        mr = wait_for(
            lambda: self.read_mr(mr["iid"]),
            lambda value: value["detailed_merge_status"] not in ("checking", "unchecked", "preparing", "ci_still_running"),
            polls=self.polls, interval=self.interval, sleep=self.sleep, what="merge status",
        )
        refusal = merge_refusal(mr)
        if refusal is not None:
            raise CheckError(f"merge refused: {refusal}")
        self.check_no_closures(mr["iid"])
        expected = mr["sha"]
        self.client.write("PUT", self.mr_path(mr["iid"], "/merge"), {"sha": expected, "squash": False})
        merged = wait_for(
            lambda: self.read_mr(mr["iid"]), lambda value: value["state"] == "merged",
            polls=self.polls, interval=self.interval, sleep=self.sleep, what="merge readback",
        )
        commit = merged.get("merge_commit_sha") or merged.get("squash_commit_sha")
        base = self.client.get(f"{PREFIX}repository/branches/{quote(self.guard.base, safe='')}")
        if merged["sha"] != expected or not commit or base["commit"]["id"] != commit:
            raise CheckError("merge readback mismatch")
        self.step("journey-b", mr=mr["iid"], pipeline=pipeline["id"], pipeline_source=source, merged_head=expected, merge_commit=commit, writes=self.guard.writes)
        return merged

    def cleanup(self):
        outcome = {}
        for iid in sorted(self.guard.merge_requests):
            mr = self.read_mr(iid)
            if mr["state"] == "opened":
                self.client.write("PUT", self.mr_path(iid), {"state_event": "close"})
                mr = self.read_mr(iid)
            outcome[f"!{iid}"] = mr["state"]
        for branch in sorted(self.guard.task_branches) + [self.guard.base]:
            path = f"{PREFIX}repository/branches/{quote(branch, safe='')}"
            status, _, _ = self.client.call("GET", path, allow=(200, 404))
            if status == 200:
                # GitLab may already have removed a merged source branch; 404 counts as removed.
                self.client.write("DELETE", path, allow=(204, 404))
            status, _, _ = self.client.call("GET", path, allow=(200, 404))
            outcome[branch] = "deleted" if status == 404 else "present"
        main = self.client.get(f"{PREFIX}repository/branches/{PROTECTED_BASE}")
        verified = (
            all(value in ("closed", "merged", "deleted") for value in outcome.values())
            and main["commit"]["id"] == self.result.get("main_tip_before")
        )
        self.result["cleanup"] = {"outcome": outcome, "main_unchanged": main["commit"]["id"] == self.result.get("main_tip_before"), "verified": verified}
        return verified

    def execute(self):
        error = None
        try:
            self.preflight()
            self.client.write("POST", f"{PREFIX}repository/branches", {"branch": self.guard.base, "ref": PROTECTED_BASE})
            self.journey_a()
            self.journey_b()
        except Exception as caught:  # any failure after a write must still reach cleanup
            error = caught
        try:
            verified = self.cleanup() if self.guard.writes else True
        except Exception as caught:
            verified = False
            error = error or caught
        self.result.update(
            writes=self.guard.writes,
            requests=self.client.requests,
            rate_limited=self.client.rate_limited,
            guard={"denied": self.guard.denied},
            error=f"{type(error).__name__}: {error}" if error else None,
            passed=error is None and verified and not self.guard.denied,
        )
        return self.result


def merge_refusal(mr):
    """Return GitLab's reason when the binding must refuse to merge, else None."""
    if mr.get("draft"):
        return f"draft ({mr.get('detailed_merge_status')})"
    if mr.get("has_conflicts"):
        return "conflicts"
    if mr.get("detailed_merge_status") != "mergeable":
        return mr.get("detailed_merge_status")
    if mr.get("source_project_id") != PROJECT_ID or mr.get("target_project_id") != PROJECT_ID:
        return "fork merge request"
    return None


def preconditions(arguments, environ):
    if not arguments.live:
        raise CheckError("refusing to run without --live (requires maintainer authorization)")
    result = Path(arguments.result)
    if not result.is_absolute():
        raise CheckError("--result must be an absolute path")
    present = [name for name in OVERRIDE_VARIABLES if environ.get(name)]
    if present:
        raise CheckError(f"refusing to run: {', '.join(present)} would override the glab:{HOST} login")
    executable = shutil.which("glab")
    if not executable:
        raise CheckError("glab is not installed")
    # shortcut: the ledger lives beside --result, so a different directory resets it; keep one result directory per qualification.
    ledger = result.parent / "gitlab-live-attempts.json"
    attempts = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else []
    if len(attempts) >= MAX_ATTEMPTS:
        raise CheckError(f"refusing to run: {len(attempts)} write attempts already recorded in {ledger}")
    return executable, ledger, attempts


def main(argv=None, environ=None, transport=None, sleep=time.sleep):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--live", action="store_true", help="Perform the authorized live writes")
    parser.add_argument("--result", required=True, help="Absolute path for the result JSON")
    arguments = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    try:
        executable, ledger, attempts = preconditions(arguments, environ)
    except CheckError as error:
        print(error, file=sys.stderr)
        return 2
    run_id = time.strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:4]
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps([*attempts, run_id]), encoding="utf-8")
    client = Client(transport or GlabTransport(executable), Guard(run_id), sleep=sleep)
    result = Run(client, run_id, sleep=sleep).execute()
    if not result["writes"]:
        ledger.write_text(json.dumps(attempts), encoding="utf-8")  # a zero-write run is not a write attempt
    Path(arguments.result).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("run_id", "passed", "writes", "error")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
