# Todo Lane

Use this lifecycle for Project items in `Todo` and for the verified handoff
into implementation.

Configured Wayfinder children take the separate integration branch in
[Wayfinder Todo Lane](wayfinder-lane.md). They share this lane's scheduling
class and safe-checkpoint rules, but never use the implementation-plan marker,
Ready handoff, or implementation lifecycle below.

## Eligibility And Plan State

Require both:

1. the exact `ready-for-agent` label; and
2. current `Todo` Status.

Verify the active marked plan under the [normalized-ticket contract](normalized-ticket.md):
runner authorship, revision chain, semantic payload digest, and configured base.
Hydrate minimized predecessors; accept only the unique unminimized leaf. Plan
missing or stale plans; preserve invalid chains and foreign markers as semantic
blockers. Never fall back to an unmarked Agent Brief.
Record the plan identities and metadata in the authority lease and screen base
SHA drift before implementation. Column membership supplies authority; a verified
replan report determines when a replacement revision is needed.

## Plan a Todo item

1. Enter the controller lane and refetch current `Todo` membership. If the
   item is in Backlog, stop its automatic work and preserve its artifacts;
   only a human can promote it. Assign the issue exclusively to the
   authenticated user, refetch and verify the assignment, and release the lane. Reconcile an
   ambiguous Status or assignment mutation before retrying. Preserve the
   assignment through planning and implementation.
2. Use one dedicated, reusable, clean planning worktree at a stable
   controller-recorded path outside the checkout, detached at the configured
   base. Refresh it only between tickets; never discard ignored build state.
