# Project Controller Handoff

Use this mode only for an active `run-project` controller's exclusively
claimed implementation ticket. A direct named-issue request cannot create this
handoff or take over a Project claim.

## Procedure

1. Verify the controller's independently selected providers under
   [Delivery bindings](provider-bindings.md), then verify its packet under the Project's
   [ticket lifecycle](ticket-lifecycle.md):
   source/plan identities and task graph, trusted bindings, item and runner,
   configuration and authority leases, fixed base, worktree/branch/PR head,
   review evidence, repair usage, agent capacity, active revision evidence folder
   and controller-retained preservation baseline. Reconcile live state on
   resume; return gaps to the controller without selecting or claiming work.
   Establish independent-review capability from runtime metadata, without a
   capability-only reviewer. Reconcile retained candidate evidence and the
   controller's implementation routing inputs. Queue temporary
   capacity limits only for capabilities actually needed. For
   asynchronous or persistent live qualification, carry its finite pass
   conditions, required offline harness result, live evidence,
   execution/recovery checkpoint, remaining allowance, and blocker/resume
   condition under [Live qualification and failure
   recovery](qualification-failure.md); withhold dependent dispatch when a
   required live prerequisite is unknown.
2. Accept the verified handoff as authority for continuing in-scope implementation,
   tests and repairs in this checkout. Require no per-file or per-stage permission
   packets. Follow [Evidence and review](evidence-and-review.md) for
   checkpoint feedback, validation cadence, routine corrections, conditional
   early review and evidence reuse. Material changes
   return to the controller for the appropriate decision; `--auto` cannot expand
   scope or grants. For a supplied integration amendment, verify its effective
   contract and retained candidate under that reference. Preserve owners, work,
   PRs, consumed budgets and live qualification gates. The controller alone
   revalidates claims/leases and schedules continuation.
3. Follow the bundled [implementation procedure](implementation-mode.md) for
   ownership preflight. Use the persistent ticket context as delivery lead
   and compare its actual settings to the invocation's required implementation
   settings. Fit worker routes within authorized spare Project capacity and
   preserve controller scheduling priority. Record the route or precise blocker
   in the existing delivery record and return it to the controller.
   For a handoff whose active plan is a controller fast-path revision, apply
   the [fast path](fast-path.md) and return its escalation packet to the
   controller as soon as a condition fails.
4. Before any push, satisfy the Project's
   [review contracts](review-contracts.md).
   Give the single independent reviewer the
   [delivery record](evidence-and-review.md) and all applicable contracts.
   Record coverage at the final clean head; run only missing or invalidated
   contracts. Return repairs to their owners and renew affected evidence. The
   default route requires no external review skill or tracker setup; explicitly
   invoked providers retain their actual scope, roles and capacity requirements.
   Report missing coverage rather than weakening a provider. Never waive final
   review.
5. Reuse the supplied branch and verified change request. After review, push and
   reconcile
   the exact head; create one draft PR only for a nonempty integrated diff.
   Open/update through the code-host binding and link through the selected
   provider pair. Use closing keywords only for verified native tracker closure
   under `closing-keyword`; otherwise use a non-closing link for
   `close-after-merge`. Verify the complete effective closing-reference set.
   Apply [PR review timing](pr-review-timing.md) to start
   applicable external review while CI runs, preferring verified draft review and otherwise
   permitting earlier PR readiness. Verify that state separately from delivery
   `ready`, which requires all required checks, reviews and finding dispositions
   applicable to the final head. For an empty diff, return `no-change` and
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
   Include the revision folder and written paths under
   [evidence isolation](evidence-and-review.md#isolate-plan-revision-evidence);
   controller preservation verification is required before accepting the handoff.
   `pending` names only remote or controller-owned gates; never return while a
   reviewer or helper you launched is still running. The controller alone
   claims, assigns, changes labels/Project Status, records
   [ticket pauses](authority-and-pauses.md),
   manages capacity, merges, closes issues, and reconciles terminal state.
   Return missing grants and material decisions to that controller even when
   its invocation has merge permission.

## Finish Gate

Return the current head, effective source/plan/amendment identities, validation
provenance and applicability, findings/dispositions, review coverage, PR identity
and exact pending/blocking operation. Preserve artifacts on pending
or blocked results. The controller's finish gate owns the board outcome.
