# Jira Cloud tracker qualification

The maintainer approved one tracker-only run for [issue #159](https://github.com/chrisbanes/skills/issues/159) under the [reviewed plan](https://github.com/chrisbanes/skills/issues/159#issuecomment-6961077522). The run passed on 2026-11-17 from 21:25:55 to 21:26:09 UTC using driver commit `52e2b9e2e5b5cbfd798ee5195ec67ee2d813bc10`.

The authenticated runner verified the Jira Cloud KAN project, project-level delete permission, Task and Sub-task creation metadata, and workflow status IDs before the first write. It used enhanced JQL scoped to `project = KAN AND labels = "skills-qual-af7ed37f53e642b0a3e4a72f58ffe130"`. Direct issue and related API readbacks were limited to the two recorded test issues. Both issues appeared in the scoped search on the first reconciliation read for their respective IDs.

| Check | Readback |
| --- | --- |
| Create parent and child | `KAN-8` (ID `10048`) and `KAN-9` (ID `10049`) both carried the run label, and `KAN-9` referenced the parent. |
| Exercise parent assignment and In Progress transition | The runner's assignment and exact In Progress status `3` matched. Changelog entry `10073` confirmed the transition from To Do `10003`. |
| Round-trip ADF marker | Comment `10033` matched the runner identity and verbatim code block text. Payload SHA-256 was `9a84860a70b14def21fa62b9f16d33fd99a44d0b07b0baa312173cc68e8dc000`. |
| Close sub-task, then parent | Both reached Done `10005`. Changelog entries `10074` and `10075` verified the exact transitions and runner attribution in that order. |
| Delete sub-task, then parent | Jira returned HTTP 404 for `KAN-9` before deletion of `KAN-8`, then returned HTTP 404 for `KAN-8`. |

The run sent nine writes. Seven covered creates, claim, marker and transitions. Two used the cleanup reserve of six. The cap was 20 sends. The run opened zero change requests and ended with zero unresolved effects. Deletion was permanent and the Jira issue keys remain consumed.

The parent transition exercises assignment and status transport. The offline
fixtures verify the controller's gate against claiming a parent with open
descendants.

KAN has no configured Backlog status, so parked behavior was exercised in the deterministic fixtures. Transition skips, a parent validator rejection, external closures, and ADF expand supersession also have offline fixture coverage. This run surfaced no gap in the live operations it exercised.

Review added two safeguards for future runs. The driver now verifies the
team-managed Jira Software project style before trusting the project-level
delete grant, and requires the authenticated runner to be the creator on
issue readback and ambiguous-create recovery. The revised preflight was
rechecked read-only. Fake-transport tests exercise both denial paths. The one
authorized live run used the driver commit above and completed without
ambiguous creates or cleanup failures.

[Atlassian's team-managed permission model](https://support.atlassian.com/jira-software-cloud/docs/next-gen-permissions/)
