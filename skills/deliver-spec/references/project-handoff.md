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
   Require hard runtime capacity for the lead plus an independent descendant
   and the chosen review provider's reviewer count. Return a capability blocker
   when that cannot fit; queue temporarily busy but sufficient capacity.
2. Accept the verified execution handoff as satisfying the implementation
   provider's source, plan, and user-approved test-seam prerequisites. Require
   no further human confirmation for an in-scope stage. Independently review
   the plan against source, criteria, repository facts, dependencies, and tests
   unless current evidence covers those exact inputs. Return findings to the
   controller for `to-plan --auto` repair and a verified handoff; automatically
   review repaired inputs. Preserve Project repair budgets and replan rules.
3. Follow `deliver-spec`'s implementation procedure with the supplied tasks and
   materialized source. Keep the persistent ticket agent as integration owner
   and non-merge PR owner. `implement-with-subagents` owns isolated tasks,
   acceptance, integration, and same-owner repairs. Task descendants write
   only their isolated branches. Count all descendants against currently spare
   Project capacity; serialize when one fits and yield when none is free.
   Never replace a task owner with lead implementation.
4. Before any push, satisfy the Project's
   [review contracts](../../run-github-project/references/review-contracts.md).
   Record contracts covered by the provider's joined review at the final clean
   head and run only missing contracts. Return repairs to their owners and
   renew affected evidence. Use the provider's independent local-spec fallback
   only when missing tracker setup prevents its named review; otherwise report
   the capability blocker. Never waive final review.
5. Reuse the supplied branch and verified PR. After review, push and reconcile
   the exact head; create one draft PR only for a nonempty integrated diff.
   Use `Fixes #<ticket>` for `closing-keyword`, or a non-closing issue link for
   `close-after-merge`. Mark ready and verify that state when applicable checks
   and reviews cover the final head. For an empty diff, return `no-change` and
   verification evidence for controller reconciliation.
6. Use `shepherd` for feedback and PR operations, with code repairs through task
   owners. Apply Project verification, repair, monitoring, and CI-parking rules
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
