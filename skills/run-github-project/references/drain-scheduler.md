# Drain Scheduler

Use this scheduler only for `drain`. Keep `next` single-ticket.

## Slot Model

1. Default to two implementation slots; accept any positive user limit without
   a skill-defined maximum. Compute the effective slot limit from the strictest
   applicable repository and invocation limits. Separately compute active-agent
   capacity from the strictest runtime, repository and invocation concurrency
   limits. Running ticket agents, planners and descendants consume active-agent
   capacity; idle contexts do not. Parked claims consume neither. Pass the
   effective slot limit to the ranker, not the currently free agent count.
   Never turn a ranked candidate or idle slot into an agent-capacity grant.
2. Give each occupied slot one ticket agent, issue, authority lease, warm
   worktree, branch, PR, verified SHA, remote-wait deadline, and fix-round count.
   Start unrelated ticket agents concurrently by default when agent capacity
   permits.
3. Keep every implementation claim `In progress` until merge reconciliation. Derive
   operational state from its slot, PR, checks, and reviews; require no extra
   Project Status values.
4. Reconstruct slots and parked claims after restart through
   [Terminal Required-CI Parking](#terminal-required-ci-parking) and
   [ticket authority pauses](authority-and-pauses.md), using GitHub
   claims and marker records plus verified skill-owned worktrees. Use local
   caches only as hints.
5. Recover verified authority pauses outside capacity before ranking. Preserve
   invalid current-user claims as blocked slots, resume every other valid
   claim, then fill free slots. Stop for reconciliation when all active and
   blocked-slot claims together exceed the invocation's slot limit.
6. Keep one separate planning lane. It preserves assignment and planning
   handoff claims but never consumes one of the configured implementation slots.
   Follow [Todo Lane](todo-lane.md) for its worktree, agent, authority,
   handoff, and blocker rules. Do not reserve agent capacity for Todo;
   start it only from currently spare capacity. For actionable delivery repair,
   use the [cooperative planner checkpoint](todo-lane.md#yield-a-planner-for-delivery)
   rather than waiting for speculative planning to finish.
7. When an implementation slot requeues for contract-preserving planning,
   release the slot but park its assignment, branch, worktree, PR, dirty work
   and idle ticket context on the planning claim. Restore that same ownership
   when the handoff reacquires a slot. Handle a human move to Backlog under the
   [failure-isolation procedure](#failure-isolation-and-finish-gate).
8. Apply [Terminal Required-CI Parking](#terminal-required-ci-parking) only to a
   qualifying failure after its repair budget, and the
   [ticket-pause procedure](authority-and-pauses.md#pause-one-ticket) for missing
   authority or a decision. Parked implementation claims
   consume neither an implementation slot nor agent capacity.
9. Keep Todo triage as a tail lane. Follow
   the authoritative execution-clear predicate in
   [Todo Triage Lane](triage-lane.md#dispatch). It consumes no implementation
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
addressed threads concurrently. Invalidate review evidence affected by a SHA
change and cover the new head under the [review evidence rule](review-contracts.md)
before another push.

Keep one controller lane for just-in-time claims and assignment, Project Status
mutations, slot setup and cleanup, merges or merge-queue admission, issue
closure, and Done reconciliation. Serialize those actions and reconcile every
ambiguous remote mutation before the next controller mutation. Ticket agents
never mutate another slot or the controller-owned Project state.

For each ticket pass, continue through implementation, verification, review
coverage under the [review evidence rule](review-contracts.md), a focused
commit, and a reconciled push plus PR creation or update.
Then yield durable evidence to the controller and idle that persistent context.
Resume the same agent for actionable feedback or base repair.

Apply [Route Agents By Task](ticket-lifecycle.md#route-agents-by-task) and record
the selected agent in the existing ownership record when selecting each
persistent ticket agent and helper.

### Conflict Admission Gate

Before concurrent admission, inspect native dependencies and the approved
plans' task graph, exact paths/seams, resource use and integration boundaries.
For planned or discovered overlap, the later-claimed slot is the younger one:

1. Delay the whole candidate for a native blocker/open descendant, an explicit
   approved-plan prerequisite on occupied work, an inseparable shared seam, or
   uncertain independence. Leave it unclaimed and consider the next candidate.
   Never infer conflicts or native blockers from title similarity alone.
2. For a concrete shared path/resource, admit only when approved plans prove
   independently testable slices that neither touch nor depend on that boundary.
   Record those task IDs, permitted paths/resources and the stop boundary in
   both owners' records before dispatch. Without that proof, delay the ticket.
3. Let those safe slices proceed, but serialize the actual shared edit/resource
   operation under the named-resource grant below. A file lock covers the whole
   repository identity and canonical repository-relative path across worktrees,
   not guessed disjoint
   line ranges. Repository-required mutation ownership remains stricter.
4. At the shared integration boundary, checkpoint and pause the younger claim,
   revoke merge eligibility and apply the older-first base/review procedure
   below. Neither a free edit lock nor completed disjoint slice permits a
   younger ticket to merge ahead of its unresolved integration boundary.

Do not claim a ticket just to wait when it has no safe runnable slice. Keep
native dependencies at whole-ticket admission and qualification gates at their
required operation boundaries; partial work never bypasses either.

When running agents discover a concrete overlap that was absent from their
plans, let the younger agent finish only the
current atomic operation, complete and verify its current vertical slice, and
reach a clean focused commit checkpoint. A reconciled push of that commit is
also valid. If the agent cannot reach a clean commit safely, preserve and block
the younger slot; do not begin automated base repair from a dirty worktree.

After that clean checkpoint, pause the younger slot without releasing its
claim, and revoke its merge eligibility. If the older integration is waiting on
missing authority or a human decision, use the existing
[verified preservation pause](authority-and-pauses.md#pause-one-ticket)
for the younger ticket too: identify the older ticket and exact blocked
integration, preserve its claim, owner, branch, worktree and checkpoint, and
record verified completion of that older integration as the resume condition.
Only after pause publication is reconciled, writers are quiescent and grants
are released may its implementation slot and agent capacity be released for
unrelated work. Unknown publication or ownership keeps that capacity blocked.
Do not repeatedly reacquire a slot while the older integration remains paused.
On recovery, satisfy that exact condition and revalidate the younger lease
through the same pause/resume procedure; restore its same owner and artifacts
in the next free slot before base repair. Authority for the older ticket alone
does not satisfy the younger ticket's completion condition. While the older
integration can proceed within this run, retain the younger occupied slot.
Merge the older slot first, refresh
the verified base, then resume the younger slot's owning ticket agent. Under
its existing exclusive slot ownership, only that agent may update its branch
and worktree to the new base using repository policy; the controller never
edits the agent-owned branch.

The owning agent must revalidate the authority lease and approved plan, repeat
affected verification and review against the updated SHA, retaining demonstrably
unaffected evidence. Repeat full checks only when invalidated, impact cannot be
bounded or an explicit repository/provider requirement demands them. Then
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
Descendant agents at any depth use only currently spare agent capacity.
Discovery and review helpers are read-only at immutable SHAs and route findings
to their owning ticket or planning agent. `deliver-spec` owns implementation
assignment, integration, acceptance, and same-owner repair; workers write only
their task worktrees and branches and return commits to their ticket delivery
lead. Count every active descendant against actual spare capacity. Task
implementation and review descendants never mutate Project, issue, or PR
state. An implementation helper yields before its occupied slot agent must
resume. Under scarce capacity, request a verified cooperative planner yield
for actionable delivery repair. Do not interrupt an atomic operation, steal
ownership, or dispatch into capacity that has not actually been released.
Reconcile publication in flight first. With spare capacity, resume the delivery
owner immediately without disturbing the planner.

## Scheduling

Before starting new work, recover and select claim classes in the order defined
by [Todo Lane](todo-lane.md#scheduling).

At every controller event or worker yield, perform all independent runnable
actions that fit the slot and active-agent limits. Exhaust each class before
dispatching the next:

1. Exclude Backlog from automatic work and recovery. Reconcile eligible
   resumable authority pauses and park newly blocked operations
   through their controller procedure before selecting another ticket.
2. Merge the oldest merge-ready slot, unless an explicit dependency requires a
   different order. Admit or merge only one at a time.
3. Reconcile the highest-ranked ready epic with issue-close authority, then
   refresh the complete Project graph before taking another action.
4. Resume owning ticket agents for actionable review, CI, or base-repair events
   in oldest-event order.
5. Resume paused local implementation slots in claim order.
6. Resume a verified yielded planner after higher-priority delivery work, or
   finish a current replan/plan/handoff. Retain its owner, draft, used planning
   time and attempt count. Choose preserved replan claims before other Todo
   claims; never start a second planner while one retains the planning lane.
7. Apply the [Conflict Admission Gate](#conflict-admission-gate), claim ranked
   `Ready to implement` tickets one at a time, and launch unrelated slot agents
   until the in-flight or active-agent limit is reached.
8. Start the next ranked `Todo` item with the default-owner capability only
   when the planning lane and active agent capacity are free after maximizing
   runnable implementation. An AFK Wayfinder research or task item uses this
   same step, but each non-research child receives a fresh provider context and
   research uses the required `research` subagent. Resume a marked Wayfinder
   reconciliation before new Todo work. Surface unassigned Wayfinder HITL
   frontier work and assigned HITL attention without dispatching either.
9. Keep the [Project Watcher](#project-watcher) running for every remote slot
   and human-gated item, even while other slots have agents working. When no
   local or controller action remains, wait on it and on agent notifications.
10. After the authoritative execution-clear predicate in
   [Todo Triage Lane](triage-lane.md#dispatch) is satisfied, process the next
   unblocked Todo `needs-triage` item through the triage tail lane.

At startup and after every refreshed query, present the changed human frontier
packet from [Epics And Human Frontier](human-frontier.md), together with the
ordered unassigned Wayfinder human frontier and assigned HITL attention. Never
wait for either while any step above remains runnable.

### Refresh Gate

Require one successful complete Project query and verified-base refresh before
new selection after a merge, parked or released slot, Todo or Ready
handoff, epic closure, user prompt, controller resumption, or other event that
can change capacity, dependencies, or eligibility. Rebuild and rank every class
from that snapshot before a new claim or capacity-dependent dispatch, and apply
the same gate immediately before concluding that no runnable work remains.

Do not run the gate merely to handle a targeted review, CI, or base-repair event
for an occupied slot when no selection or finish decision follows. Refetch that
ticket's affected PR/head/check/review and authority records; rehydrate only
changed or unverified records. Repeated unchanged CI observations do not justify
another complete board hydration. A successful complete post-mutation query
satisfies the gate; reuse it until invalidated. Never preempt a valid occupied
slot for newly higher-priority work.

Record the complete snapshot's identity, verified base, observation time and
completeness in the existing controller checkpoint. For each invalidation and
full refresh record its triggering event and decision: selection, merge,
capacity/eligibility change, recovery, incomplete/ambiguous read or final
reconciliation. A scheduling boundary needs a current complete snapshot, not a
fresh network round trip when the existing snapshot remains uninvalidated.
Changed record fingerprints identify what to rehydrate; they never authorize
reuse after an incomplete logical read. Discard partial/ambiguous results and
reestablish the complete logical read before ranking, dispatch or finish.
Immediately before each consequential write, still refetch its operation-specific
authority and identities; snapshot reuse does not waive that check.

Use [Todo Lane](todo-lane.md) for handoffs and bounded planner recovery.
When several slots requeue, retain their original claim order ahead of new
Ready and Todo work. Only the verified cooperative planner checkpoint may
release an active planner for delivery; occupied ticket owners are not preempted.

### Project Watcher

In `drain` only, wake the controller from a wait with the read-only
`python3 <skill-dir>/scripts/watch_project.py`, which runs only `gh api graphql`
queries; `next` never starts one. Its report is a hint to refresh, never
authority: it never satisfies the [Refresh Gate](#refresh-gate), authorizes a
claim, merge, or close, replaces a complete Project query, or serves as a
resumption signal for a [parked claim](#terminal-required-ci-parking). Waiting
grants nothing; run grants stay invocation-scoped and lapse when the run returns.

1. Run exactly one watcher whenever any slot is in remote wait or a human action
   or authority/decision pause exists. With neither, start none, stop a running
   one, and wait for agent notifications. Never poll, sleep, or use
   `ScheduleWakeup`, `CronCreate`, `/loop`, or the single-PR host monitor.
2. Immediately before each complete Project query, and before the targeted
   refetch that answers a PR-only report, write a baseline:
   `snapshot --project-id <Node ID> --repository <owner/name> --status-field <Status field name> [--pr <N>]... [--issue <N>]... > <baseline file>`.
   Pass `--pr` for every in-flight PR in remote wait and every preserved PR of a
   paused, parked, or authority-paused ticket, and `--issue` for every parked
   claim, paused ticket, and human-frontier issue. A non-zero `snapshot` is an
   `error` under step 6: discard its output, launch no `wait`, and retake the
   snapshot before repeating the read it precedes.
3. After a read preceded by a successful `snapshot` completes, stop any running
   watcher through the host's cancellation mechanism, never by process-name or
   command-line match. Then launch `wait` with the same arguments plus
   `--baseline <file>` and `--deadline <ISO-8601>` and, when the binding sets
   one, `--interval <seconds>` from
   [Monitoring](project-config.md#monitoring-optional); the default is 120.
   A PR or issue the read added to or dropped from those sets appears as `added`
   or `removed` in the first report; handle it like any other report.
4. On a host that wakes the controller when a background command exits (Claude
   Code `run_in_background`), run the command directly and wait for its
   completion notification. On any other host (Codex), launch the cheapest
   available subagent, briefed under [subagent selection](subagent-selection.md)
   to run that one `wait` command once and return its stdout verbatim, with no
   other action or further delegation, and wait with the host's agent-wait call
   (`wait_agent`).
5. Set the deadline to the last productive wake plus 24 hours, or the drain start
   when there is none; when a PR is in remote wait, use the latest such PR
   deadline if it is later. A productive wake is any watcher report or agent
   notification that leads to a claim, merge, or dispatched work, and it resets
   the deadline. A wake whose refresh finds nothing eligible does not. Record the
   last productive wake in the existing controller checkpoint.
6. Read the one-line report; treat a non-zero exit or any other output as `error`.
   - `changed` naming only occupied-slot PRs: refetch only those tickets' PR,
     head, check, review, and authority records; run no Refresh Gate.
   - Any other `changed`, including a preserved PR of a paused or parked ticket:
     pass the Refresh Gate before any selection or claim.
   - `error`: a wake, never "no change". Pass the Refresh Gate and count one
     consecutive failure; `changed` and `deadline` reset the count. After three,
     stop watching. Once no local or controller action remains, apply the
     [finish gate](#failure-isolation-and-finish-gate)'s monitoring-unavailable
     rule.
   - `deadline`: pass the Refresh Gate and take any newly runnable action;
     otherwise the [finish gate](#failure-isolation-and-finish-gate) now
     returns `waiting-for-human` if only human-gated work remains.

## Phase Timing And Stalls

1. Persist observed planning, implementation, repair, review and CI intervals
   in the existing run/ticket checkpoint: stable interval ID, ticket/owner,
   phase, start, end or still-open state, source/plan/head and progress evidence.
   Record capacity/resource waits separately with their cause and awaited owner
   or grant, and each [Project Watcher](#project-watcher) wait as a wait with
   cause `watcher`. Checkpoint before yielding, handing off or compacting context.
2. Resume the same interval IDs; never append duplicate starts after compaction.
   Reconcile uncertain endpoints from evidence and report unknown time when
   unavailable. Keep planning active-time budget separate from yielded/wait time.
3. Report phase elapsed times and waits with their overlap, plus total run wall
   time from observed start/end. Never sum overlapping phases or tickets into
   wall time. For example, planning 00:00–00:10, implementation 00:05–00:15 and
   a repair capacity wait 00:06–00:10 are 10, 10 and 4 minutes, within a
   15-minute observed wall span. Do not invent a saving or attribute all waiting
   to planning without the recorded cause.
4. When a lifecycle cycle repeats without a delivered increment, compare its
   source/plan/base/head, phase/wait and invalidation evidence with the previous
   cycle. Identify the unchanged failure or renewed work, its cause and one
   bounded next action through the existing repair/replan rules. Keep the same
   owner and budgets. If no evidence-supported next action exists, preserve an
   exact blocker; do not repeat a full plan/review loop, blanket retry, weaken
   qualification or reset a budget merely to keep the run moving.

## Terminal Required-CI Parking

This CI procedure classifies only a required-CI failure isolated to one ticket
as parkable. Missing user authority uses
[ticket authority pauses](authority-and-pauses.md), not CI repair rounds. Access,
authentication, configuration, review, base-repair, merge,
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
live merge-policy fingerprint. A committed display-name-only change may use
[verified lease renewal](project-config.md#renew-presentation-only-configuration);
every other mismatch or unknown read stops the drain and preserves the parked
claim. Renewal alone is never a qualifying ticket-local resumption signal. After
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
   capacity. Monitor all PRs together through the
   [Project Watcher](#project-watcher), without no-op comments.
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
within budget. A missing grant or material decision follows
[ticket authority pauses](authority-and-pauses.md) and releases verified paused
work from active capacity. A qualifying terminal required-CI failure follows
[Terminal Required-CI Parking](#terminal-required-ci-parking); other terminal
ticket blockers remain preserved in their slots. Stop the whole drain for
semantic or unverified configuration drift, lost permissions, invalid base
state, merge-policy drift, correlated CI failure, or another integrity problem
that affects every claim.

Treat an unexplained scarce-resource collision as slot-local on its first
occurrence. Discover and add the narrow named lock before retrying. Pause new
claims when the same collision or infrastructure failure affects two slots or
the verified base.

If an item is now in Backlog, stop its writers and release capacity. Preserve
and report any assignment, PR, process checkpoint, worktree, or branch without
mutating that ticket or cleaning its artifacts. Backlog role labels and prior
ownership never authorize work; only a human promotion makes it eligible again.
Keep Backlog issues in the native dependency graph, so they can still block
eligible dependants, but exclude them from automatic frontier actions.

Pass the refresh gate before evaluating the finish state. Finish successfully
only when the authoritative execution-clear predicate in
[Todo Triage Lane](triage-lane.md#dispatch) is satisfied, the complete live
query has no non-deferred triage candidate after merge reconciliation, no
marked Wayfinder reconciliation claim remains, and no authority/decision pause,
human action, Wayfinder
human-frontier item, or assigned Wayfinder HITL attention item remains.
Excluded Backlog items do not prevent completion of the authorized queue;
report any of them that blocks eligible work or retains interrupted artifacts.
Dependency-parked Todo items retain their normal blocker reporting. If only human
actions, verified authority/decision pauses, Wayfinder human-frontier items,
and/or assigned HITL attention remain,
wait under the [Project Watcher](#project-watcher) instead of returning. Return
`waiting-for-human` through [Epics And Human Frontier](human-frontier.md) and
the Wayfinder frontier only when the watcher reports its `deadline` or
monitoring becomes unavailable after three consecutive failures. In the latter
case, the `waiting-for-human` return, which names each preserved PR in remote
wait, applies only when nothing but human-gated work and PRs in remote wait
remains; any other blocker still produces the partial-drain report below. If no
runnable work remains but a parked implementation claim, blocked or timed-out
slot, unknown/unavailable execution or qualification prerequisite, or incomplete
eligible triage item remains, stop with a partial-drain
report, preserve every affected worktree, branch, PR, assignment, and
`In progress` Status, and never report success.
