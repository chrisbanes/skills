# Drain Scheduler

Use this scheduler only for `drain`. Keep `next` single-ticket.

## Slot Model

1. Default to two slots. Accept any positive user-specified limit and impose no
   skill-defined maximum. Treat the limit as both the maximum number of
   occupied implementation slots and the maximum number of concurrently active
   ticket agents. A preserved parked claim is not an occupied slot.
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
4. Reconstruct slots and parked claims after restart through
   [Terminal Required-CI Parking](#terminal-required-ci-parking), using GitHub
   claims and marker records plus verified skill-owned worktrees. Use local
   caches only as hints.
5. Preserve invalid current-user claims as blocked slots, resume every valid
   claim, then fill free slots. Stop for reconciliation when all active and
   blocked-slot claims together exceed the invocation's slot limit.
6. Keep one separate planning lane. It preserves assignment and planning
   handoff claims but never consumes one of the configured implementation slots.
   Follow [Planning Lane](planning-lane.md) for its worktree, agent, authority,
   handoff, and blocker rules. Do not reserve agent capacity for Planning;
   start it only from currently spare capacity, then never preempt it.
7. When an implementation slot requeues for contract-preserving planning,
   release the slot but park its assignment, branch, worktree, PR, dirty work
   and idle ticket context on the planning claim. Restore that same ownership
   when the handoff reacquires a slot. A Backlog handoff instead removes all
   skill-owned artifacts and retains no claim.
8. Apply [Terminal Required-CI Parking](#terminal-required-ci-parking) only to a
   qualifying failure after its repair budget. Parked implementation claims
   consume neither an implementation slot nor agent capacity.
9. Keep Backlog triage as a tail lane. Follow
   the authoritative execution-clear predicate in
   [Backlog Triage Lane](triage-lane.md#dispatch). It consumes no implementation
   slot and processes one issue at a time.
10. Keep ready epics and human actions in the separate
   [Epics And Human Frontier](human-frontier.md). They consume neither a slot
   nor agent capacity. Serialize epic closure in the controller lane, surface
   changed human actions immediately, and continue independent work.
11. Keep configured Wayfinder work in the same single planning lane. Give it
    one durable controller lease, but start a fresh Wayfinder provider context
    for each non-research child and never reuse that context for another ticket.
    A research batch may fan out the required `research` subagents from spare
    capacity. The controller serializes every Wayfinder assignment, comment,
    closure, map edit, issue creation, Project addition, and dependency mutation.

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

Apply [Route Agents By Task](../SKILL.md#route-agents-by-task) and append its
routing-ledger entry when selecting each persistent ticket agent and helper.
Use the portable default-owner capability for every normal ticket owner and
planner; never infer exceptional capability from topic, scope, plan size,
module count, or language count.

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

1. Finish any interrupted assigned-Backlog cleanup before new claims.
2. Merge the oldest merge-ready slot, unless an explicit dependency requires a
   different order. Admit or merge only one at a time.
3. Reconcile the highest-ranked ready epic with issue-close authority, then
   refresh the complete Project graph before taking another action.
4. Resume owning ticket agents for actionable review, CI, or base-repair events
   in oldest-event order.
5. Resume paused local implementation slots in claim order.
6. Finish a current contract-preserving replan, other plan, or verified
   planning handoff without preemption. Choose preserved replan claims before
   other Planning claims.
7. Apply the [Conflict Admission Gate](#conflict-admission-gate), claim ranked
   `Ready to implement` tickets one at a time, and launch unrelated slot agents
   until the in-flight or active-agent limit is reached.
8. Start the next ranked `Planning` item with the default-owner capability only
   when the planning lane and active agent capacity are free after maximizing
   runnable implementation. An AFK Wayfinder research or task item uses this
   same step, but each non-research child receives a fresh provider context and
   research uses the required `research` subagent. Resume a marked Wayfinder
   reconciliation before new Planning work. Surface unassigned Wayfinder HITL
   frontier work and assigned HITL attention without dispatching either.
9. Monitor all remote slots together only when no local or controller action
   remains.
10. After the authoritative execution-clear predicate in
   [Backlog Triage Lane](triage-lane.md#dispatch) is satisfied, process the next
   unblocked Backlog `needs-triage` item through the triage tail lane.

At startup and after every refreshed query, present the changed human frontier
packet from [Epics And Human Frontier](human-frontier.md), together with the
ordered unassigned Wayfinder human frontier and assigned HITL attention. Never
wait for either while any step above remains runnable.

### Refresh Gate

Require one successful complete Project query and verified-base refresh before
new selection after a merge, parked or released slot, Planning or Backlog
handoff, epic closure, user prompt, controller resumption, or other event that
can change capacity, dependencies, or eligibility. Rebuild and rank every class
from that snapshot before a new claim or capacity-dependent dispatch, and apply
the same gate immediately before concluding that no runnable work remains.

Do not run the gate merely to handle a targeted review, CI, or base-repair event
for an occupied slot when no selection or finish decision follows. A successful
complete post-mutation query satisfies the gate; reuse that snapshot until a
later relevant mutation or event invalidates it. Never preempt a valid occupied
slot for newly higher-priority work.

Planning runs read-only beside implementation, enters the controller lane only
at assignment, comment publication, and Status transitions, and continues to
completion without preemption. Once handed off, the same assigned issue enters
the next available implementation slot. Apply the planning lane's reconciled
three-attempt recovery to planner loss, crash, or timeout; do not classify
those execution failures as semantic blockers.

Contract-preserving replan claims outrank all new Ready and Planning work but
never preempt an active agent. They retain their original claim order when
several slots requeue. Backlog items are never queue candidates; only an
interrupted current-runner cleanup is recoverable.

## Terminal Required-CI Parking

Classify only a required-CI failure isolated to one ticket as parkable. Access,
authentication, authorization, configuration, review, base-repair, merge,
ambiguous-mutation, shared-infrastructure, and correlated failures are not
parkable. Preserve or stop them through their existing failure-isolation rule.

Count one repair round only after the owning agent makes one bounded repair or
evidence-supported rerun and the reconciled required check reaches a terminal
failure at a verified PR head. Treat three rounds with the same sanitized
failure fingerprint and no new diagnostic direction as non-converging. Before
releasing the slot:

1. Publish one runner-authored issue comment containing
   `<!-- run-github-project:parked-implementation:v1 -->`, the issue and Project
   item IDs, PR URL, branch and head SHA, verified base SHA, committed
   configuration digest, and
   [live merge-policy fingerprint](project-config.md#live-merge-policy-fingerprint),
   required-check names and conclusions, sanitized failure fingerprint, and the
   check-run IDs, heads, and fingerprints for all three rounds. Include the
   preserved assignment and `In progress` Status. Never include local paths,
   secrets, or unsanitized logs.
2. Refetch the comment, assignment, Project Status, PR head, and checks. Require
   the marker author to be the authenticated runner and compute a digest from
   its immutable payload. Reconcile an ambiguous create before retrying. Keep
   the slot occupied when the record cannot be verified.
3. Preserve the verified record permalink and digest with the branch, worktree,
   PR, failed-check evidence, and repair history. Release every named resource,
   idle or discard the ticket agent, release the implementation slot, then pass
   the [Refresh Gate](#refresh-gate).

On startup and every refresh, honor the latest validated global configuration
and live merge-policy fingerprint before parked-claim recovery. Do not reread
either solely for an unchanged parked claim. Compare the lightweight live PR
head and required-check observation fingerprint with the latest verified
parking record. Keep an exact match parked without deep hydration. Deeply
hydrate it only when reconstructing the record, a marker changes, that
ticket-local observation fingerprint differs, or the user explicitly
authorizes a focused investigation. Treat a changed observation fingerprint as
a hydration trigger only, never as a resumption signal.

Restore a deeply hydrated parked claim only when it proves at least one
qualifying ticket-local recovery signal: an authority-lease-valid PR head from
a verified repair push; the previously failing required-check set now
terminal-success;
a materially different sanitized failure fingerprint with one concrete new
diagnostic direction; or explicit focused-investigation authority. A new check
run, attempt, timestamp, status transition, or conclusion that reproduces the
same sanitized failure is not a recovery signal and never resets the repair
budget. For example, deeply hydrate an external rerun that creates new check-run
IDs on the same head, but keep the claim parked when it reaches the same failure
without new diagnostics.

Before restoring a parked claim, publish and verify one runner-authored
`<!-- run-github-project:resume-parked-implementation:v1 -->` issue comment that
references the parking permalink and digest, records the qualifying recovery
signal and its evidence or a reference to the explicit investigation authority,
and captures the current PR head, checks, base, configuration, and merge-policy
evidence. An ambiguous resume record leaves the claim parked. Before publishing
that record, freshly revalidate the committed configuration digest and canonical
live merge-policy fingerprint. Any mismatch or unknown read stops the drain and
preserves the parked claim; it is never an autonomous resumption signal. After
verification, return the claim to the next free slot ahead of new claims,
reconstruct its owning agent if needed, and reset its repair-round count. A user
prompt, controller wake, global drift, changed observation fingerprint without
a qualifying recovery signal, or unchanged refetch alone is not a resumption
signal.

Treat a verified parking record as active only until a later verified resume
record references its permalink and digest. On restart, keep an active matching
record parked; restore a claim with a valid later resume record without
publishing another one. Ignore foreign, malformed, or mismatched markers.

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
6. After three non-converging required-CI repair rounds, apply
   [Terminal Required-CI Parking](#terminal-required-ci-parking).

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

Preserve a ticket-local blocker in its occupied slot while repair remains
within budget. Only a qualifying terminal required-CI failure follows
[Terminal Required-CI Parking](#terminal-required-ci-parking); other terminal
ticket blockers remain preserved in their slots. Stop the whole drain for
changed configuration, lost permissions, invalid base state, merge-policy
drift, correlated CI failure, or another integrity problem that affects every
claim.

Treat an unexplained scarce-resource collision as slot-local on its first
occurrence. Discover and add the narrow named lock before retrying. Pause new
claims when the same collision or infrastructure failure affects two slots or
the verified base.

After a verified Backlog handoff, cleanup failure is ticket-local. Release
scheduler capacity, report the exact unreconciled artifact, and never delete it
by guess. Keep the runner assigned as the durable cleanup lease until the
idempotent finish state proves that its PR, processes, resource grants,
worktree, and branches are gone; unassign last. A later run may finish only an
assigned Backlog cleanup with verified runner provenance. An unassigned Backlog
item without the configured `needs-triage` label remains human-owned; an
eligible labeled item belongs only to the triage tail lane.

Pass the refresh gate before evaluating the finish state. Finish successfully
only when the authoritative execution-clear predicate in
[Backlog Triage Lane](triage-lane.md#dispatch) is satisfied, the complete live
query has no non-deferred triage candidate after merge reconciliation, no
marked Wayfinder reconciliation claim remains, and no human action, Wayfinder
human-frontier item, or assigned Wayfinder HITL attention item remains.
Dependency-parked
Backlog items do not prevent success; report their live blockers. If only human
actions, Wayfinder human-frontier items, and/or assigned HITL attention remain,
return
`waiting-for-human` through [Epics And Human Frontier](human-frontier.md) and
the Wayfinder frontier. If no
runnable work remains but a parked implementation claim, blocked or timed-out
slot, or incomplete eligible triage item remains, stop with a partial-drain
report, preserve every affected worktree, branch, PR, assignment, and
`In progress` Status, and never report success.
