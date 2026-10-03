# Project Controller Handoff

Use this mode only for an active `run-github-project` controller's exclusively
claimed implementation ticket. A direct named-spec request cannot create this
handoff or take over a Project claim.

## Procedure

1. Verify the controller packet under the Project's
   [ticket lifecycle](../../run-github-project/references/ticket-lifecycle.md):
   source/plan identities and task graph, trusted binding, item and runner,
   configuration and authority leases, fixed base, worktree/branch/PR head,
   review evidence, repair usage, and agent capacity. Reconcile live state on
   resume; return gaps to the controller without selecting or claiming work.
   Establish independent-review capability from runtime metadata, without a
   capability-only reviewer. Reconcile retained candidate evidence; solo delivery
   is normal and delegation follows the implementation procedure. Queue temporary
   capacity limits only for capabilities actually needed. For
   asynchronous or persistent live qualification, carry its finite pass
   conditions, required offline harness result, live evidence,
   execution/recovery checkpoint, remaining allowance, and blocker/resume
   condition under [Live qualification and failure
   recovery](qualification-failure.md); withhold dependent dispatch when a
   required live prerequisite is unknown.
2. Accept the verified handoff as authority for continuing in-scope implementation,
   tests and repairs in this checkout. Require no per-file or per-stage permission
   packets. Follow [Evidence and review](evidence-and-review.md) for routine
   corrections, conditional early review and evidence reuse. Material changes
   return to the controller for the appropriate decision; `--auto` cannot expand
   scope or grants. For a supplied integration amendment, verify its effective
   contract and retained candidate under that reference. Preserve owners, work,
   PRs, consumed budgets and live qualification gates. The controller alone
   revalidates claims/leases and schedules continuation.
3. Follow the bundled [implementation procedure](implementation-mode.md) for
   solo or delegated work. Keep the persistent ticket context as delivery lead;
   it may implement tightly coupled work directly. Delegate when justified by
   independence, isolation or specialist investigation, fit descendants within
   actual spare Project capacity, and preserve controller scheduling priority.
   Reuse the existing delivery record for ownership and acceptance evidence.
4. Before any push, satisfy the Project's
   [review contracts](../../run-github-project/references/review-contracts.md).
   Give the single independent reviewer the
   [delivery record](evidence-and-review.md) and all applicable contracts.
   Record coverage at the final clean head; run only missing or invalidated
   contracts. Return repairs to their owners and renew affected evidence. The
   default route requires no external review skill or tracker setup; explicitly
   invoked providers retain their actual scope, roles and capacity requirements.
   Report missing coverage rather than weakening a provider. Never waive final
   review.
5. Reuse the supplied branch and verified PR. After review, push and reconcile
   the exact head; create one draft PR only for a nonempty integrated diff.
   Use `Fixes #<ticket>` for `closing-keyword`, or a non-closing issue link for
   `close-after-merge`. Mark ready and verify that state when applicable checks
   and reviews cover the final head. For an empty diff, return `no-change` and
   verification evidence for controller reconciliation.
6. Use `shepherd` for feedback and PR operations, with code repairs through
   the implementation owner, coordinating any necessary reassignment only after
   the previous writer is quiescent. Apply Project verification,
   repair, monitoring, and CI-parking rules
   instead of generic shepherd cadence or the standalone 30-minute handback.
   In `drain`, process controller-discovered actionable events using its remote
   snapshot; do not start a second polling loop or evidence helper. Yield exact
   PR/head, checks, feedback IDs, review coverage, and pending gates between
   passes; resume the same context when actionable. Remote waiting consumes
   no active-agent capacity.
7. Return `ready`, `pending`, `blocked`, or `no-change` with exact evidence.
   The controller alone claims, assigns, changes labels/Project Status, records
   [ticket pauses](../../run-github-project/references/authority-and-pauses.md),
   manages capacity, merges, closes issues, and reconciles terminal state.
   Return missing grants and material decisions to that controller even when
   its invocation includes `--auto-merge`.

## Finish Gate

Return the current head, effective source/plan/amendment identities, validation
provenance and applicability, findings/dispositions, review coverage, PR identity
and exact pending/blocking operation. Preserve artifacts on pending
or blocked results. The controller's finish gate owns the board outcome.
