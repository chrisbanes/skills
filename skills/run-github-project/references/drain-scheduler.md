# Drain Scheduler

Use this scheduler only for `drain`. Keep `next` single-ticket.

## Slot Model

1. Default to three slots. Accept a user-specified limit of one or two; never exceed three.
2. Give each occupied slot one ticket agent, issue, authority lease, warm
   worktree, branch, PR, verified SHA, remote-wait deadline, and fix-round count.
3. Keep every claimed issue `In progress` until merge reconciliation. Derive
   operational state from its slot, PR, checks, and reviews; require no extra
   Project Status values.
4. Reconstruct slots after restart from GitHub claims, Project items, PR heads,
   and verified skill-owned worktrees. Use local caches only as hints.
5. Preserve invalid current-user claims as blocked slots, resume every valid
   claim, then fill free slots. Stop for reconciliation when all claims
   together exceed the invocation's slot limit.
6. Keep one separate planning lane. It preserves assignment and planning
   handoff claims but never consumes one of the three implementation slots.
   Follow [Planning Lane](planning-lane.md) for its worktree, agent, authority,
   handoff, and blocker rules.

## Mutation Lane

Permit exactly one slot agent to mutate local or remote state at a time. Keep
other slot agents idle; read-only work may run concurrently at an immutable SHA.
Invalidate and repeat a review contract whenever its SHA changes.
Keep claims, pushes, merges, and Project mutations under one controller.

Switch slots only after a recoverable checkpoint:

- a complete RED/GREEN vertical slice;
- a completed verification command;
- a clean commit;
- a reconciled push or merge; or
- an explicit preserved stop.

Keep each slot's ticket agent idle between passes; resume it with refreshed
durable state and discard it only when the slot frees, reconstructing if lost.
Descendant agents at any depth use only currently spare agent capacity and
are read-only at immutable SHAs, route findings to the owning ticket or planning
agent, and never own or mutate tickets. An implementation helper yields before
its occupied slot agent must resume. Never preempt a planning agent after
planning starts; queue the implementation event until planning finishes or its
bounded liveness recovery releases capacity.

## Scheduling

Before starting new work, recover and select claim classes in the order defined
by [Planning Lane](planning-lane.md#scheduling).

At every checkpoint, choose one action:

1. Merge the oldest merge-ready slot, unless an explicit dependency requires a
   different order.
2. Service the oldest actionable review or CI event.
3. Resume existing local implementation.
4. Finish a current plan or verified planning handoff.
5. Claim the next ranked `Ready to implement` ticket just in time when a slot
   is free.
6. Start the next ranked `Planning` item when the planning lane and spare agent
   capacity are free.
7. Wait on all remote slots together only when no local action remains.

Never preempt a valid occupied slot for newly higher-priority work. Requery and
rank live data before every just-in-time claim.

Planning runs read-only beside implementation, waits for the mutation lane only
at assignment, comment publication, and Status transitions, and continues to
completion without preemption. Once handed off, the same assigned issue enters
the next available implementation slot. Apply the planning lane's reconciled
three-attempt recovery to planner loss, crash, or timeout; do not classify those
execution failures as semantic blockers.

Do not concurrently claim tickets connected by `blocked by`, a parent-child
relationship, or a declared exclusive resource. Do not guess conflicts from
titles, briefs, or predicted file overlap.

## Remote Waiting

After a reconciled push:

1. Preserve the slot and release the mutation lane.
2. Monitor all PRs without no-op comments or sequential polling.
3. Give that PR a 24-hour deadline from its latest push unless the user or
   repository specifies another duration.
4. Reset only that PR's deadline after a fix push.
5. Return actionable events to the owning slot at the next checkpoint.
6. Block only that slot after three non-converging fix rounds.

Treat the first unexplained CI failure as slot-local. If the same failure
appears in two slots or on the verified base, pause new claims and treat it as
a global failure.

## Merge And Base Drift

Serialize every merge and prefer the configured merge queue. Before merging,
revalidate the slot against the latest base, authority lease, approvals,
terminal-green CI, and mergeability.

After a merge:

1. Reconcile the issue and Project item.
2. Refresh mergeability for every other PR.
3. Update and rerun CI for another branch only when repository policy requires
   the latest base, a conflict appears, or the merge invalidates a tested
   assumption. Never rebase every branch automatically.
4. Snap the merged slot's clean worktree to the verified base and reuse it.
5. Delete only that slot's merged local ticket branch.

## Failure Isolation And Finish Gate

Preserve a ticket-local blocker in its occupied slot and continue unrelated
slots. Stop the whole drain for changed configuration, lost permissions,
invalid base state, merge-policy drift, correlated CI failure, or another
integrity problem that affects every claim.

Finish successfully only when a complete live query is empty and every slot is
free after merge reconciliation. If no runnable work remains but a slot is
blocked or timed out, stop with a partial-drain report, preserve every affected
worktree, branch, PR, assignment, and `In progress` Status, and never report
success.
