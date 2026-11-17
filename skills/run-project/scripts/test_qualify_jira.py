"""Test the KAN write boundary and receipts through a fake Jira v3 transport."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qualify_jira import (
    CLEANUP_RESERVE, PROJECT_ID, RECONCILE_READS, WRITE_LIMIT, Failure,
    Qualification, RequestFailed,
)


LABEL = "skills-qual-" + "a" * 32
TASK = {"id": "1", "name": "Task", "subtask": False}
CHILD = {"id": "2", "name": "Sub-task", "subtask": True}
STATUSES = [
    {"id": "10", "name": "To Do", "statusCategory": {"key": "new"}},
    {"id": "11", "name": "In Progress", "statusCategory": {"key": "indeterminate"}},
    {"id": "12", "name": "Done", "statusCategory": {"key": "done"}},
]
CHILD_DONE = {**STATUSES[-1], "id": "13"}


class JiraFixture:
    def __init__(self, *, sub_tasks=True, denied=None, ambiguous_create=None, ambiguous_delete=None):
        self.types = [TASK, CHILD] if sub_tasks else [TASK]
        self.advertised = self.types
        self.project_style = "next-gen"
        self.denied = denied
        self.ambiguous_create = ambiguous_create
        self.ambiguous_delete = ambiguous_delete
        self.issues = {}
        self.comments = {}
        self.histories = {}
        self.writes = []
        self.searches = []

    def __call__(self, method, path, *, query=None, body=None):
        if method != "GET":
            self.writes.append((method, path))
            return self.write(method, path, query, body)
        return deepcopy(self.read(path, query))

    def page(self, field, values, query):
        start = query["startAt"]
        return {field: values[start:start+1], "startAt": start, "total": len(values)}

    def read(self, path, query):
        if path == "/myself":
            return {"accountId": "runner", "active": True}
        if path == "/project/KAN":
            return {"id": PROJECT_ID, "key": "KAN", "issueTypes": self.advertised,
                    "style": self.project_style, "projectTypeKey": "software"}
        if path == "/mypermissions":
            if "issueId" in query:
                assert query["issueId"] in self.issues
            else:
                assert query["projectId"] == PROJECT_ID
            return {"permissions": {name: {"havePermission": name != self.denied}
                                    for name in query["permissions"].split(",")}}
        if path == "/issue/createmeta/KAN/issuetypes":
            return self.page("issueTypes", self.types, query)
        if path.startswith("/issue/createmeta/KAN/issuetypes/"):
            fields = ["project", "summary", "issuetype", "labels"]
            if path.endswith("/2"):
                fields.append("parent")
            return self.page("fields", [{"fieldId": field, "required": field != "labels"}
                                        for field in fields], query)
        if path == "/project/KAN/statuses":
            return [{"id": "1", "statuses": STATUSES},
                    {"id": "2", "statuses": [STATUSES[0], CHILD_DONE]}]
        if path == "/search/jql":
            assert query["jql"] == f'project = KAN AND labels = "{LABEL}"'
            self.searches.append(query)
            issues = list(self.issues.values())
            if query.get("nextPageToken"):
                assert query["nextPageToken"] == "second-page"
                return {"issues": issues[1:], "isLast": True}
            if len(issues) > 1:
                return {"issues": issues[:1], "nextPageToken": "second-page", "isLast": False}
            return {"issues": issues, "isLast": True}
        _, _, issue_id, *tail = path.split("/")
        if issue_id not in self.issues:
            raise RequestFailed(404)
        if tail == ["transitions"]:
            workflow = STATUSES if issue_id == "21" else (STATUSES[0], CHILD_DONE)
            return {"transitions": [{"id": status["id"], "isAvailable": True,
                                     "to": status, "fields": {}} for status in workflow]}
        if tail == ["changelog"]:
            return self.page("values", self.histories[issue_id], query)
        if tail == ["comment", "88"]:
            return self.comments[issue_id]
        assert not tail, path
        return self.issues[issue_id]

    def write(self, method, path, query, body):
        if method == "POST" and path == "/issue":
            fields = deepcopy(body["fields"])
            assert fields["labels"] == [LABEL] and fields["project"] == {"id": PROJECT_ID}
            if self.ambiguous_create == "missing" or (self.ambiguous_create == "child-missing" and fields.get("parent")):
                raise RequestFailed()
            issue_id = str(21 + len(self.issues))
            parent = fields.get("parent")
            if parent:
                self.issues[parent["id"]]["fields"]["subtasks"].append({"id": issue_id})
            creator = "someone-else" if self.ambiguous_create == "foreign-clone" else "runner"
            fields.update(status=STATUSES[0], subtasks=[], assignee=None,
                          creator={"accountId": creator})
            self.issues[issue_id] = {"id": issue_id, "key": f"KAN-{issue_id}", "fields": fields}
            self.histories[issue_id] = []
            if self.ambiguous_create in ("persisted", "foreign-clone"):
                raise RequestFailed()
            return {"id": issue_id, "key": f"KAN-{issue_id}"}

        _, _, issue_id, *tail = path.split("/")
        fields = self.issues[issue_id]["fields"]
        if method == "DELETE":
            assert query == {"deleteSubtasks": "false"} and not fields["subtasks"]
            if self.ambiguous_delete == "still-present":
                raise RequestFailed()
            if fields.get("parent"):
                parent = self.issues[fields["parent"]["id"]]["fields"]
                parent["subtasks"].remove({"id": issue_id})
            del self.issues[issue_id]
            if self.ambiguous_delete == "deleted":
                raise RequestFailed()
        elif (method, tail) == ("PUT", ["assignee"]):
            fields["assignee"] = body
        elif (method, tail) == ("POST", ["transitions"]):
            status = next(item for item in [*STATUSES, CHILD_DONE]
                          if item["id"] == body["transition"]["id"])
            self.histories[issue_id].append(
                {"id": str(len(self.histories[issue_id]) + 1), "author": {"accountId": "runner"},
                 "items": [{"field": "status", "from": fields["status"]["id"], "to": status["id"]}]}
            )
            fields["status"] = status
        elif (method, tail) == ("POST", ["comment"]):
            self.comments[issue_id] = {"id": "88", "author": {"accountId": "runner"}, **body}
            return {"id": "88"}
        else:
            raise AssertionError((method, path))


class QualificationTests(unittest.TestCase):
    def set_up_run(self, fixture):
        self.events = []
        return Qualification(fixture, lambda event, **info: self.events.append((event, info)),
                             LABEL, wait=lambda seconds: None)

    def test_live_sequence_with_and_without_sub_tasks(self):
        for enabled in (True, False):
            with self.subTest(sub_tasks=enabled):
                fixture = JiraFixture(sub_tasks=enabled)
                run = self.set_up_run(fixture)
                self.assertTrue(run.run(), self.events)
                self.assertFalse(fixture.issues)
                self.assertEqual(9 if enabled else 6, run.sends)
                transitions = [(info["id"], info["target"]) for event, info in self.events
                               if event == "transition-verified"]
                self.assertEqual([("21", "11"), ("22", "13"), ("21", "12")] if enabled
                                 else [("21", "11"), ("21", "12")], transitions)
                deletions = [(info["id"], info["readback"]) for event, info in self.events if event == "deleted"]
                self.assertEqual([("22", 404), ("21", 404)] if enabled else [("21", 404)], deletions)
                self.assertTrue(any(event == "marker-verified" for event, _ in self.events))
                self.assertEqual(len(fixture.writes), sum(event == "send" for event, _ in self.events))
                if enabled:
                    self.assertTrue(any("nextPageToken" in query for query in fixture.searches))

    def test_delete_denial_or_unknown_sub_tasks_stops_before_writes(self):
        denied = JiraFixture(denied="DELETE_ISSUES")
        unknown = JiraFixture()
        unknown.advertised = [TASK, {"id": "2", "name": "Sub-task"}]
        for fixture, reason in [(denied, "DELETE_ISSUES"), (unknown, "sub-task availability")]:
            with self.subTest(reason=reason):
                run = self.set_up_run(fixture)
                self.assertFalse(run.run())
                self.assertEqual([], fixture.writes)
                self.assertIn(reason, str(self.events))

    def test_project_permission_without_team_managed_role_guarantee_cannot_create(self):
        fixture = JiraFixture()
        fixture.project_style = "classic"
        run = self.set_up_run(fixture)
        self.assertFalse(run.run())
        self.assertEqual([], fixture.writes)
        self.assertIn("cannot verify team-managed software delete permission", str(self.events))

    def test_guard_rejects_foreign_targets_and_preserves_cleanup_reserve(self):
        fixture = JiraFixture(sub_tasks=False)
        run = self.set_up_run(fixture)
        run.preflight()
        for method, path in [("POST", "/issue/999/transitions"),
                             ("DELETE", "/issue/999"), ("PUT", "/project/KAN")]:
            with self.subTest(method=method, path=path), self.assertRaises(Failure):
                run.send(method, path)
        self.assertEqual([], fixture.writes)
        issue_id = run.create("1")
        run.sends = WRITE_LIMIT - CLEANUP_RESERVE
        with self.assertRaisesRegex(Failure, "budget"):
            run.send("PUT", f"/issue/{issue_id}/assignee", body={"accountId": "runner"})
        self.assertTrue(run.cleanup())
        self.assertEqual(WRITE_LIMIT - CLEANUP_RESERVE + 1, run.sends)
        run.sends = WRITE_LIMIT
        with self.assertRaisesRegex(Failure, "budget"):
            run.send("DELETE", f"/issue/{issue_id}", query={"deleteSubtasks": "false"})

    def test_unknown_create_recovers_visible_issue_without_sending_again(self):
        fixture = JiraFixture(sub_tasks=False, ambiguous_create="persisted", ambiguous_delete="deleted")
        run = self.set_up_run(fixture)
        self.assertTrue(run.run(), self.events)
        self.assertEqual(1, fixture.writes.count(("POST", "/issue")))
        self.assertEqual(1, fixture.writes.count(("DELETE", "/issue/21")))
        self.assertIn(("deleted", {"id": "21", "readback": 404}), self.events)

    def test_unknown_create_never_adopts_a_matching_foreign_issue(self):
        fixture = JiraFixture(ambiguous_create="foreign-clone")
        run = self.set_up_run(fixture)
        self.assertFalse(run.run())
        self.assertEqual([("POST", "/issue")], fixture.writes)
        self.assertFalse(run.owned)
        self.assertIn("21", fixture.issues)

    def test_unknown_create_preserves_reconciliation_checkpoint(self):
        fixture = JiraFixture(sub_tasks=False, ambiguous_create="missing")
        run = self.set_up_run(fixture)
        self.assertFalse(run.run())
        self.assertEqual([("POST", "/issue")], fixture.writes)
        self.assertEqual(RECONCILE_READS, sum(event == "reconcile-create" for event, _ in self.events))
        event, info = self.events[-1]
        self.assertEqual("finish", event)
        self.assertFalse(info["cleanup"])
        self.assertEqual(f"{LABEL} parent", info["unresolved_create"])

    def test_unreconciled_child_create_holds_parent_deletion(self):
        fixture = JiraFixture(ambiguous_create="child-missing")
        run = self.set_up_run(fixture)
        self.assertFalse(run.run())
        self.assertEqual([("POST", "/issue"), ("POST", "/issue")], fixture.writes)
        self.assertEqual(["21"], self.events[-1][1]["unresolved_ids"])
        self.assertEqual(f"{LABEL} child", self.events[-1][1]["unresolved_create"])

    def test_failed_child_delete_blocks_parent_delete_and_preserves_unresolved_ids(self):
        fixture = JiraFixture(ambiguous_delete="still-present")
        run = self.set_up_run(fixture)
        self.assertFalse(run.run())
        self.assertEqual(1, fixture.writes.count(("DELETE", "/issue/22")))
        self.assertNotIn(("DELETE", "/issue/21"), fixture.writes)
        self.assertEqual(RECONCILE_READS, sum(event == "reconcile-delete" for event, _ in self.events))
        self.assertEqual(["21", "22"], self.events[-1][1]["unresolved_ids"])


if __name__ == "__main__":
    unittest.main()
