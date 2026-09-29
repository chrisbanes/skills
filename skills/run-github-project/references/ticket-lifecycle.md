# Ticket lifecycle

## Route agents by task

Apply the shared
[selection and handoff reference](subagent-selection.md)
when available. The Project-specific routing and authority rules below remain
binding. If the trusted configuration has Agent Setup, follow
[agent routing](agent-routing.md) for eligible runtime profiles; keep the
selected lead model unchanged.

Route by behavioral capability, not local profile/model names. Use a read-only
discovery helper for files/seams/tests/ownership, evidence helper for bounded
mechanical analysis, default owner for normal planning/implementation/review
repairs, and exceptional investigator only for concrete unresolved architecture,
security, rendering, performance, or data-integrity evidence that the default
owner cannot safely resolve. Record task, portable role, actual runtime choice,
and exceptional justification in a routing ledger. Generic runtimes encode role
and boundaries in prompt; unavailable controls use runtime default.

Default owners handle every planner and normal ticket. Helpers are bounded
read-only and never substitute for an owner. Do not call broad scope, API,
multiple modules, destructive work, or a large plan exceptional evidence. An
exceptional question may use a spare-capacity read-only investigator; product,
public-contract, architecture, or safety decisions stop at their durable
boundary. Helpers get one question, immutable SHA, repository/worktree, ticket
contract, and exact evidence. They never edit, claim, push, comment, resolve,
merge, or mutate Project state; the owner reconciles their evidence.

## Implement in ticket context

For each occupied slot, refresh verified base; create/reuse a clean stable
skill-owned worktree with exact base identity; create new
`cb/issue-<number>-<short-slug>` branch unless instructions say otherwise, or
resume exact verified PR head without replacement. Stop on divergence, access
ambiguity, or changed head. Start one fresh ticket-specific context per slot,
pair it until free, and resume it for every pass. Pass repository/worktree/
branch/base, ticket and approved plan, authority leases, durable repair usage,
HEAD/check/review/PR events, and worker contract. Verify the worker returns a
clean focused final HEAD with coherent commits, current verification and review
evidence, and no unrelated change, or a complete replan packet with no later
mutation.

Persist plan-mismatch repair consumption by ticket, plan permalink, and payload
digest. Count only a wrong factual seam or repository assumption in the approved
plan, as classified by the [replan contract](planning-lane.md#replan-packet-contract).
Initialize only for a verified new plan; reserve each such diagnosis or repair
before it starts, preserve usage across replacement, restart, and reacquisition,
and block plan-mismatch repair if prior usage is uncertain. Worker: obey trusted
instructions and own
worktree/branch/PR only; never controller mutations; treat plan as approved
outcome, make evidence-backed in-scope adjustments under the
[replan packet contract](planning-lane.md#replan-packet-contract), and return a
packet only when that contract requires it; inspect minimal scope; invoke `tdd`
at the agreed plan seam before behavioral change; work red-green vertical
slices; run focused checks per slice and full applicable checks on the frozen
candidate; complete review on that candidate; make coherent focused commits;
revalidate authority and pre-push, push/open-update PR, reconcile remote result,
and return exact SHA/evidence.

### Repair progress gate

For an ordinary in-scope repair outside required CI, compare the failure after
each repair with its previous terminal result. A second occurrence of the same
sanitized failure with no new diagnostic direction is a stall, not a reason to
repeat the edit or move the issue to Planning. Ask one bounded read-only evidence
helper about that failure and give the result to the same ticket owner. Resume
repair only with a concrete new direction. Otherwise preserve the claim and
worktree as an exact ticket-local blocker and continue unrelated work. Do not
repeat the helper on unchanged evidence. Expected red tests in a test-first
slice are not repair failures. Required CI uses its separate
[three-round parking gate](drain-scheduler.md#terminal-required-ci-parking).

## Pre-push, shepherd, and merge

Before the first push, complete every review contract on the frozen candidate,
preferably using `review-and-simplify-changes` and `ponytail-review` for their
respective contracts. Fix every actionable finding or give an evidence-based
disposition except for explicitly very low priority findings. If a repair
changes the reviewed candidate, rerun affected checks and review the changed
range plus its interaction with the previously reviewed effective diff. Broaden to
full verification and all review contracts when an earlier result is
invalidated or the affected scope cannot be bounded. Before every push, verify
that the combined evidence covers the exact final HEAD and that no actionable
finding remains; never treat unchanged prior checks as proof for changed code.

PRs include `Fixes #<ticket>`, rationale, validation, and residual risks. Keep
claim/agent while open; drain follows Remote Waiting and terminal-CI parking,
next shepherds directly. For feedback, batch fixes in same worktree, reapply TDD
for behavior, repeat affected validation and review against the new final HEAD,
reply inline where possible, and
resolve only after reply and required fix. Address every comment unless explicitly
very low priority; stop for material maintainer direction. Silence is not approval:
merge only with required reviews/checks terminal-green, mergeable PR, and
recorded authority. Use scheduler/wait mechanisms, never long sleep.

Before merge, revalidate authority, approvals, CI, mergeability, configuration,
and merge authority. Follow configured merge/queue, serialize oldest ready slot
unless dependency requires otherwise, and reconcile exact merge. Enforce closure
policy, reconcile Done automation without archiving/removing directly, stop on
unexpected outcomes, cleanly detach/snap worktree to base without `git clean`,
delete only skill-created local ticket branch, discard agent, refresh other PRs,
and query Project completely. `next` finishes one selected terminal issue,
Wayfinder child, tail triage, or ready epic; otherwise report human frontier.
`drain` follows its scheduler finish gate. On blocked/ambiguous next work,
preserve worktree, branch, PR, assignment, and In-progress state.
