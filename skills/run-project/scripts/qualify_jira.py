#!/usr/bin/env python3
"""One guarded, tracker-only qualification against the KAN Jira Cloud fixture."""

import argparse
import base64
from datetime import datetime, timezone
from hashlib import sha256
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import uuid4


SITE = "https://banes-team.atlassian.net"
PROJECT = "KAN"
PROJECT_ID = "10001"
WRITE_LIMIT = 20
CLEANUP_RESERVE = 6
REQUEST_TIMEOUT = 10
RECONCILE_READS = 6
PAGE_LIMIT = 20
FIELDS = "project,summary,issuetype,labels,parent,subtasks,status,assignee,creator"
PERMISSIONS = ("BROWSE_PROJECTS", "CREATE_ISSUES", "DELETE_ISSUES",
               "ASSIGN_ISSUES", "TRANSITION_ISSUES", "ADD_COMMENTS")


class Failure(Exception):
    pass


class RequestFailed(Failure):
    def __init__(self, status=None):
        self.status = status
        super().__init__(f"HTTP {status}" if status else "unknown transport outcome")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def transport(email, token):
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    opener = build_opener(ProxyHandler({}), NoRedirect())

    def request(method, path, *, query=None, body=None):
        url = SITE + "/rest/api/3" + path
        if query:
            url += "?" + urlencode(query)
        headers = {"Authorization": f"Basic {basic}", "Accept": "application/json"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        try:
            with opener.open(Request(url, data=data, headers=headers, method=method),
                             timeout=REQUEST_TIMEOUT) as response:
                raw = response.read()
            return json.loads(raw) if raw else None
        except HTTPError as error:
            raise RequestFailed(error.code) from None
        except (URLError, OSError, ValueError, HTTPException):
            raise RequestFailed() from None

    return request


def numeric_id(value):
    return isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value) is not None


def require(condition, message):
    if not condition:
        raise Failure(message)


def one(values, message):
    require(len(values) == 1, message)
    return values[0]


