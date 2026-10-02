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
   a capability blocker only when the required capability cannot run.
2. Accept the verified execution handoff as satisfying the implementation
   workflow's source, plan, and user-approved test-seam prerequisites. Require
   no further human confirmation for an in-scope stage. Independently review
   the plan against source, criteria, repository facts, dependencies, and tests
   unless current evidence covers those exact inputs. Return findings to the
   controller for `to-plan --auto` repair and a verified handoff; automatically
   review repaired inputs. Preserve Project repair budgets and replan rules.
3. Follow the bundled [implementation procedure](implementation-mode.md) with
   the supplied tasks and materialized source, including its low-risk lead-edit
   exception. It delegates all other single, sequential, and concurrent
   implementation to workers under the shared procedure.
   Keep the persistent ticket context as architecture, integration, acceptance,
   and non-merge PR delivery lead. Count every active descendant against actual
   spare Project capacity and preserve controller scheduling priority; serialize
   or wait when capacity is busy. Do not transfer an already delegated task or
   its repair to the lead.
4. Before any push, satisfy the Project's
   [review contracts](../../run-github-project/references/review-contracts.md).
   Give the single independent reviewer all applicable contracts and record
   coverage at the final clean head; run only missing contracts. Return repairs
   to their owners and renew affected evidence. No external review skill or
   tracker setup is required. Never waive final review.
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

Return the current head, source/plan identities, verification, review coverage,
PR identity, and exact pending/blocking operation. Preserve artifacts on pending
or blocked results. The controller's finish gate owns the board outcome.
