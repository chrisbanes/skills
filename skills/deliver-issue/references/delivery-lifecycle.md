# Deliver an approved outcome

Use this procedure for one approved PR, including a fast-path fix or a group
of issues covered by one plan. The owning controller supplies the scope and
operation grants.

## Executor handoff

1. Open the existing [delivery record](evidence-and-review.md). Reconcile the
   approved task graph, fixed base, checkout, owners, settings, capacity and
   evidence. Carry forward the review contracts, data-handling and spend limits.
   For required live checks, apply [qualification and recovery](qualification-failure.md)
   before each attempt or resume.
2. Invoke the installed [`implement-with-subagents`](../../implement-with-subagents/SKILL.md)
   in implement mode with that graph and record. Where direct invocation is
   unavailable, follow its installed entrypoint. If missing, hold the affected
   implementation or repair and continue independent planning and delivery.
3. Record the returned commits, owners, clean head, validation, independent
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

## Finish gate

Report `ready` when required checks and reviews pass on the final head and
findings are resolved. Report `merged` after merge readback and report tracker closure separately.
Return `no-change` for a verified satisfied outcome with an empty final diff,
`pending` with outstanding gates, or `blocked` with the missing decision or
capability. Preserve the source, PR, head and evidence needed to resume.