def paragraph(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


class Qualification:
    def __init__(self, request, record, label, wait=sleep):
        require(re.fullmatch(r"skills-qual-[0-9a-f]{32}", label), "invalid run label")
        self.request = request
        self.record = record
        self.label = label
        self.wait = wait
        self.owned = {}
        self.deleted = set()
        self.sends = 0
        self.cleaning = False
        self.preflight_passed = False
        self.pending_create = None
        self.pending_parent = None

    def get(self, path, **query):
        return self.request("GET", path, query=query)

    def send(self, method, path, *, body=None, query=None):
        require(self.preflight_passed, "write before preflight")
        count = self.sends + 1
        limit = WRITE_LIMIT if self.cleaning else WRITE_LIMIT - CLEANUP_RESERVE
        require(count <= limit, "write budget exhausted")
        if method == "DELETE":
            issue_id = path.removeprefix("/issue/")
            require(self.cleaning and path.startswith("/issue/") and issue_id in self.owned
                    and query == {"deleteSubtasks": "false"},
                    "delete target is outside cleanup scope")
        elif (method, path) == ("POST", "/issue"):
            fields = body["fields"]
            allowed_fields = {"project", "issuetype", "summary", "labels"}
            if self.pending_parent:
                allowed_fields.add("parent")
            require(not self.cleaning and set(body) == {"fields"} and set(fields) == allowed_fields
                    and fields["project"] == {"id": PROJECT_ID}
                    and fields["labels"] == [self.label]
                    and fields["summary"] == self.pending_create
                    and fields["issuetype"].get("id") in self.statuses
                    and fields["issuetype"] == {"id": fields["issuetype"]["id"]}
                    and (not self.pending_parent or
                         fields["parent"] == {"id": self.pending_parent}
                         and self.pending_parent in self.owned), "create scope mismatch")
        else:
            match = re.fullmatch(r"/issue/([0-9]+)/(assignee|transitions|comment)", path)
            require(not self.cleaning and match and match[1] in self.owned and
                    (method, match[2]) in {("PUT", "assignee"), ("POST", "transitions"), ("POST", "comment")},
                    "write target is outside the run")
        details = {}
        if (method, path) == ("POST", "/issue"):
            details["summary"] = body["fields"]["summary"]
        self.record("send", number=count, method=method, path=path, **details)
        self.sends = count
        try:
            result = self.request(method, path, query=query, body=body)
        except RequestFailed as error:
            self.record("response", number=count, status=error.status)
            raise
        self.record("response", number=count, outcome="accepted")
        return result

    def offset_pages(self, path, field):
        values = []
        first_total = None
        seen = set()
        for _ in range(PAGE_LIMIT):
            page = self.get(path, startAt=len(values), maxResults=50)
            items = page[field]
            require(isinstance(items, list) and page["startAt"] == len(values),
                    "invalid offset page")
            for item in items:
                identity = item["fieldId"] if field == "fields" else item["id"]
                require(identity not in seen, "duplicate offset result")
                seen.add(identity)
            values.extend(items)
            total = page.get("total")
            require(type(total) is int and total >= len(values), "invalid offset total")
            if first_total is None:
                first_total = total
            require(total == first_total, "offset total changed")
            if page.get("isLast") is True or len(values) == total:
                require(len(values) == total, "incomplete offset pages")
                return values
            require(items, "empty nonterminal page")
        raise Failure("offset page limit reached")

    def search(self, *, reconcile_id=None):
        query = {"jql": f'project = {PROJECT} AND labels = "{self.label}"',
                 "fields": FIELDS, "maxResults": 50}
        if reconcile_id is not None:
            query["reconcileIssues"] = reconcile_id
        seen_ids = set()
        seen_tokens = set()
        items = []
        for _ in range(PAGE_LIMIT):
            page = self.get("/search/jql", **query)
            require(not page.get("warningMessages"), "incomplete run-label search")
            for item in page["issues"]:
                issue_id = item["id"]
                self.check_identity(item)
                require(issue_id not in seen_ids, "duplicate run-label result")
                seen_ids.add(issue_id)
                items.append(item)
            token = page.get("nextPageToken")
            if page.get("isLast") is True:
                require(not token, "inconsistent last search page")
                return items
            require(isinstance(token, str) and token and token not in seen_tokens,
                    "missing or repeated search token")
            seen_tokens.add(token)
            query["nextPageToken"] = token
        raise Failure("search page limit reached")

    def check_identity(self, issue):
        fields = issue["fields"]
        require(numeric_id(issue["id"]) and re.fullmatch(r"KAN-[1-9][0-9]*", issue["key"])
                and fields["project"]["id"] == PROJECT_ID and self.label in fields["labels"]
                and (fields.get("creator") or {}).get("accountId") == self.account,
                "run issue identity or label mismatch")

    def read_issue(self, issue_id):
        require(issue_id in self.owned, "issue read outside the recorded run")
        item = self.get(f"/issue/{issue_id}", fields=FIELDS)
        self.check_identity(item)
        summary, parent, issue_type = self.owned[issue_id]
        fields = item["fields"]
        require(item["id"] == issue_id and fields["summary"] == summary
                and (fields.get("parent") or {}).get("id") == parent
                and fields["issuetype"]["id"] == issue_type, "recorded issue identity changed")
        return fields

    def preflight(self):
        identity = self.get("/myself")
        self.account = identity["accountId"]
        require(self.account and identity.get("active") is True, "active Jira identity unavailable")
        project = self.get(f"/project/{PROJECT}")
        require((project["key"], project["id"]) == (PROJECT, PROJECT_ID), "fixture identity changed")
        # Jira Software team-managed roles grant Delete any work item for the space.
        require(project.get("style") == "next-gen" and project.get("projectTypeKey") == "software",
                "cannot verify team-managed software delete permission")
        self.check_permissions(projectId=PROJECT_ID)
        types = self.offset_pages(f"/issue/createmeta/{PROJECT}/issuetypes", "issueTypes")
        advertised = project["issueTypes"]
        require(advertised and all(type(item.get("subtask")) is bool for item in advertised),
                "sub-task availability unknown")
        require(all(type(item.get("subtask")) is bool for item in types), "invalid create type metadata")
        standard = one([item for item in types if item["subtask"] is False and item["name"] == "Task"],
                       "expected exactly one creatable Task type")
        subtasks = [item for item in types if item["subtask"] is True]
        advertised_subtasks = {item["id"] for item in advertised if item["subtask"]}
        require(set(item["id"] for item in subtasks) <= advertised_subtasks
                and bool(subtasks) == bool(advertised_subtasks), "sub-task capability unresolved")
        subtasks.sort(key=lambda item: item["id"])
        selected = [standard, *subtasks[:1]]
        statuses = self.get(f"/project/{PROJECT}/statuses")
        self.statuses = {}
        for issue_type in selected:
            type_id = issue_type["id"]
            require(numeric_id(type_id), "invalid create type ID")
            metadata = self.offset_pages(f"/issue/createmeta/{PROJECT}/issuetypes/{type_id}", "fields")
            supplied = {"project", "summary", "issuetype", "labels"}
            if issue_type["subtask"]:
                supplied.add("parent")
            fields = {field["fieldId"]: field for field in metadata}
            require(supplied <= fields.keys(), "required fixture input cannot be set on create")
            require(not any(field["required"] and not field.get("hasDefaultValue")
                            and field["fieldId"] not in supplied for field in metadata),
                    "unhandled required create field")
            workflow = one([row["statuses"] for row in statuses if row["id"] == type_id],
                           "issue-type workflow unavailable")
            self.statuses[type_id] = {
                name: one([status["id"] for status in workflow
                           if status["name"] == name and status["statusCategory"]["key"] == category],
                          f"fixture status unavailable: {name}")
                for name, category in (("To Do", "new"), ("In Progress", "indeterminate"), ("Done", "done"))
                if not issue_type["subtask"] or name != "In Progress"
            }
            require(all(numeric_id(value) for value in self.statuses[type_id].values()),
                    "invalid workflow status ID")
        require(not self.search(), "run label already exists")
        self.record("preflight", site=SITE, project=PROJECT, identity_verified=True,
                    delete_permission=True, sub_tasks=bool(subtasks), statuses=self.statuses)
        self.preflight_passed = True
        return [item["id"] for item in selected]

    def check_permissions(self, **scope):
        names = PERMISSIONS if "projectId" in scope else ("BROWSE_PROJECTS", "DELETE_ISSUES")
        permissions = self.get("/mypermissions", permissions=",".join(names), **scope)["permissions"]
        for name in names:
            require(permissions.get(name, {}).get("havePermission") is True,
                    f"missing {name} permission")

    def find_created(self, summary):
        for attempt in range(1, RECONCILE_READS + 1):
            self.record("reconcile-create", summary=summary, attempt=attempt)
            matches = [item for item in self.search() if item["fields"]["summary"] == summary]
            if matches:
                item = one(matches, "ambiguous run-owned create")
                return item["id"], item["key"]
            if attempt < RECONCILE_READS:
                self.wait(1)
        self.record("unresolved-create", summary=summary, reads=RECONCILE_READS)
        raise Failure("create outcome unknown after scoped reconciliation")

    def create(self, issue_type, parent=None):
        role = "child" if parent else "parent"
        summary = f"{self.label} {role}"
        fields = {"project": {"id": PROJECT_ID}, "issuetype": {"id": issue_type},
                  "summary": summary, "labels": [self.label]}
        if parent:
            fields["parent"] = {"id": parent}
        self.pending_create = summary
        self.pending_parent = parent
        try:
            result = self.send("POST", "/issue", body={"fields": fields})
        except RequestFailed as error:
            if error.status is not None and error.status < 500 and error.status not in (408, 429):
                self.pending_create = None
                self.pending_parent = None
                raise
            result = None
        if (isinstance(result, dict) and numeric_id(result.get("id"))
                and re.fullmatch(r"KAN-[1-9][0-9]*", result.get("key") or "")):
            issue_id, key = result["id"], result["key"]
        else:
            issue_id, key = self.find_created(summary)
        require(issue_id not in self.owned, "create returned a previously owned ID")
        self.owned[issue_id] = (summary, parent, issue_type)
        self.record("created", id=issue_id, key=key, role=role)
        self.pending_create = None
        self.pending_parent = None
        self.read_issue(issue_id)
        self.check_permissions(issueId=issue_id)
        for attempt in range(1, RECONCILE_READS + 1):
            self.record("reconcile-index", id=issue_id, attempt=attempt)
            if any(item["id"] == issue_id and item["fields"]["summary"] == summary
                   for item in self.search(reconcile_id=issue_id)):
                return issue_id
            if attempt < RECONCILE_READS:
                self.wait(1)
        raise Failure("new issue missing from run-label search")

    def transition(self, issue_id, target, before, *, child_ids=None, runner_owned=False):
        path = f"/issue/{issue_id}"
        snapshot = self.read_issue(issue_id)
        require(snapshot["status"]["id"] == before, "status changed before transition")
        transitions = self.get(path + "/transitions", expand="transitions.fields")["transitions"]
        matches = [step for step in transitions if step["to"]["id"] == target
                   and step.get("isAvailable") is True]
        transition = one(matches, "transition skipped: need a single available target")
        fields = transition.get("fields")
        require(isinstance(fields, dict) and all(value.get("required") is False
                for value in fields.values()), "transition skipped: required or unknown fields")
        changelog = path + "/changelog"
        old_ids = {entry["id"] for entry in self.offset_pages(changelog, "values")}
        snapshot = self.read_issue(issue_id)
        require(snapshot["status"]["id"] == before, "status changed before send")
        if runner_owned:
            require((snapshot.get("assignee") or {}).get("accountId") == self.account,
                    "runner assignment changed before transition")
        if child_ids is not None:
            require({item["id"] for item in snapshot["subtasks"]} == child_ids,
                    "parent descendant inventory changed")
            require(all(self.read_issue(child)["status"]["statusCategory"]["key"] == "done"
                        for child in child_ids), "sub-task is not terminal")
        require(numeric_id(transition["id"]), "invalid transition ID")
        self.send("POST", path + "/transitions", body={"transition": {"id": transition["id"]}})
        current = self.read_issue(issue_id)["status"]
        require(current["id"] == target, "transition status readback mismatch")
        edges = [(entry, change) for entry in self.offset_pages(changelog, "values")
                 if entry["id"] not in old_ids for change in entry["items"] if change["field"] == "status"]
        entry, edge = one(edges, "transition changelog attribution is ambiguous")
        require(entry["author"]["accountId"] == self.account and edge["from"] == before
                and edge["to"] == target, "transition changelog attribution mismatch")
        self.record("transition-verified", id=issue_id, previous=before, target=target,
                    changelog=entry["id"], category=current["statusCategory"]["key"])

    def marker(self, issue_id):
        path = f"/issue/{issue_id}/comment"
        text = f"<!-- skills:jira-qualification:v1 -->\n{self.label}\nLine two  \n"
        block = {"type": "codeBlock", "content": [{"type": "text", "text": text}]}
        doc = {"version": 1, "type": "doc", "content": [paragraph("Jira qualification"), block]}
        self.read_issue(issue_id)
        created = self.send("POST", path, body={"body": doc})
        require(numeric_id(created["id"]), "invalid comment identifier")
        comment = self.get(path + "/" + created["id"])
        content = comment["body"]["content"]
        require(len(content) == 2 and content[0] == doc["content"][0]
                and content[1]["type"] == "codeBlock", "ADF marker shape mismatch")
        nodes = content[1]["content"]
        require(all(node["type"] == "text" for node in nodes), "non-text ADF marker payload")
        require(comment["id"] == created["id"] and comment["author"]["accountId"] == self.account
                and "".join(node["text"] for node in nodes) == text, "ADF marker readback mismatch")
        digest = sha256(text.encode()).hexdigest()
        self.record("marker-verified", id=issue_id, comment=comment["id"], digest=digest)

    def journey(self):
        type_ids = self.preflight()
        parent_type = type_ids[0]
        parent = self.create(parent_type)
        child = self.create(type_ids[1], parent=parent) if len(type_ids) == 2 else None
        workflow = self.statuses[parent_type]
        snapshot = self.read_issue(parent)
        require(snapshot["status"]["id"] == workflow["To Do"] and
                (snapshot.get("assignee") or {}).get("accountId") in (None, self.account),
                "parent status or assignment changed before claim")
        self.send("PUT", f"/issue/{parent}/assignee", body={"accountId": self.account})
        self.transition(parent, workflow["In Progress"], workflow["To Do"], runner_owned=True)
        require(self.read_issue(parent)["assignee"]["accountId"] == self.account,
                "claim assignment readback mismatch")
        self.marker(parent)
        if child:
            child_workflow = self.statuses[type_ids[1]]
            self.transition(child, child_workflow["Done"], child_workflow["To Do"])
        self.transition(parent, workflow["Done"], workflow["In Progress"],
                        child_ids={child} if child else set(), runner_owned=True)

    def cleanup(self):
        self.cleaning = True
        clean = self.pending_create is None
        for issue_id in reversed(self.owned):
            try:
                current = self.read_issue(issue_id)
                known_child_unresolved = any(
                    parent == issue_id and child_id not in self.deleted
                    for child_id, (_, parent, _) in self.owned.items()
                )
                require(issue_id != self.pending_parent and not current["subtasks"]
                        and not known_child_unresolved,
                        "delete held for remaining or unreconciled sub-tasks")
                self.check_permissions(issueId=issue_id)
                self.record("cleanup-authority-verified", id=issue_id)
                delete_acknowledged = True
                try:
                    self.send("DELETE", f"/issue/{issue_id}", query={"deleteSubtasks": "false"})
                except RequestFailed as error:
                    if error.status is not None and error.status < 500 and error.status not in (408, 429):
                        raise
                    delete_acknowledged = False
                self.confirm_deleted(issue_id, delete_acknowledged=delete_acknowledged)
            except (Failure, KeyError, TypeError, ValueError) as error:
                clean = False
                message = str(error) if isinstance(error, Failure) else "invalid Jira response shape"
                self.record("cleanup-unverified", id=issue_id, reason=message)
        return clean

    def confirm_deleted(self, issue_id, *, delete_acknowledged):
        for attempt in range(1, RECONCILE_READS + 1):
            self.record("reconcile-delete", id=issue_id, attempt=attempt)
            try:
                self.read_issue(issue_id)
            except RequestFailed as error:
                if error.status == 404:
                    require(delete_acknowledged, "404 after unacknowledged delete cannot verify deletion")
                    self.deleted.add(issue_id)
                    self.record("deleted", id=issue_id, readback=404)
                    return
            if attempt < RECONCILE_READS:
                self.wait(1)
        raise Failure("delete outcome unknown after readback bound")

    def run(self):
        complete = False
        try:
            self.journey()
            complete = True
        except (Failure, KeyError, TypeError, ValueError, KeyboardInterrupt) as error:
            reason = str(error) if isinstance(error, Failure) else "interrupted or invalid Jira response shape"
            self.record("journey-failed", reason=reason)
        finally:
            clean = self.cleanup()
            self.record("finish", journey=complete, cleanup=clean,
                        writes=self.sends, unresolved_ids=sorted(self.owned.keys() - self.deleted),
                        unresolved_create=self.pending_create)
        return complete and clean


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="send Jira requests under a separate maintainer grant")
    parser.add_argument("--result", type=Path, help="new absolute path for the sanitized JSON Lines journal")
    args = parser.parse_args(argv)
    if not args.live:
        print(f"Dry run: {SITE} {PROJECT}, {WRITE_LIMIT} sends, {CLEANUP_RESERVE} reserved for cleanup. "
              "Run-label JQL only, owned issue readbacks and child-first deletion. No requests sent.")
        return 0
    if not args.result or not args.result.is_absolute():
        parser.error("--live requires a new absolute --result path")
    env = tuple(os.environ.get(name) for name in ("JIRA_SITE", "JIRA_EMAIL", "JIRA_API_TOKEN"))
    if env[0] != SITE or not all(env):
        parser.error("provide JIRA_SITE for the pinned fixture, JIRA_EMAIL and JIRA_API_TOKEN")
    try:
        fd = os.open(args.result, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError:
        parser.error("cannot create the new result journal")
    label = "skills-qual-" + uuid4().hex
    with os.fdopen(fd, "w", encoding="utf-8") as journal:
        def record(event, **fields):
            entry = {"time": datetime.now(timezone.utc).isoformat(), "event": event, "run": label, **fields}
            journal.write(json.dumps(entry) + "\n")
            journal.flush()
            os.fsync(journal.fileno())

        record("start", site=SITE, project=PROJECT, write_limit=WRITE_LIMIT,
               cleanup_reserve=CLEANUP_RESERVE, request_timeout_seconds=REQUEST_TIMEOUT,
               reconciliation_reads=RECONCILE_READS, reconciliation_interval_seconds=1)
        passed = Qualification(transport(*env[1:]), record, label).run()
    print(f"{label}: {'passed' if passed else 'incomplete'}; journal {args.result}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
