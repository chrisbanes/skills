# Drain Scheduler

Use this scheduler only for `drain`. Keep `next` single-ticket.

## Slot Model

1. Default to three slots. Accept a user-specified limit of one or two; never
   exceed three. Treat the limit as both the maximum number of claimed,
   in-flight tickets and the maximum number of concurrently active ticket
   agents.
   Define active-agent capacity as the environment-reported number of
   non-controller agents that can run simultaneously. Running ticket agents,
   the planner, and descendants consume it; idle persistent contexts do not.
2. Give each occupied slot one ticket agent, issue, authority lease, warm
   worktree, branch, PR, verified SHA, remote-wait deadline, and fix-round count.
   Start unrelated ticket agents concurrently by default when agent capacity
   permits.
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
   handoff, and blocker rules. Do not reserve agent capacity for Planning;
   start it only from currently spare capacity, then never preempt it.

## Parallel Workers And Controller Lane

Give each ticket agent exclusive ownership of its skill-owned worktree, branch,
and PR. Permit independent ticket agents to edit, test, commit, push different
branch refs, open or update their PRs, reply to review comments, and resolve
addressed threads concurrently. Invalidate and repeat a review contract
whenever that ticket's SHA changes.

Keep one controller lane for just-in-time claims and assignment, Project Status
mutations, slot setup and cleanup, merges or merge-queue admission, issue
closure, and Done reconciliation. Serialize those actions and reconcile every
ambiguous remote mutation before the next controller mutation. Ticket agents
never mutate another slot or the controller-owned Project state.

For each ticket pass, continue through implementation, verification, all review
contracts, a focused commit, and a reconciled push plus PR creation or update.
Then yield durable evidence to the controller and idle that persistent context.
Resume the same agent for actionable feedback or base repair.

### Conflict Admission Gate

Before starting agents concurrently, delay a candidate when it has any of:

- an explicit dependency declared in repository metadata or either approved
  plan, including a `blocked by` or parent-child relationship to an occupied
  ticket;
- a declared exclusive resource shared with an occupied ticket; or
- an exact overlapping path or seam stated in both approved implementation
  plans.

Leave a delayed candidate unclaimed and consider the next ranked runnable
candidate. Never infer a conflict from titles, briefs, predicted scope, or
similarity alone.

When running agents discover a concrete overlap that was absent from their
plans, define the later-claimed slot as younger. Let its agent finish only the
current atomic operation, complete and verify its current vertical slice, and
reach a clean focused commit checkpoint. A reconciled push of that commit is
also valid. If the agent cannot reach a clean commit safely, preserve and block
the younger slot; do not begin automated base repair from a dirty worktree.

After that clean checkpoint, pause the younger slot without releasing its
claim, and revoke its merge eligibility. Merge the older slot first, refresh
the verified base, then resume the younger slot's owning ticket agent. Under
its existing exclusive slot ownership, only that agent may update its branch
and worktree to the new base using repository policy; the controller never
edits the agent-owned branch.

The owning agent must revalidate the authority lease and approved plan, repeat
full applicable verification and every review gate against the updated SHA,
push the exact commit, and reconcile the remote result. Refetch the PR and
require its head SHA to equal that pushed SHA before restoring merge
eligibility or evaluating its new checks and reviews.

If the owning agent is lost or its mutation outcome is ambiguous, stop it when
possible and inspect the worktree, branch HEAD, locks, and active Git processes.
Reconstruct its replacement from that exact clean HEAD only after confirming
the prior agent can no longer mutate them. Otherwise preserve and block the
younger slot.

### Named Resource Locks

Before a command uses a repository-declared or discovered exclusive resource,
derive a canonical non-secret key from its stable identity, such as a device
serial, emulator instance, host and port, or service identity. Never use a
worker-chosen alias.

Keep only `resource key -> (grant ID, holder slot)` in the controller's atomic
registry and durable slot evidence:

1. Grant a free key to one requesting slot; otherwise wait while unrelated work
   continues. Generate a fresh unique grant ID; never start the command without
   its grant.
2. After the command, clear only the entry matching both the holder and grant
   ID, acknowledge release, then reschedule waiting slots. Reject and report a
   stale or mismatched release without clearing the current grant.
3. After worker loss, controller restart, or an ambiguous acquire or release,
   keep the key held until the actual process, device, port, or service is
   confirmed unused.
4. When ownership remains unknown, block only dependent passes and continue
   unrelated work. Never expire or steal a grant by elapsed time.

Keep each slot's ticket agent idle between passes; resume it with refreshed
durable state and discard it only when the slot frees, reconstructing if lost.
Reconcile any named resource grant before reconstructing or resuming a lost
ticket agent.
Descendant agents at any depth use only currently spare agent capacity and
are read-only at immutable SHAs, route findings to the owning ticket or planning
agent, and never own or mutate tickets. An implementation helper yields before
its occupied slot agent must resume. Never preempt a planning agent after
planning starts; queue the implementation event until planning finishes or its
bounded liveness recovery releases capacity.

## Scheduling

Before starting new work, recover and select claim classes in the order defined
by [Planning Lane](planning-lane.md#scheduling).

At every controller event or worker yield, perform all independent runnable
actions that fit the slot and active-agent limits. Exhaust each class before
dispatching the next:

1. Merge the oldest merge-ready slot, unless an explicit dependency requires a
   different order. Admit or merge only one at a time.
2. Resume owning ticket agents for actionable review, CI, or base-repair events
   in oldest-event order.
3. Resume paused local implementation slots in claim order.
4. Finish a current plan or verified planning handoff without preemption.
5. Apply the [Conflict Admission Gate](#conflict-admission-gate), claim ranked
   `Ready to implement` tickets one at a time, and launch unrelated slot agents
   until the in-flight or active-agent limit is reached.
6. Start the next ranked `Planning` item only when the planning lane and active
   agent capacity are free after maximizing runnable implementation.
7. Monitor all remote slots together only when no local or controller action
   remains.

Never preempt a valid occupied slot for newly higher-priority work. Requery and
rank live data before every just-in-time claim.

Planning runs read-only beside implementation, enters the controller lane only
at assignment, comment publication, and Status transitions, and continues to
completion without preemption. Once handed off, the same assigned issue enters
the next available implementation slot. Apply the planning lane's reconciled
three-attempt recovery to planner loss, crash, or timeout; do not classify
those execution failures as semantic blockers.

## Remote Waiting

After a reconciled push:

1. Preserve the slot and verify it holds no named resource grant. Reconcile one
   before entering remote wait.
2. Idle its persistent ticket agent so remote waiting consumes no active-agent
   capacity. Monitor all PRs without no-op comments or sequential polling.
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
   assumption or planned seam. Never rebase every branch automatically.
4. Snap the merged slot's clean worktree to the verified base and reuse it.
5. Delete only that slot's merged local ticket branch.

## Failure Isolation And Finish Gate

Preserve a ticket-local blocker in its occupied slot and continue unrelated
slots. Stop the whole drain for changed configuration, lost permissions,
invalid base state, merge-policy drift, correlated CI failure, or another
integrity problem that affects every claim.

Treat an unexplained scarce-resource collision as slot-local on its first
occurrence. Discover and add the narrow named lock before retrying. Pause new
claims when the same collision or infrastructure failure affects two slots or
the verified base.

Finish successfully only when a complete live query is empty and every slot is
free after merge reconciliation. If no runnable work remains but a slot is
blocked or timed out, stop with a partial-drain report, preserve every affected
worktree, branch, PR, assignment, and `In progress` Status, and never report
success.
