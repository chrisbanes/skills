# Epics And Human Frontier

Use this lane for Backlog work whose next action belongs to the controller or
a human rather than an implementation agent.

## Classify Work

Treat the configured `epic` label as the work shape. Treat the exact
`ready-for-agent`, configured human-work, and configured `needs-triage` labels
as mutually exclusive next-action roles.

Classify an open Backlog issue as follows:

| Labels | Result |
| --- | --- |
| Epic only | Closeable epic after native dependencies clear |
| Epic plus human work | Human epic after native dependencies clear |
| Human work only | Human action after native dependencies clear |
| Ready for agent only | Human Planning authorization after native dependencies clear |
| Needs triage | Existing triage lane after native dependencies clear |

Reject `epic` plus `ready-for-agent` and multiple next-action labels. Treat an
unlabelled non-epic Backlog issue as human-owned and outside this frontier.
Permit an existing human assignee on human work, but never assign one from this
workflow. Require a bare epic, Planning authorization request, or triage item
to have no assignee or open implementation pull request. Use only native open
blockers and descendants as gates. Report a prose-only dependency discrepancy,
but never enforce it.

## Build The Frontier

1. Rank ready epics, human actions, and parked work by Priority, visible
   Project position, then issue number.
2. Return a bare unblocked epic as `readyEpics` with action `close-epic`.
3. Return unblocked human work as `humanActions` with action
   `perform-human-work`.
4. Return an unblocked Backlog `ready-for-agent` issue as `humanActions` with
   action `move-to-planning`.
5. Return a dependency-blocked item as role-tagged `parkedBlocked`.
6. Derive what each action unlocks from reverse native blocker and parent-child
   relationships in the complete live graph. Do not infer unlocks from prose.

Present one ordered frontier packet containing every current human action and
its direct unlocks. Present it when its action, issue, blockers, or direct
unlocks change. Do not repeat an unchanged packet and do not stop autonomous
controller, planning, implementation, monitoring, or triage work merely
because the packet is non-empty.

## Reconcile A Ready Epic

Enter the controller lane and require standing issue-close authority covering
the epic. Refetch it and require all of:

1. open issue state and configured repository and Project membership;
2. Backlog Status and the configured epic label;
3. no next-action role label, assignee, or open implementation pull request;
4. no native open blocker or descendant; and
5. unchanged configuration digest and verified base.

Close the issue directly with the live descendant and blocker evidence. Treat
an ambiguous response as unknown, refetch before retrying, and never issue a
duplicate close. Reconcile the Project Status and archive state through the
configured Done automation exactly as for a merged issue. Then perform a
complete live Project refresh before selecting more work.

In `next`, reconcile at most one ready epic and finish. In `drain`, reconcile
ready epics serially and continue through newly unlocked work.

## Wait For Human Work

Never assign human work, move it to Planning, close it, or treat conversation
approval as a durable Project transition. Require the configured execution
approver to perform each `move-to-planning` transition. Observe human work
completion only through refreshed authoritative GitHub state.

Return `waiting-for-human` only when no controller, planning, implementation,
monitoring, or non-deferred triage action remains and `humanActions` is
non-empty. This result is resumable and is neither success nor partial drain.
Report the complete frontier packet, parked dependency chain, and actions that
would become available next.

On a later invocation, reconstruct the frontier from GitHub. Expire all prior
standing mutation authority and obtain one fresh confirmation covering the
remaining eligible merges and epic closures. Use no local checkpoint as an
authority source.

## Finish Gate

Use the authoritative drain finish gate in
[Drain Scheduler](drain-scheduler.md#failure-isolation-and-finish-gate),
including its partial-drain result for an eligible triage item that the triage
provider cannot complete. Finish successfully only when that gate passes and no
human action remains. Never call a human frontier a failure or successful empty
drain.
