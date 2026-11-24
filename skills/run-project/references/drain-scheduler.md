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
   worktree under [Worktrees](ticket-lifecycle.md#worktrees), branch, PR,
   verified SHA, remote-wait deadline, and fix-round count.
   Start unrelated ticket agents concurrently by default when agent capacity
   permits.
3. Keep every implementation claim `In progress` until terminal reconciliation. Derive
   operational state from its slot, PR, checks, and reviews; require no extra
   Project Status values. A claim in [Remote Waiting](#remote-waiting) keeps
   its status, idle agent, worktree and PR but frees its slot. Cap waiting
   claims at the effective slot limit unless the user sets another cap; when
   the cap is full, the claim keeps its slot. Keep waiting claims outside the
   ranker's normalized array and `--max-claims` count, as for parked claims.
4. Reconstruct slots, waiting claims and parked claims after restart through
   [Remote Waiting](#remote-waiting),
   [Terminal Required-CI Parking](#terminal-required-ci-parking) and
   [ticket authority pauses](authority-and-pauses.md), using binding
   claims and marker records plus worktrees located by branch under
   [Worktrees](ticket-lifecycle.md#worktrees). Use local caches only as hints.
   Recover controller-owned batches separately under
   [Batched Post-Merge Updates](#batched-post-merge-updates).
5. Recover verified authority pauses outside capacity before ranking. Preserve
   invalid current-user claims as blocked slots, classify waiting claims
   (those beyond the waiting cap occupy slots), resume every other valid
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
   when the handoff reacquires a slot. Handle human removal of `ready-for-agent` under the
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
10. Keep role-labelled epics and human actions in the separate
   [Epics And Human Frontier](human-frontier.md). They consume neither a slot
   nor agent capacity. Require explicit human closure authority for a shape-only epic; surface
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

For each ticket pass, continue through implementation and local verification.
When full acceptance is verified at the integrated base with an empty final
diff, return `no-change` with the handoff evidence before push, PR creation/update
or shepherding. Yield to the controller for
[no-change reconciliation](ticket-lifecycle.md#reconcile-verified-no-change).
Preserve the claim and report any missing proof for a proposed no-change outcome.

For a nonempty candidate, continue through review coverage under the
[review evidence rule](review-contracts.md), a focused commit, and a
reconciled push plus PR creation or update.
Apply [PR review timing](../../shepherd/references/pr-review-timing.md) to request applicable external review before
yielding, while CI runs; record the trigger/readback, non-applicability, or exact capability or
repository gate that prevents it. Do not idle a locally qualified PR merely
waiting for CI before starting an otherwise permitted review.
Then yield durable evidence to the controller and idle that persistent context.
Resume the same agent for actionable feedback or base repair.

Apply [Route Agents By Task](ticket-lifecycle.md#route-agents-by-task) and record
the selected agent in the existing ownership record when selecting each
persistent ticket agent and helper.

### Conflict Admission Gate

Before concurrent admission, inspect native dependencies and the approved
plans' task graph, exact paths/seams, resource use and integration boundaries.
For planned or discovered overlap, the later-claimed slot is the younger one:

1. Delay the whole candidate for a native blocker/open descendant. For an
   approved-plan prerequisite, distinguish behavior needed to start a slice,
   shared-file mutation, and the final integrated baseline. Gate only the
   slices that need that behavior or boundary when the accepted plan explicitly
   permits independent preparation. An all-work prerequisite, inseparable seam,
   or uncertain independence still delays the whole candidate. Leave it
   unclaimed and consider the next candidate. Never infer conflicts or native
   blockers from title similarity alone, or silently weaken an accepted plan;
   use the authorized planning/change route if its scope or ordering must change.
2. A shared path alone is not a conflict. Inspect functions, symbols and regions
   plus behavioral dependencies: admit disjoint, independently testable edits
   in isolated worktrees when neither consumes the other's behavior. Record
   task IDs, region ownership, verified base, focused checks and the stop
   boundary in both owners' records. Unknown overlap still delays admission;
   disjoint line ranges alone do not establish semantic independence. For a
   real overlap, admit only explicitly approved independent preparation that
   stops before that boundary; its checks do not satisfy final qualification.
3. Retain named-resource grants for genuinely exclusive operations and
   repository-required file ownership. A declared file lock covers the canonical
   repository-relative path across worktrees; disjoint regions do not bypass it.
   Do not create a whole-file lock merely because isolated edits share a path.
4. Merge concurrent same-file tickets in claim order, older first. For proven
   disjoint edits, reassess the younger branch under
   [Merge And Base Drift](#merge-and-base-drift); shared paths alone require no
   rebase. For a shared integration boundary, checkpoint and pause the younger
   claim, revoke merge eligibility and apply the older-first base/review
   procedure below. Neither a free lock nor completed preparation clears an
   unresolved behavioral dependency.

Exclude an edit from the overlap check only when the controller has verified
that it will be deferred under
[Batched Post-Merge Updates](#batched-post-merge-updates). Keep other edits in
the same file and any declared file lock in the gate.

Do not claim a ticket just to wait when it has no safe runnable slice. Keep
native dependencies at whole-ticket admission and qualification gates at their
required operation boundaries; partial work never bypasses either.

When running agents discover a concrete overlap that was absent from their
plans, including needing another owner's region, stop and report to the
controller before further shared edits. Let the younger agent finish only the
current atomic operation, verify work within its safe owned scope, and
reach a clean focused commit checkpoint without crossing the uncertain seam.
A reconciled push of that commit is also valid. If the agent cannot reach a
clean commit safely, preserve and block
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
to their owning ticket or planning agent. Through the ticket handoff,
`implement-with-subagents` owns assignment, integration, task acceptance and
same-owner repairs. Workers write only
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
actions that fit the slot and active-agent limits. Exhaust each existing-claim
class before dispatching the next. For Jira, select new work at steps 7–8 from
the combined ranker order across planning and implementation. Pick the first
runnable candidate with capacity in its lane. For GitHub keep the separate
new-work classes in steps 7 and 8.

1. Apply the label-stop gate before automatic work and recovery. Exclude unlabelled Todo and binding-parked work. Reconcile eligible
   resumable authority pauses and park newly blocked operations
   through their controller procedure before selecting another ticket.
2. Merge the oldest merge-ready claim, unless an explicit dependency requires a
   different order. Admit or merge only one at a time.
3. Reconcile explicitly human-authorized epic closures, then
   refresh the complete bound tracker scope before taking another action.
4. Resume owning ticket agents for actionable review, CI, or base-repair events
   in oldest-event order.
5. Resume paused local implementation slots in claim order.
6. Resume a verified yielded planner after higher-priority delivery work, or
   finish a current replan/plan/handoff. Retain its owner, draft, used planning
   time and attempt count. Choose preserved replan claims before other Todo
   claims; never start a second planner while one retains the planning lane.
7. Apply the [Conflict Admission Gate](#conflict-admission-gate), claim ranked
   Todo tickets with verified usable active plans one at a time, and launch
   unrelated slot agents
   until the in-flight or active-agent limit, less any watcher relay
   reservation ([GitHub watcher step 4](github-project-watcher.md)), is reached.
8. Start the next selected `Todo` planning item with the default-owner
   capability when the planning lane and active agent capacity are free.
   For GitHub, maximize runnable implementation first. An AFK Wayfinder research or task item uses this
   same step, but each non-research child receives a fresh provider context and
   research uses the required `research` subagent. Resume a marked Wayfinder
   reconciliation before new Todo work. Surface unassigned Wayfinder HITL
   frontier work and assigned HITL attention without dispatching either.
9. Check [Batched Post-Merge Updates](#batched-post-merge-updates) for work
   before waiting or starting tail triage. Use the selected tracker's
   [remote wait procedure](#project-watcher) for
   remote claims and human-gated items. Continue handling agent notifications
   while local or controller actions remain.
10. After the authoritative execution-clear predicate in
   [Todo Triage Lane](triage-lane.md#dispatch) is satisfied, process the next
   unblocked Todo `needs-triage` item through the triage tail lane.

At startup and after every refreshed query, present the changed human frontier
packet from [Epics And Human Frontier](human-frontier.md), together with the
ordered unassigned Wayfinder human frontier and assigned HITL attention. Never
wait for either while any step above remains runnable.

### Refresh Gate

Use the execution controller's [bound-scope refresh](execution-controller.md#remote-state-and-queue).
Require one successful complete read of the selected tracker scope and a
verified-base refresh before new selection after a merge, parked or released slot, Todo
handoff, epic closure, user prompt, controller resumption after interruption,
or other event that
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
reconciliation. Each merge, recovery, selection or finish decision needs a
current complete snapshot, not a fresh network round trip when the existing snapshot remains uninvalidated.
Changed record fingerprints identify what to rehydrate; they never authorize
reuse after an incomplete logical read. Discard partial/ambiguous results and
reestablish the complete logical read before ranking, dispatch or finish.
Immediately before each consequential write, still refetch its operation-specific
authority and identities; snapshot reuse does not waive that check.

Use [Todo Lane](todo-lane.md) for handoffs and bounded planner recovery.
When several slots requeue, retain their original claim order ahead of new
Todo implementation and planning work. Only the verified cooperative planner
checkpoint may
release an active planner for delivery; occupied ticket owners are not preempted.

### Project Watcher

In parent scope, a Project query reads the complete parent, descendant and
dependency graph, and Status means the logical claim state.

For a GitHub `drain`, use the [GitHub watcher procedure](github-project-watcher.md)
to decide whether a watcher is needed before reserving relay capacity or taking
the pre-read baseline. Follow it on watcher wakes or deadlines.
`next` never starts a watcher. For Jira or GitLab, follow the binding's
unavailable wait lane ([Jira](../../deliver-issue/references/jira-binding.md#unavailable-lanes-and-finish-gate),
[GitLab](../../deliver-issue/references/gitlab-binding.md#tracker-availability-and-finish-gate))
and the [finish gate](#failure-isolation-and-finish-gate) when eligible work is exhausted.

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

1. Publish the [CI parking payload](github-binding.md#publish-a-ci-parking-record)
   through the selected tracker's marker operations, with the preserved item and
   scope identities and the three-round check evidence.
2. Refetch the marker, exact claim status and assignment through the selected
   tracker. Refetch the PR head and checks through the selected code host.
   Require the marker author to be the authenticated runner and compute its
   [payload digest](../../to-plan/references/github-mode.md#payload-digest). Reconcile an ambiguous create before retrying. Keep
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
[resume-parking marker](github-binding.md#resume-parking-format) through the
selected tracker's marker operations. Include the parking permalink and digest,
the qualifying recovery
signal and its evidence or a reference to the explicit investigation authority,
and the current PR head, checks, base, configuration, and merge-policy evidence. An ambiguous resume record leaves the claim parked. Before publishing
that record, freshly revalidate the effective binding fingerprint and canonical
live merge-policy fingerprint. A committed display-name-only change may use
[verified lease renewal](github-binding.md#renew-presentation-only-configuration);
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

After a reconciled push and the PR review timing step above:

1. Verify the claim holds no named resource grant, reconciling one before
   entering remote wait, then release its slot under the waiting cap in the
   [Slot Model](#slot-model). After restart, treat an `In progress` claim as
   waiting when its clean worktree matches its runner-pushed PR head, which
   passed local review gates before push; no marker is needed. Reconcile the
   external-review request independently of CI and resume the owner if that
   permitted request was omitted. A pending actionable
   event does not make it active: queue it for the next free slot ahead of
   new claims.
2. Idle its persistent ticket agent so remote waiting consumes no active-agent
   capacity. Monitor PRs under the selected tracker's
   [remote wait procedure](#project-watcher), without no-op comments.
3. Give that PR a 24-hour deadline from its latest push unless the user or
   repository specifies another duration.
4. Reset only that PR's deadline after a fix push.
5. Return an actionable event to its ticket agent at the next checkpoint,
   restoring a released claim to the next free slot ahead of new claims.
6. After three non-converging required-CI repair rounds, apply
   [Terminal Required-CI Parking](#terminal-required-ci-parking).

Treat the first unexplained CI failure as ticket-local. If the same failure
appears on two claims or on the verified base, pause new claims and treat it as
a global failure.

## Merge And Base Drift

Serialize every merge and prefer the configured merge queue. Before merging,
refresh the exact head and revalidate the claim against the latest base,
authority lease, all required checks and reviews, finding dispositions and
their final-head applicability, terminal-green CI, and mergeability.

After a merge:

1. Reconcile terminal issue and bound-scope state through the selected tracker.
   Verify the Project item's terminal state when the scope is a GitHub Project.
2. Refresh mergeability for every other PR.
3. Shared files alone require neither a branch update nor a CI rerun. Use
   `git merge-tree` against the verified new base to check conflicts without
   mutating the owner's worktree; an unavailable/error result is unknown, not
   a clean merge. Update and renew affected checks only for a confirmed
   conflict, repository policy requiring an up-to-date branch, or evidence that
   the merged change invalidates an assumption the PR's checks relied on.
   Never rebase every branch automatically; apply final-head evidence rules
   when an update is required.
4. Clean up the merged claim's worktree and branch under
   [Worktrees](ticket-lifecycle.md#worktrees).

### Batched Post-Merge Updates

In `drain`, defer only repository-approved updates that can land after an
independently deliverable ticket. Use the ordinary PR flow for `next`, direct
delivery and human PRs.

1. Read opt-in rules in the trusted repository instructions at the verified
   base. Each rule names repository-relative paths or globs, the allowed update,
   and how to apply and verify it. Match each proposed path individually. Defer
   the update only when the rules agree and evidence shows the ticket still
   builds, passes its required checks and ships correctly with the file
   unchanged. Keep build inputs, same-PR requirements, ambiguous matches and
   changes that are themselves the ticket deliverable in the ticket PR. For
   example, a repository may opt in Unreleased entries in `CHANGELOG.md` and
   regenerated indexes under `docs/indexes/*.md` when neither affects the main
   build or delivery.
2. Verify planned deferrals before conflict admission and record them in the
   ticket packet. Have the owner leave the deferred edit out of the ticket
   diff and put the target path and intended update in a `Deferred updates`
   section of the PR body. Record the content or name the repository's
   regeneration procedure and inputs for the changes delivered by that PR.
   A decision to contribute nothing needs a reason. At PR handoff, confirm
   the section is complete, the planned edit is
   absent from the diff and the rule still applies. Persist the verified content,
   rule, scope, ticket, source PR and head in the existing delivery checkpoint
   before remote wait, pause or handback. Revalidate affected evidence on head,
   body or policy changes before merging. Resume the owner when evidence is
   incomplete or an edit belongs in the ticket PR.
3. Make an update eligible only on authoritative source merge readback, including
   external-merge reconciliation. Bind it to the verified merged head, target
   branch and exact recorded intent. On restart, recover outstanding updates
   from the durable delivery records and reconcile their source PRs, including
   terminal tickets. Use an identity derived from the source PR, merged head,
   path and recorded intent to avoid duplicate application. Preserve and report
   updates whose evidence cannot be verified. Keep unmerged updates out of the
   batch and list them in the report.
4. Pass the [Refresh Gate](#refresh-gate) and check after any event that can
   leave no occupied, remote-waiting or runnable ticket, including a pause or
   release, and again at the finish gate. If eligible updates remain, resume
   the existing batch for the repository and target branch or prepare one.
5. Keep one pending batch per code-host repository and target branch, across
   drain invocations. Derive a stable, reserved batch branch from that identity.
   Before creating or retrying, read the checkpoint, reserved branch and exact
   host PRs. Recover one verified batch, including a pushed branch without a
   confirmed PR, by verifying owner, membership, head and target. Revalidate
   current authority and exclude concurrent writers before resuming writes.
   Preserve and report foreign, competing or ambiguous records. Retain a
   closed-unmerged batch and its entries when retry needs a human decision.
6. Before editing, record batch ID, owner, binding, target, base, branch and
   member update identities in the controller's durable checkpoint. Use the
   shared [checkout lifecycle](../../implement-with-subagents/references/checkout-lifecycle.md) to create and record this
   controller-owned worktree. Recheck each rule against the latest verified base
   and apply the recorded intent there. If an update is already present, record
   the evidence and skip the edit. Preserve and report updates whose rules drift
   or whose application or verification is uncertain. Open a PR only for a
   nonempty verified diff.
7. Keep edits and repairs with the controller. Freeze membership when independent
   review starts. Queue later merges for a subsequent batch. Record batch
   identity and membership in the pushed commit and PR body. Create the remote
   branch only if absent and condition later pushes on the verified prior head.
   Reconcile an uncertain push or PR creation through the
   [code-host binding](../../deliver-issue/references/provider-bindings.md). Use non-closing links to the
   verified source PRs and check the batch has no effective closing references.
   Require independent review, applicable external reviews, required checks
   and finding dispositions for the exact final head. Include a pending batch
   in the [watch set](#project-watcher) even when it is the only PR awaiting a
   signal. Use the PR deadline in [Remote Waiting](#remote-waiting) and route
   review, CI and timeout events to the controller without a ticket slot or
   ticket parking. If monitoring is unavailable or the deadline expires,
   preserve and report the pending PR and the exact reconciliation needed.
   Once a batch timeout is handled, remove its expired deadline from watcher
   inputs. Keep the PR in the watch set while other monitored work remains.
8. Serialize merge with other controller merges. Verify the current binding,
   grant, target, head, checks, reviews, closing references and mergeability
   before merging. Without a merge grant, hand back the checked, reviewed batch
   as ready and retain it for recovery. After verified merge readback, record
   its delivered member identities, retire the checkout under the shared
   lifecycle and release the reserved branch only after verifying it still
   points at the delivered head. Reconcile cleanup before reusing the branch.
   Refresh other PRs and the scope. Batch delivery never changes source ticket
   status or closure. Account for the checkout and remaining updates at handback.

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

If `ready-for-agent` is removed, apply [Stop on label removal](authority-and-pauses.md#stop-on-label-removal) before any recovery or write. Stop writers, release verified capacity, and retain assignment, worktree, dirty draft, branch, PR and artifacts without cleanup. Later runs stay stopped until a human restores the label; the controller never restores it. Keep these items and unlabelled Todo in the native dependency graph and report stopped work in the human frontier.

Before a drain returns success, `partial-drain` or `waiting-for-human`, or
starts the human-gated watcher wait, apply
[Batched Post-Merge Updates](#batched-post-merge-updates) and re-pass the
refresh gate after batch mutations. Success requires all eligible updates
verified on the target or in a ready batch handed back without merge authority.
Report pending batch PRs, blocked or not-yet-batched merged updates, and the
recorded updates of unmerged tickets. For an integrity stop, preserve existing
batches and report outstanding updates without further batch mutations.

Whenever a drain finishes, waits for humans or stops, apply
[Worktrees](ticket-lifecycle.md#worktrees) step 6.

Pass the refresh gate before evaluating the finish state. Finish successfully
only when the authoritative execution-clear predicate in
[Todo Triage Lane](triage-lane.md#dispatch) is satisfied, the complete live
query has no non-deferred triage candidate after merge reconciliation, no
marked Wayfinder reconciliation claim remains, and no label-stopped work, authority/decision pause,
human action, Wayfinder
human-frontier item, or assigned Wayfinder HITL attention item remains.
Unlabelled Todo without retained work does not prevent completion of the authorized queue. Stopped retained work remains a human frontier; report its artifacts and any dependency edges blocking eligible work.
Dependency-parked Todo items retain their normal blocker reporting. If the
selected tracker cannot monitor waits, finish runnable work and refresh once.
Return `waiting-for-human` for a human-only frontier or `partial-drain` for
pending PRs or other blockers. Preserve all affected state and name the fresh
tracker and host reads needed on resume. Use the following watcher deadline
and failure rules only where the binding supplies a watcher.

If only human
actions, verified authority/decision pauses, Wayfinder human-frontier items,
and/or assigned HITL attention or label-stopped work remain,
wait under the [Project Watcher](#project-watcher) instead of returning. Return
`waiting-for-human` through [Epics And Human Frontier](human-frontier.md) and
the Wayfinder frontier only when the drain's no-progress deadline has passed or
monitoring becomes unavailable after three consecutive failures. In the latter
case, the `waiting-for-human` return, which names each preserved PR in remote
wait, applies only when nothing but human-gated work and PRs in remote wait
remains; any other blocker still produces the partial-drain report below. If no
runnable work remains but a parked implementation claim, blocked or timed-out
slot, blocked or timed-out batch, unknown/unavailable execution or qualification
prerequisite, or incomplete eligible triage item remains, stop with a partial-drain
report, preserve every affected worktree, branch, PR, assignment, and
`In progress` Status, and never report success.
