# Ticket lifecycle

## Route agents by task

Apply the shared
[selection and handoff reference](subagent-selection.md)
when available. The Project-specific routing and authority rules below remain
binding.

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
HEAD/check/review/PR events, and worker contract. Verify the worker returns one
focused reviewed freshly verified commit with no unrelated change, or a complete
replan packet with no later mutation.

Persist mechanical-repair consumption by ticket, plan permalink, and payload
digest. Initialize only for verified new plan; reserve each diagnosis/repair
before it starts, preserve usage across replacement/restart/reacquisition, and
block if prior usage is uncertain. Worker: obey trusted instructions and own
worktree/branch/PR only; never controller mutations; treat plan as approved
outcome, follow only its bounded mechanical repairs, otherwise return the
[replan packet](planning-lane.md#replan-packet-contract); inspect minimal scope;
invoke `tdd` at the agreed plan seam before behavioral change; work red-green
vertical slices; run focused and final checks/locks; complete correctness and
standards review; make one focused commit; revalidate authority and pre-push,
push/open-update PR, reconcile remote result, and return exact SHA/evidence.

## Pre-push, shepherd, and merge

Before every push, complete reuse/clarity/efficiency and over-engineering review
contracts, preferably `review-and-simplify-changes` and `ponytail-review`. Fix
every actionable finding or evidence-based disposition except explicitly very
low priority. If files change, rerun focused/full verification and correctness
review, update commit, then rerun pre-push checks against final diff. Push only
clean exact `HEAD` with no remaining findings.

PRs include `Fixes #<ticket>`, rationale, validation, and residual risks. Keep
claim/agent while open; drain follows Remote Waiting and terminal-CI parking,
next shepherds directly. For feedback, batch fixes in same worktree, reapply TDD
for behavior, validate/review/pre-push once, reply inline where possible, and
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
