# Planning Lane

Use this lifecycle for Project items in `Planning` and for the verified handoff
into implementation.

Configured Wayfinder children take the separate integration branch in
[Wayfinder Planning Lane](wayfinder-lane.md). They share this lane's scheduling
class and non-preemption rules, but never use the implementation-plan marker,
Ready handoff, or implementation lifecycle below.

## Authority And Plan State

Require both:

1. the exact `ready-for-agent` label; and
2. the latest transition into `Planning` to be either:
   - a non-automated event by a configured execution approver; or
   - the authenticated runner's non-automated machine requeue backed by its
     verified earlier Ready handoff and runner-authored replan report.

The human transition authorizes autonomous plan publication and implementation.
The verified Ready handoff carries that authority across a contract-preserving
machine requeue. Ordinary issue-body or comment edits do not revoke it. A newer
human transition into `Planning` explicitly requests a new plan.

Recognize implementation-plan comments containing either:

```html
<!-- to-plan:implementation-plan:v1 -->
<!-- to-plan:implementation-plan:v2 -->
```

Treat a v1 comment as a revision-one root. Require each v2 comment to record a
positive revision, the predecessor permalink or `none`, and the triggering
replan-report permalink or `none`. Hydrate minimized comments too. Require one
runner-authored root, contiguous revisions, no forks, and one unminimized leaf.
That leaf is the active implementation plan. A missing predecessor, duplicate
revision, fork, foreign marker, or minimized leaf is a semantic planning
blocker.

Classify the active leaf as current in Planning only when its semantic payload
was published at or after the authorizing Planning event and its planned branch
matches the configured base. Treat the predecessor as stale immediately after
a machine requeue. Compute its lease digest from the semantic plan payload,
excluding a superseded banner or presentation-only `<details>` wrapper.

Do not recognize `## Agent Brief` or any unmarked fallback. Record the active
and predecessor comment IDs, permalinks, revisions, authors, payload digests,
creation, publication and update times, planned branch and SHA, replan report,
and minimized state in the authority lease.

## Plan A Planning Item

1. Enter the controller lane, assign the issue exclusively to the authenticated
   user, refetch and verify the assignment, then release the lane. Reconcile
   an ambiguous assignment before retrying. Preserve the assignment through
   planning and implementation.
2. Use one dedicated, reusable, clean planning worktree at a stable
   controller-recorded path outside the checkout, detached at the configured
   base. Refresh it only between tickets; never discard ignored build state.
