# Plan and deliver an outcome

Use this procedure for one outcome intended for one PR, including a fast-path
fix or a group of issues covered by one plan. The owning controller supplies
the scope and operation grants.

## Prepare a standalone planning checkout

Before invoking tracker-mode `to-plan`, verify the bound target branch and
resolve its exact tip SHA through the selected code host. Reconcile any
existing planning checkout and draft for this outcome. Use an idle, isolated
checkout detached at that SHA. Reuse an owned planning checkout only if its
state and retained draft inventory match the record. Otherwise
[create and verify](../../implement-with-subagents/references/checkout-lifecycle.md#create)
one at the exact SHA and [record](../../implement-with-subagents/references/checkout-lifecycle.md#record)
its identity and ownership. Stop on unknown ownership or baseline and report
the evidence needed to proceed.

Pass the verified checkout path, target branch and base SHA in the live
controller handoff. Preserve drafts with their baseline. If the base moves,
apply the planner's baseline-drift rules before reusing the draft or its
evidence. Board-owned planning uses the board controller's checkout procedure.

## Executor handoff

1. Open the existing [delivery record](evidence-and-review.md). Reconcile the
   approved task graph, fixed base, owners, settings, capacity and
   evidence. Carry forward the review contracts, data-handling and spend limits.
   For required live checks, apply [qualification and recovery](qualification-failure.md)
   before each attempt or resume. Verify that the installed
   [`implement-with-subagents`](../../implement-with-subagents/SKILL.md)
   entrypoint is available before allocating a checkout. If missing, hold the
   affected implementation or repair and continue independent work.
2. For standalone delivery, verify the approved base against the bound target
   branch and record its exact SHA. Reconcile any existing checkout, branch
   and PR for this outcome before allocating another checkout. Reuse a clean,
   isolated checkout only when its recorded ownership, branch, base and
   candidate HEAD match and no other writer uses it. When recovering an
   existing PR without a checkout, attach its recorded task branch in an
   isolated checkout at the verified PR head. Resolve divergence before
   attaching. For new work, [create](../../implement-with-subagents/references/checkout-lifecycle.md#create)
   an isolated checkout and unique task branch at the verified base SHA, even
   when the invocation started on another branch. [Record](../../implement-with-subagents/references/checkout-lifecycle.md#record)
   the path, branch, base, HEAD and ownership. Preserve unrelated work and
   stop on unresolved divergence or ownership. For a board handoff use the
   controller's verified checkout.
3. Resolve [which full checks PR CI can supply](evidence-and-review.md#implementation-and-validation)
   from the selected host's required checks and the applicable CI configuration.
   Pass their exact names and covered validation, along with required pre-push
   checks, to the executor. Recheck applicability when the candidate or its CI
   inputs change, including on repair.
4. Invoke `implement-with-subagents` in implement mode with the checkout,
   branch, fixed base, graph, check requirements and record. Where direct
   invocation is unavailable, follow its installed entrypoint.
5. Record the returned commits, owners, clean head, validation, independent
   review and named pending CI checks. Require applicable review coverage and
   passing pre-push checks on that head. Return missing coverage to the executor.
   For an empty final diff, verify full acceptance and follow
   [no-change closure](provider-bindings.md#verified-no-change-closure) before any PR operation.

## Publish and follow the PR

1. Open or update one draft PR for the reviewed head. Verify its head, tracker
   links and closure intent through the [provider bindings](provider-bindings.md).
   Apply [PR review timing](../../shepherd/references/pr-review-timing.md) to start external review while CI runs.
2. Use `shepherd` for CI and PR feedback. For an in-scope repair, resume the
   executor with the finding, current head and delivery record. Verify the
   returned repair before pushing. Route changes to scope, qualification or
   permissions back to planning. Board tickets use their controller’s waiting
   policy. Standalone runs use [wait and resume](issue-lifecycle.md#wait-and-resume).
3. Merge or close only with the applicable grant and provider readback.
   For board tickets, return the outcome to the controller for both operations.

## Account for the standalone checkout

Before handing back a standalone outcome, [account](../../implement-with-subagents/references/checkout-lifecycle.md#account)
for its planning and implementation checkouts. Reconcile any recorded
retirement before retrying cleanup. Use the shared
[retire steps](../../implement-with-subagents/references/checkout-lifecycle.md#retire)
for an owned planning checkout after verified plan handoff when no writer or
pending decision needs it and its drafts and evidence are accounted for.
Preserve and report a checkout that holds a pending plan or a human stop.

Retain the implementation checkout for unfinished work, pending PRs, human
stops, unknown outcomes or ownership, or when it holds work still needed for
repair or remaining scope. Preserve pre-existing, adopted, pinned and shared
checkouts and branches.

For a delivered outcome, quiesce writers and verify that the clean run-created
checkout holds the exact delivered PR head with authoritative merge readback,
or the exact integrated base used for verified no-change acceptance with
verified tracker closure. Preserve the delivery record and evidence needed for
any pending tracker operation. Apply the same retire steps
and verify removal or host-cleanup handoff. After a verified merge, remove only
the run-created local task branch after checking it is unused and still at the
delivered head. Guard removal with the expected ref SHA to preserve concurrent
changes. Verify branch removal and keep the branch on no-change. Report
cleanup as incomplete if a required operation or readback fails.

## Finish gate

Report `ready` when required checks and reviews pass on the final head and
findings are resolved. Report `merged` after merge readback and report tracker closure separately.
Return `no-change` for a verified satisfied outcome with an empty final diff,
`pending` with outstanding gates, or `blocked` with the missing decision or
capability. Preserve the source, PR, head and evidence needed to resume.