3. Start a fresh ephemeral planning agent using the default-owner capability
   from [Route Agents By Task](ticket-lifecycle.md#route-agents-by-task) and invoke:

   ```text
   /to-plan --auto <canonical issue URL>
   ```

   For this workflow, require the plan's Guardrails to distinguish a wrong
   approved-plan seam or repository assumption from an implementation defect.
   The former uses `to-plan`'s one diagnosis and two repair-cycle allowance;
   ordinary in-scope implementation, integration, test, fixture, documentation,
   and CI repairs stay with the ticket owner under the progress rules below.
   The generic `to-plan` compile and fixture examples use its budget here only
   when a wrong plan assumption caused the failure.
   Do not accept a new plan whose repair wording contradicts that distinction.

4. Follow [Route agents by task](ticket-lifecycle.md#route-agents-by-task)
   for bounded read-only discovery or an evidence-justified investigator, using
   only spare agent capacity. Stop at its durable decision boundary.
5. Planning does not occupy an implementation slot or reserve the controller
   lane during read-only work. Honor a delivery-priority yield request through
   [the checkpoint procedure](#yield-a-planner-for-delivery) before another
   mutation; never force an unsafe interruption.
6. At the publish boundary, wait for the controller lane. Let `to-plan` create
   a new v2 revision when the substantive plan changed, or return the identical
   active leaf as a no-op. Never edit a semantic plan payload in place.
7. Refetch all marker comments and verify the unique active leaf, revision
   chain, authenticated-runner author, payload digest, permalink, planned
   branch, planned SHA, replan-report link, and timestamps. After a new leaf is
   verified, minimize its predecessor as `OUTDATED`. When native minimization
   is unavailable, prepend a superseded banner and wrap the unchanged payload
   in `<details>`, then refetch and verify its payload digest. If both
   presentation operations fail after bounded reconciliation, report the
   hygiene failure but continue because the chain is authoritative. Treat
   missing `to-plan` as an issue-local planning blocker; it must not block
   implementation items with current plans.
8. Move the item to `Ready to implement` and refetch its current Status,
   assignment, and usable active plan. Verify the mutation by current field
   value; do not query or inspect its transition event.
9. In `next`, or when an implementation slot is free, move the same item to
   `In progress`, verify the full authority lease, and start its slot. Otherwise
   preserve the assigned verified Ready handoff, release the planner, and
   resume that handoff before new claims when a slot frees.

After a successful handoff, require the planning worktree to be clean with no
retained draft, detach it, snap it to the verified base, and keep it for reuse.
Preserve its exact path, base, and draft only when planning blocks and recovery
requires them.

Project schema mutations are never part of this procedure. Stop with the
required configuration repair when an expected field or option is missing.

Give each planning attempt a 30-minute active-time deadline unless the user or
repository sets another. Pause only verified cooperative-yield time; preserve
consumed time and attempt count across compaction. Agent loss, crash or exhausted
active-time budget is a liveness failure, not intentional yielding:

1. stop the failed planner when possible and release its agent capacity;
2. refetch assignment, current Status, and the marker plan;
3. reconcile an ambiguous comment or Status mutation before retrying;
4. complete an already-verified handoff, or restart a fresh planner in the same
   clean planning worktree;
5. after three failed attempts, preserve the assignment, block that planning
   item, release the lane, and continue unrelated work.

## Yield A Planner For Delivery

Use this in `drain` when actionable delivery, CI repair or review feedback needs
the planner's active-agent capacity. Keep the planning claim and owner.

1. Request a cooperative checkpoint before the planner's next mutation. Let an
   already-started atomic operation finish; reconcile any publication or Status
   write already in flight before releasing capacity. An ambiguous outcome or
   missing acknowledgment keeps affected capacity occupied.
2. Persist the owner/context, worktree, draft path and digest, source/plan/base
   identities, publication/handoff state, used active planning time, remaining
   deadline and attempt count in the existing planning record. Verify the
   retained draft against that digest. Quiesce descendants, reconcile/release
   resource grants and confirm no writer remains. Only then mark it yielded
   and free its actual active-agent capacity, not its planning-lane ownership.
3. Resume the same delivery owner for the actionable event. Preserve the
   planner's context and draft; no ownership transfer or duplicate planner.
   Record the capacity wait and yielded interval under the scheduler's timing
   procedure. Intentional yield consumes no failure attempt and never resets
   time already used. Twelve minutes used then forty yielded leaves eighteen
   active minutes of a thirty-minute budget, including across compaction.
4. After higher-priority delivery work, refetch planning membership, exclusivity,
   source/base, draft and published marker state. Reconcile any already-published
   result and finish its existing handoff rather than republish. If inputs
   changed, invalidate affected draft evidence before continuing under the
   provider's rules. Resume the same planner with its remaining deadline.
5. For a lost owner or missing checkpoint/timing evidence, stop affected writers
   and reconcile before using the existing bounded liveness recovery. Never
   treat an unknown process as quiescent or a stale draft as an approved plan.

Wayfinder shares this capacity procedure only where its provider can checkpoint
and prove quiescence; reconcile its map/issue publication too. If its active
provider cannot yield safely, preserve capacity until its safe boundary and
report the delivery wait; do not bypass its required research/session contracts.

## Resume And Re-plan

Resume an assigned `Todo` item before starting new Todo work:

- run planning when the plan is missing or stale;
- finish the Ready handoff when the plan is current.

Resume an assigned `Ready to implement` item when its current column,
exclusive ownership, and usable active plan pass verification. No historical
Ready event is required. Preserve a missing or invalid plan as a blocked
planning claim without consuming an implementation slot.

Before the Ready or In-progress transition, compare the planned SHA with the
current base:

- accept non-overlapping committed drift after screening the changed files,
  symbols, seams, contracts, and validation;
- for proven routine integration overlap, try the verified amendment route below;
- when overlap is unknown or amendment requirements are not met, retain the
  existing autonomous-replan or human-decision path as appropriate. Unknown
  overlap is never classified as harmless.

### Consume A Verified Integration Amendment

Before a full requeue for routine base integration, inspect the installed
`to-plan` [GitHub contract](../../to-plan/references/github-mode.md) for explicit
integration-amendment capability and its handoff. The baseline full-plan
v1/v2 protocol alone does not supply it. Without that capability, preserve work
and use the existing full-replan path; do not invent an amendment wire format
or infer support from an issue proposing it.

1. Keep the delivery owner, claim, slot, branch, draft/worktree and PR; quiesce
   affected implementation writes at the exact retained candidate. Use the
   provider's classification and independent review in the existing planning
   lane and available capacity. The controller still owns shared publication
   and Project mutations. Do not move the ticket through Todo/Ready merely
   to obtain a supported amendment.
2. Verify the provider-owned effective contract: original source and active
   plan identities/digests, authenticated append-only amendment lineage,
   predecessor continuity without forks/gaps/foreign edits, old/new base and
   exact retained candidate/PR, concrete integration overlap, preserved work,
   invalidated evidence and affected checks/review. Require evidence that
   requirements, acceptance, architecture, qualification and authority remain
   unchanged. Unknown overlap, unsupported preservation or stale artifacts
   block this route; material changes follow full replanning or a stakeholder
   decision under the existing classification contract.
3. Reconcile publication already in flight before retrying. Freshly read back
   one unambiguous effective contract and its independent review, then renew
   the controller's plan lease with those exact identities while retaining the
   original marked plan. Keep Status and owner unchanged. Publication ambiguity
   stops dependent work; no local draft or old-SHA evidence can stand in for
   the verified effective contract.
4. Hand the retained owner and artifacts plus verified effective contract to
   `deliver-spec`. It owns integration, affected verification/review and final
   exact-head evidence. Retain grant consumption and repair history; an amendment
   neither authorizes additional live turns nor resets a qualification gate.
5. On recovery and before material writes, repeat effective-contract integrity,
   current authority and artifact-head validation. Distinguish the amendment's
   retained starting candidate from later verified owner-produced integration
   heads through delivery evidence; an unexplained head change blocks. Pass
   only the original plan schema to the ranker and carry amendments alongside
   it in the lease/handoff. Ranker eligibility alone cannot clear this gate.

### Replan Packet Contract

Classify an unexpected failure by cause, not its file type or whether it occurs
before or after a push. A wrong factual seam or repository assumption in the
approved plan is a mechanical plan mismatch: reserve one focused diagnosis and
at most two repair edit-and-validation cycles under that plan's budget. A wrong
approved design decision, exhausted mechanical budget, changed accepted
contract, or uncertain baseline overlap requires the packet below.

An implementation defect within the accepted outcome, scope, acceptance
criteria, and plan decisions is an ordinary in-scope repair, including
integration, CI, test, fixture, and documentation fixes. The owning agent
records the cause and affected evidence, repairs in its existing slot, and
repeats affected verification and review. The mechanical plan-mismatch budget
does not count these repairs. Apply the [repair progress gate](ticket-lifecycle.md#repair-progress-gate)
when attempts reproduce the same failure; required CI also follows the
[terminal required-CI rule](drain-scheduler.md#terminal-required-ci-parking).

When repository evidence invalidates the approved plan or the required
adjustment exceeds its accepted contract, require the owning ticket agent to
stop writes and return one packet containing:

- disposition: `autonomous-replan` or `human-required`;
- active plan permalink and payload digest;
- exact evidence and invalid assumption;
- current accepted stakeholder contract, upstream policy, and risk posture;
- recommended direction;
- verified base SHA, branch and PR heads, and retained dirty-work summary.

Classify the packet as:

- `autonomous-replan` when accepted behavior, scope, acceptance criteria,
  upstream policy, and risk posture remain unchanged and repository evidence
  supports a contract-realizing resolution, even when it affects a public
  interface, schema, persisted representation, seam, or testing contract;
- `human-required` only when the accepted stakeholder contract or upstream
  policy must change, new security, privacy, or permission policy must be
  established, an unsupported compatibility commitment or irreversible
  migration must be approved, or credible data-loss risk must be accepted.

For `autonomous-replan`, require the evidence supporting that classification.
For `human-required`, require the exact decision plus the authoritative issue,
specification, or ADR that must change. Return no packet when the ticket is
already implemented, superseded, contradicts an ADR, or remains ambiguous after
applying this rule.

### Re-plan A Contract-Preserving Inconsistency

When the owning ticket agent returns an `autonomous-replan` packet, first
classify whether the supported, verified integration-amendment route above
applies. Otherwise use this full lifecycle:

1. Enter the controller lane and revalidate the current authority lease,
   verified base, assignment, Status, plan leaf, branch, worktree and PR.
2. Publish one new comment containing
   `<!-- run-github-project:replan-request:v1 -->` and the exact evidence packet.
   Refetch and verify it.
   If publication or verification fails, keep the ticket In progress and its
   slot occupied.
3. Move the item to Todo and refetch its current Status, assignment, report,
   and retained artifacts. Verify the field value without a transition event.
4. Release the implementation slot without preempting another worker. Preserve
   exclusive assignment, deterministic branch and worktree, open PR, dirty
   partial work, and idle ticket context as one priority replan claim. These
   artifacts no longer count toward the implementation-slot limit.
5. Plan against the current verified base. Pass the retained branch or PR head
   and dirty-work summary as evidence, not as the planning baseline. Permit
   exactly that runner-owned implementation PR during this replan; competing
   or foreign PRs still block.
6. Publish and verify the next plan revision, perform the Ready handoff, then
   reacquire the next free implementation slot ahead of new claims. Resume the
   same ticket context and let it reconcile retained work to the new plan.

The report's predecessor plan identity and exact retained PR/head remain
recovery evidence. A missing or mismatched link preserves a blocked planning
claim until reconciled. Current Todo membership supplies planning authority;
no preceding Ready event or following Todo event is required.

### Pause A Stakeholder Decision

When the verified packet disposition is `human-required`:

1. Publish and verify the marker-owned exact evidence packet.
2. Apply the [ticket-pause procedure](authority-and-pauses.md#pause-one-ticket)
   referencing that packet for the exact decision and authoritative source to
   change. A pending decision never triggers Backlog cleanup.
3. Resume only from a recorded human outcome, not a merge flag or another
   unchanged run. When the outcome keeps implementation with agents, reconcile
   the newly accepted source contract. Give the controlled replanning procedure
   above an `autonomous-replan` packet referencing the decision and prior plan;
   that procedure publishes it once and retains artifacts and repair history.
   Review the new plan automatically before implementation resumes.

### Abandon Partial Work And Return It To Backlog

Use this only after a recorded stakeholder direction explicitly abandons the
partial work. While the item is still in Todo or a later eligible column:

1. Publish and verify the decision-bearing report and exact owned artifacts.
2. Reconcile the explicit PR closure and skill-owned process, resource,
   worktree, and branch cleanup. Preserve any foreign or ambiguous artifact.
3. Verify cleanup, replace the agent role with the configured human-work role,
   and unassign the runner. Keep unresolved cleanup paused in the current
   eligible column; do not transfer an unfinished cleanup lease to Backlog.
4. Return the item to Backlog only as the final verified transfer. Release its
   scheduler resources and perform no further automatic work on it.

If a human moves any active item to Backlog, stop its writers, release capacity,
and preserve/report its assignment and artifacts without issue, PR, or artifact
cleanup. A later run must not resume Backlog cleanup. Only a human promotion
out of Backlog can make it eligible again; labels alone never do so. Revalidate
any retained plan and artifact state once the current column permits work.

Semantic planning blockers are issue-local. Preserve the assignment and retry
them only when authoritative inputs change. Retry transient planner/tool
failures through the bounded reconciled recovery above. Never consume an
implementation slot merely to wait for a planning blocker.

Treat a `to-plan` Blocked result labelled `human-required` as one of these
planning blockers and record a verified decision pause, not Backlog cleanup. No
implementation slot or implementation artifact exists at that stage.

## Scheduling

Use the ranker as the single selector for both lanes. Process classes in this
order:

1. existing implementation and PR claims;
2. contract-preserving replan claims;
3. other resumable Todo and verified handoff claims;
4. new `Ready to implement` candidates;
5. new `Todo` candidates, including configured AFK Wayfinder children.

Exclude Backlog from every scheduling and recovery class.

Within a class, use configured Priority, visible Project position, then issue
number.

In `next`, selecting a Todo item commits the invocation to that one issue:
plan it, hand it off, implement it, merge it, and reconcile it before finishing.
Do not select another issue.

In `drain`, follow the
[Drain Scheduler](drain-scheduler.md#scheduling) for planner dispatch,
active-agent capacity, and cooperative planner checkpoints.

An unclaimed Wayfinder prototype, grilling ticket, or HITL/ambiguous task is a
normal Todo candidate in `next`, but process it only with fresh per-ticket
Wayfinder authority. When the user explicitly names the child, it replaces
Project ordering for new work but never bypasses another durable claim. In
`drain`, an unclaimed HITL child is a human-frontier item while an assigned one
is separate HITL attention; surface both without pausing independent work.
Resume a durable Wayfinder reconciliation claim before either new class. Use a
fresh Wayfinder provider context for each non-research AFK child in `drain`;
`next` keeps its one selected HITL child in the current interactive session, and
only research may fan out multiple ticket resolutions through its required
subagents.

## Migration Gate

Before adopting a new Status schema, apply the human-owned migration gate in
[project configuration](project-config.md). A display-name rename alone does
not require that migration.
