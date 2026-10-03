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
   Resolve independent-reviewer capability before any implementation. Resolve
   worker capability and capacity before new nontrivial implementation or a
   worker-owned repair; apply `deliver-spec`'s low-risk lead-edit exception as
   written. Reconcile existing candidate evidence without reassigning accepted
   work or requiring a worker merely to finish review and delivery. Review can
   follow implementation sequentially. Queue temporarily busy capacity; report
   a capability blocker only when the required capability cannot run. For
   asynchronous or persistent live qualification, carry its finite pass
   conditions, required offline harness result, live evidence,
   execution/recovery checkpoint, remaining allowance, and blocker/resume
   condition under [Live qualification and failure
   recovery](qualification-failure.md); withhold dependent dispatch when a
   required live prerequisite is unknown.
2. Accept the verified execution handoff as satisfying the implementation
   workflow's source, plan, and user-approved test-seam prerequisites. Require
   no further human confirmation for an in-scope stage. Independently review
   the plan against source, criteria, repository facts, dependencies, and tests
   unless current evidence covers those exact inputs. Return findings to the
   controller for `to-plan --auto` repair and a verified handoff; automatically
   review repaired inputs. A verified `--auto` grant may satisfy `to-plan`'s
   GitHub publication-approval pause, but route revised-plan publication and
   readback through `to-plan` and require its verified handoff before resuming.
   `--auto` does not authorize a material change to accepted behavior, scope,
   acceptance, policy, or risk; return those decisions to the stakeholder. For
   a supplied integration amendment, apply
   [Evidence and review](evidence-and-review.md) to the installed planner's
   verified effective contract and retained candidate. Preserve work, owner, PR
   and budgets; return unsupported or invalid handoffs to the controller. It
   alone revalidates claims/leases and schedules continuation. Preserve Project
   repair budgets and replan rules. Follow [Live qualification and failure
   recovery](qualification-failure.md) when the accepted source requires
   asynchronous or persistent live qualification. A routine
   contract-preserving repair continues under its existing owner and progress
   gate without renewed approval; a material contract or allowance change
   returns to the controller for one consolidated decision.
3. Apply `deliver-spec`'s documented low-risk lead-edit exception where it
   qualifies. Apply [Evidence and review](evidence-and-review.md)'s
   implementation and validation procedure to every path, including that
   initial lead edit. For all other supplied implementation, follow the bundled
   [implementation procedure](implementation-mode.md), which delegates single,
   sequential and concurrent tasks to workers and owns their implementation
   gates. Keep the persistent ticket context as architecture, integration,
   acceptance and non-merge PR delivery lead. Count descendants against actual
   spare Project capacity and preserve controller scheduling priority. Do not
   transfer a delegated task or repair to the lead.
4. Before any push, satisfy the Project's
   [review contracts](../../run-github-project/references/review-contracts.md).
   Give the single independent reviewer the
   [self-contained packet](evidence-and-review.md) and all applicable contracts.
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
   the original implementation owner; only repairs to the lead's permitted
   initial direct edit remain with the lead. Never move a worker's repair to
   the lead. Apply Project verification,
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