3. Start a fresh ephemeral planning agent using the default-owner capability
   from [Route Agents By Task](../SKILL.md#route-agents-by-task) and invoke:

   ```text
   /to-plan --auto <canonical issue URL>
   ```

4. Allow bounded read-only discovery descendants from currently spare agent
   capacity. They never own the ticket or mutate state. When repository
   evidence exposes one specific unresolved architecture, security, rendering,
   performance, or data-integrity question, record why the default owner is
   insufficient and permit one bounded read-only exceptional investigator for
   that question. Topic, scope, plan size, or language count never supplies
   that evidence. Stop at the durable decision boundary when the answer
   requires a new product, public contract, architecture, or safety decision;
   never replace the whole planner.
5. Never preempt planning after it starts. Planning does not occupy an
   implementation slot and does not reserve the controller lane during read-only
   work.
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
8. Move the item to `Ready to implement` as the authenticated runner. Refetch
   and require a non-automated Ready transition by that runner after both the
   Planning event and the plan's latest update. That reconciled event attests
   that `to-plan --auto` revalidated an identical older plan even when it made
   no comment edit.
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

Give each planning attempt a 30-minute deadline unless the user or repository
sets another. Agent loss, crash, or timeout is a liveness failure, not
preemption:

1. stop the failed planner when possible and release its agent capacity;
2. refetch assignment, Status, Planning and Ready events, and the marker plan;
3. reconcile an ambiguous comment or Status mutation before retrying;
4. complete an already-verified handoff, or restart a fresh planner in the same
   clean planning worktree;
5. after three failed attempts, preserve the assignment, block that planning
   item, release the lane, and continue unrelated work.

## Resume And Re-plan

Resume an assigned `Planning` item before starting new Planning work:

- run planning when the plan is missing or stale;
- finish the Ready handoff when the plan is current.

Resume an assigned `Ready to implement` item only when its current plan and the
later runner-authored Ready event form a verified handoff. Otherwise preserve
it as a blocked planning claim without consuming an implementation slot.

Before the Ready or In-progress transition, compare the planned SHA with the
current base:

- accept non-overlapping committed drift after screening the changed files,
  symbols, seams, contracts, and validation;
- use the autonomous replan path when drift overlaps or overlap is uncertain.

### Replan Packet Contract

When repository evidence invalidates the approved plan, require the owning
ticket agent to stop writes and return one packet containing:

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

When the owning ticket agent returns an `autonomous-replan` packet:

1. Enter the controller lane and revalidate the current authority lease,
   verified base, assignment, Status, plan leaf, branch, worktree and PR.
2. Publish one new comment containing
   `<!-- run-github-project:replan-request:v1 -->` and the exact evidence packet.
   Refetch and verify it.
   If publication or verification fails, keep the ticket In progress and its
   slot occupied.
3. Move the item to Planning as the runner, refetch it, and require the new
   transition to follow the verified report and preceding Ready handoff.
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

The ranker requires the verified report, preceding Ready handoff, and
runner-authored Planning transition. A missing or mismatched link preserves a
blocked planning claim. Any fresh human Planning transition supersedes the
machine requeue and requests a new plan.

### Return Human Work To Backlog

When the verified packet disposition is `human-required`:

1. Publish and verify the same marker-owned exact evidence packet.
2. Move the item to the configured Backlog option and verify the transition.
   Do not clean anything when either the report or transition is ambiguous.
3. Comment on and close any runner-owned implementation PR, linking the durable
   report. Reconcile an ambiguous close before continuing.
4. Resolve active processes and named-resource grants, verify exact skill
   ownership, then deliberately remove the dirty or clean ticket worktree and
   delete its skill-created local and remote branches. Never delete a foreign
   or ambiguously owned artifact.
5. Refetch and require no active process or resource grant, no open runner PR,
   and no exact skill-owned worktree, local branch, or remote branch. Treat
   absent artifacts as an idempotent cleanup success after a restart.
6. Unassign the runner only after that cleanup finish state is verified, then
   refetch and require that it no longer owns the issue. Until this final
   mutation reconciles, the assignment is the durable cleanup lease returned
   by `resume-backlog-cleanup`.
7. Discard the ticket agent and release every scheduler resource. Report any
   residue that could not be reconciled, but do not retain a claim or slot for
   the Backlog item.

A later non-automated Backlog-to-Planning transition by an execution approver
is fresh authority. Start from the verified base, recover no deleted partial
code, and publish a new plan revision that supersedes the historical leaf.
Never move a human-owned Backlog item to Planning automatically.

Semantic planning blockers are issue-local. Preserve the assignment and retry
them only when authoritative inputs change. Retry transient planner/tool
failures through the bounded reconciled recovery above. Never consume an
implementation slot merely to wait for a planning blocker.

Treat a `to-plan` Blocked result labelled `human-required` as one of these
planning blockers, not as the worker packet that enters Backlog cleanup. No
implementation slot or implementation artifact exists at that stage.

## Scheduling

Use the ranker as the single selector for both lanes. Process classes in this
order:

1. interrupted Backlog cleanup claims;
2. existing implementation and PR claims;
3. contract-preserving replan claims;
4. other resumable Planning and verified handoff claims;
5. new `Ready to implement` candidates;
6. new `Planning` candidates, including configured AFK Wayfinder children.

Within a class, use configured Priority, visible Project position, then issue
number.

In `next`, selecting a Planning item commits the invocation to that one issue:
plan it, hand it off, implement it, merge it, and reconcile it before finishing.
Do not select another issue.

In `drain`, follow the
[Drain Scheduler](drain-scheduler.md#scheduling) for planner dispatch,
active-agent capacity, and non-preemption.

An unclaimed Wayfinder prototype, grilling ticket, or HITL/ambiguous task is a
normal Planning candidate in `next`, but process it only with fresh per-ticket
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

Before adopting this schema:

1. require zero existing `In progress` items;
2. have a human create and verify `Backlog`, `Planning`, and
   `Ready to implement`;
3. configure their option IDs and execution approver logins;
4. have an execution approver move every legacy Ready item to `Planning`;
5. run `to-plan --auto` for each item, including those with an existing marker,
   before creating its runner-authored Ready handoff.

Do not automate Project option creation or rename. Do not preserve an Agent
Brief compatibility path.
