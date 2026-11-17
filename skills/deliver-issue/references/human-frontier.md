# Epics And Human Frontier

Use this lane for Todo work whose next action belongs to the controller or
a human rather than an implementation agent.

## Classify Work

Treat the configured `epic` label or the binding’s `scopeParent: true` as the
epic work shape; neither supplies a next-action role. Treat the exact
`ready-for-agent`, configured human-work, and configured `needs-triage` labels
as mutually exclusive next-action roles.

Classify an open Todo issue as follows:

| Labels | Result |
| --- | --- |
| Epic only | Unclassified backlog; no automatic closure |
| Epic plus human work | `humanActions` / `perform-human-work` |
| Human work only | `humanActions` / `perform-human-work` |
| Ready for agent only | Todo implementation candidate with a usable active plan; otherwise `plan` |
| Needs triage | `triageCandidates` / `triage` |

Reject `epic` plus `ready-for-agent` and multiple next-action labels. Treat an
Todo issue without a next-action role as human-owned and outside this frontier.
Permit an existing human assignee on human work, but never assign one from this
workflow. Require a Todo candidate or triage item
to have no assignee or open implementation pull request. Use only native open
blockers and descendants as gates. Report a prose-only dependency discrepancy,
but never enforce it.

## Build The Frontier

1. Verify labels, ownership, and native dependencies under the classification
   above. Return unblocked items in the table's collections; return blocked
   items as role-tagged `parkedBlocked`.
2. Rank each collection by the binding’s priority and order, then issue number;
   parent scope uses unset priority and depth-first native sub-issue order.
3. Derive each action's direct unlocks from reverse native blocker and
   parent-child relationships in the complete live graph, never from prose.

Present one ordered frontier packet containing every current human action and
its direct unlocks. Present it when its action, issue, blockers, or direct
unlocks change. Do not repeat an unchanged packet and do not stop autonomous
controller, planning, implementation, monitoring, or triage work merely
because the packet is non-empty.

## Reconcile an epic

Keep `readyEpics` empty when an epic has no next-action role. The shape label
does not authorize closure even after all descendants close. Route a human-
labelled epic to the human frontier and an epic with `needs-triage` to approved
triage; reject an epic carrying `ready-for-agent`. Never manufacture a role
to close an epic. Require an explicit human closure instruction or the triage
provider's approved closure outcome and fresh dependency/ownership reads
before closing through the controller and reconciling Done. For parent scope,
refetch every descendant and native blocker; only a separately authorized root
closure with verified closed readback completes the epic.

## Wait For Human Work

Never assign role-labelled human work, move it to Todo, or close it.
Observe its completion only through refreshed authoritative GitHub state; a
watcher report prompts that refresh but is never the observation.

Return `waiting-for-human` only when no controller, planning, implementation,
monitoring, or non-deferred triage action remains and `humanActions`,
`stoppedItems` or verified authority/decision pauses are non-empty. Include every
stopped item's assignment and retained artifacts, with human label restoration
as its necessary resume condition. Never dispatch a human-work role to an agent. In `drain`, waiting under the
[Project Watcher](drain-scheduler.md#project-watcher) is a monitoring action
until the [finish gate](drain-scheduler.md#failure-isolation-and-finish-gate)
allows the return; `next` returns once its startup merge decision has settled.
This result is resumable and is
neither success nor partial drain.
Report the complete frontier packet, parked dependency chain, and actions that
would become available next.

On a later invocation, reconstruct the frontier from GitHub. Expire all prior
standing mutation authority and resolve the new invocation's merge decision
under [run authority](authority-and-pauses.md): ask a fresh startup question
when this invocation has no explicit merge or no-merge instruction.
Keep uncovered operations paused while the board continues. Use no local
checkpoint as an authority source. Within this invocation, do not repeat the
startup question once it has been asked or its decision otherwise settled.

## Finish Gate

Use the authoritative drain finish gate in
[Drain Scheduler](drain-scheduler.md#failure-isolation-and-finish-gate),
including its partial-drain result for an eligible triage item that the triage
provider cannot complete. Finish successfully only when that gate passes and no
human action remains. Never call a human frontier a failure or successful empty
drain.
