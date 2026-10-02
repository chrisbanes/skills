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
mechanical analysis, default owner for normal planning, implementation, and
repairs, and a fresh read-only reviewer for independent acceptance. Use an
exceptional investigator only for concrete unresolved architecture,
security, rendering, performance, or data-integrity evidence that the default
owner cannot safely resolve. Record task, actual runtime choice, and exceptional
justification in the existing ownership record. Generic runtimes encode role
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
plan, as classified by the [replan contract](todo-lane.md#replan-packet-contract).
Initialize only for a verified new plan; reserve each such diagnosis or repair
before it starts, preserve usage across replacement, restart, and reacquisition,
and block plan-mismatch repair if prior usage is uncertain. Worker: obey trusted
instructions and own
worktree/branch/PR only; never controller mutations; treat plan as approved
outcome, make evidence-backed in-scope adjustments under the
[replan packet contract](todo-lane.md#replan-packet-contract), and return a
packet only when that contract requires it. For every ordinary implementation
ticket, invoke `deliver-spec` with this verified packet under its
[Project handoff procedure](../../deliver-spec/references/project-handoff.md).
Keep the persistent ticket context as delivery lead and integration owner.
`deliver-spec` owns the implementation-worker and integration procedure;
preserve its same-owner repair rule and fit all descendants within the
controller's actual spare capacity. Missing required capability blocks only
that ticket.
Wayfinder, triage, and epic lanes keep their own procedures.

### Repair progress gate

For an ordinary in-scope repair outside required CI, compare the failure after
each repair with its previous terminal result. A second occurrence of the same
sanitized failure with no new diagnostic direction is a stall, not a reason to
repeat the edit or move the issue to Todo. Ask one bounded read-only evidence
helper about that failure and give the result to the same ticket owner. Resume
repair only with a concrete new direction. Otherwise preserve the claim and
worktree as an exact ticket-local blocker and continue unrelated work. If no
Agent Setup exists, use the shared capability-based selection for an available
read-only evidence helper. If Agent Setup exists but no eligible
`read-only-evidence` profile is configured, or no runtime helper is available,
preserve that same blocker and report the missing helper capability without
retrying or rerouting the owner.
Do not repeat the helper on unchanged evidence. Expected red tests in a
test-first slice are not repair failures. In `drain`, required CI uses its
[three-round parking gate](drain-scheduler.md#terminal-required-ci-parking).
In `next`, count a required-CI repair round only after the owner makes a
bounded fix or evidence-supported rerun and the required check again reaches
terminal failure at a verified PR head. Keep that count in durable ticket
evidence across interruption and resumption. After three rounds with the same
sanitized failure and no new diagnostic direction, stop `next` with the exact
check and log evidence. Preserve the claim, owner, worktree, branch, PR, and
`In progress` status; do not park or release the slot. Resume after revalidating
the claim when a fresh read shows the failed required check terminal-green for
the exact current PR head, then recheck all other applicable review and merge
gates. Otherwise resume only with a new diagnostic direction or explicit
authority for one focused investigation. A new run ID alone does not reset the
count; never repeat an unchanged rerun to reset it.

## Pre-push, shepherd, and merge

Before the first push, give every review contract on the frozen candidate to
one fresh independent read-only reviewer. Reuse `deliver-spec`'s review for each
contract it explicitly covered at that head; run only missing contracts, not a
duplicate correctness pass. Fix every actionable finding or give an evidence-based
disposition except for explicitly very low priority findings. If a repair
changes the reviewed candidate, rerun affected checks and review the changed
range plus its interaction with the previously reviewed effective diff. Broaden to
full verification and all review contracts when an earlier result is
invalidated or the affected scope cannot be bounded. Before every push, verify
that the combined evidence covers the exact final HEAD and that no actionable
finding remains; never treat unchanged prior checks as proof for changed code.

PRs include the configured closing or non-closing issue link, rationale,
validation, and residual risks. Keep claim/agent while open; drain follows
Remote Waiting and terminal-CI parking,
next shepherds directly through `deliver-spec`'s Project mode. For feedback,
invoke `shepherd` for triage and PR actions. Keep code repairs with the ticket
owner or original delegated implementation owners, integrating delegated commits
in the same ticket worktree. Reapply TDD for behavior and repeat affected
validation and review against the new final HEAD, reply inline where possible,
and resolve only after reply
and required fix. Address every comment unless explicitly
very low priority; return material maintainer direction to the controller for
a ticket-local decision pause. Silence is not approval:
merge only with required reviews/checks terminal-green, mergeable PR, and
recorded authority. Use scheduler/wait mechanisms, never long sleep.

Before merge, revalidate authority, approvals, CI, mergeability, configuration,
and merge authority. When a merge or associated closure grant is absent,
apply the [ticket-pause procedure](authority-and-pauses.md#pause-one-ticket).
Follow configured merge/queue, serialize oldest ready slot
unless dependency requires otherwise, and reconcile exact merge. Enforce closure
policy, reconcile Done automation without archiving/removing directly, stop on
unexpected outcomes, cleanly detach/snap worktree to base without `git clean`,
delete only skill-created local ticket branch, discard agent, refresh other PRs,
and query Project completely. `next` finishes one selected terminal issue,
Wayfinder child, tail triage, or ready epic; otherwise report human frontier.
`drain` follows its scheduler finish gate. On blocked/ambiguous next work,
preserve worktree, branch, PR, assignment, and In-progress state.
