# Implementation-mode procedure

1. Read repository instructions and record the starting branch, exact `HEAD`,
   and worktree status. Stop before implementation if the starting checkout has
   unrelated uncommitted changes. Identify or create a clean integration branch
   from that `HEAD`, and record its base SHA. Do not stash, reset, or absorb
   user work.
   Before allocating workers, inventory available checkouts through their
   owning runtime and establish the lifecycle record described below. Record
   each exact path and runtime identity, classifying the integration checkout,
   pre-existing or adopted checkouts, and run-created worker slots; never infer
   ownership from a directory name.
2. Resolve the implementation prerequisites in the entrypoint. For each
   behavior-changing item, identify user-approved test seams in the supplied
   spec or tickets. If a seam is missing, obtain agreement before implementing
   that item. Read the installed `tdd` skill and give its path to the owner;
   stop before behavior work when it is unavailable. Identify the final review
   capability before implementation in either path: one fresh independent
   read-only reviewer
   against the approved source and repository standards under the entrypoint's
   review contract. Stop if independent review cannot run.
3. Build and validate the task graph. Require unique stable task IDs, explicit
   dependency lists, declared dependency targets, and an acyclic graph. Reserve
   the case-insensitive task ID `none` for the `Depends on: none` root marker.
   Treat a legacy plan without dependency metadata as a sequential chain in
   listed order. Keep an unsplit request and its checklist in one work item;
   group supplied items only when they cannot validate in separate
   behavior-preserving commits. Record shared-file, interface, and integration
   constraints. Stop on invalid or ambiguous graphs rather than choosing a
   new dependency for the plan owner.
   Distinguish behavioral prerequisites, shared-file mutation conflicts and
   final integration requirements. Plan-proven independent preparation may run
   on the current integrated base with an explicit slice owner, permitted
   paths/resources, focused checks and a stop before shared edits or dependent
   behavior. Preserve native blockers, resource grants and final integrated
   validation; never split an accepted task or relax its prerequisites to
   create concurrency. Route changed ordering through authorized planning.
   A parallel point means two plan-proven independent items can be ready
   together, respecting dependencies and shared-write constraints. With any
   parallel point, workers own every item, including a sequential head or tail.
   Otherwise the graph is solo-eligible. Apply
   [Implementation ownership](subagent-selection.md#implementation-ownership)
   once to the validated graph before assigning any implementation. Record and
   retain the selected route throughout the run.
4. Keep the integration checkout stable and prepare the ready frontier.
   In a solo run, allocate no worker slots: the lead follows step 6, skips the
   separate acceptance in step 7, and commits each item directly on the
   integration branch. Rerun affected checks at that integrated head under
   step 8 before starting a dependent. Skip worker-only dispatch, handoff,
   acceptance and lifecycle operations; keep final review and validation.
   The remaining worker allocation rules in steps 4-5 apply to delegated runs.
   Reconcile prior task acceptance and integration evidence first. Do not
   reassign an accepted task or repeat implementation merely to satisfy worker
   routing; resume integration, review, or delivery from the verified current
   state. Resolve worker capacity before dispatching new implementation or a
   required repair. Wait until step 5 confirms capability before dispatching.
   Assign every item to a worker. On a model-routed serial run, use the same
   owner for each item, starting it from the then-current integrated head.
   Reuse a suitable worker checkout for sequential heads and tails. Dispatch
   all plan-proven independent ready items with disjoint write sets by
   default. Each concurrent writer needs a distinct
   isolated checkout based on the same current integrated `HEAD`; reuse a
   suitable idle slot before creating another. Create only when concurrency or
   isolation requires it and runtime and repository rules permit. Count every
   active descendant within actual caller, runtime, repository, and (when
   applicable) Project capacity. Preserve explicit multi-worker authorization
   constraints and caller-supplied scheduling priority, including priority
   across ready Project tickets before adding extra within-ticket workers.
   Serialize shared-file edits, dependencies, unavailable safe isolation, or
   insufficient capacity. Wait for temporary capacity limits; do not fall back
   to lead implementation when a worker is required. A dependent is ready only
   when every prerequisite is integrated and its affected checks pass at that
   integrated head, including planned boundary evidence under
   [to-plan's boundary-validation rule](boundary-validation.md).
   Do not start it from a prerequisite's unintegrated branch.
   Give read-only helpers access to an existing checkout without allocating a
   worker slot, and never switch a checkout used by an active owner or process.
5. Select an implementation-capable subagent using the runtime requirements below
   and the shared [selection and handoff reference](subagent-selection.md).
   Verify the preflight settings before dispatch. Classify individual tasks
   under the policy for parallel work and use the preflight's whole-chain
   settings for serial work. Require workers to return newly discovered
   architectural or correctness decisions to the lead while retaining
   ownership of their tasks and repairs.
   Confirm it can edit, validate, commit, and resume the same owner session for
   repairs. Honour configured agents, models, and user selections. If a
   required capability is unavailable, stop rather than implementing in the
   lead; wait for temporarily unavailable capacity. Use the caller's supported
   wait or idle behavior for the coordinator while workers run, and verify
   capacity again after resuming; do not assume a blocking wait releases the
   caller's slot. Retain each owner handle. Give each owner a decision-complete
   implementation brief under the shared reference, pointing to the exact task,
   spec, approved test seams where applicable, and repository instructions.
   State that other agents may be editing independently, and require preservation of unrelated
   changes. Dispatch the ready frontier only after this capability check passes.
6. Have each owner (the lead in solo runs) implement only its item. For behavior
   changes, invoke `tdd`
   directly at the approved test seams and follow its red-green loop. For
   documentation or configuration without a meaningful test seam, use focused
   validation and record why TDD does not apply. Require focused checks, owner
   self-review against the task and repository standards, a task-scoped commit,
   and record each command's exit code, tested SHA, output tail and complete-log
   path, plus relevant input and environment identity. Delegated owners return
   that evidence in the [selection and handoff reference](subagent-selection.md)
   report format; solo work needs no separate acceptance receipt. Run a
   broader check here only when the user or repository requires it. Do not
   invoke the separate `/implement` skill.
7. For delegated runs, perform the lead's one task acceptance before integration.
   Independently
   inspect the complete commit range and diff from the recorded base for task
   scope and criteria. Verify the owner's branch advanced by a task-scoped
   commit and its worktree is clean. Inspect exit status, tested revision, and
   relevant inputs and environment, and the complete log when acceptance needs
   it; a tail alone is not complete output. Reuse passing evidence
   only when the environment remains unchanged and the tested revision is the
   branch `HEAD`, or an inspected descendant changed no relevant inputs. Repeat
   an affected check when evidence is missing, failed, stale, or explicitly
   required fresh. An owner's assertion is not acceptance. Return incomplete
   work to the same owner for repair and repeat this check on its new commit.
8. In delegated runs, while workers run, advance useful independent coordination
   work that does
   not touch their owned files or invalidate their evidence. Integrate accepted
   task commits in dependency order. Before each attempt,
   record the integration branch and exact pre-attempt SHA and verify its
   worktree is clean, including untracked files. If the Git operation conflicts
   before completion, abort that operation and verify the branch is again at
   the recorded SHA and clean. Stop if that state cannot be restored. Give the
   conflict and pre-attempt SHA to the original owner, who replays its work in
   a new isolated task branch from that SHA using an available worker slot and
   returns a task-scoped commit with fresh affected evidence. Never resolve
   task-owned source conflicts in the controller.

   In either path, after a completed integration (a direct task commit in solo
   runs), record its exact post-integration `HEAD`.
   Recheck only validation affected by changed inputs at that head, including
   shared interfaces, generated output, and merge or cherry-pick resolutions.
   Inspect the joined diff when cross-file interactions or conflict resolutions
   can change meaning. Release a worker checkout only under the lifecycle gate
   below. When checks pass, release newly ready dependents with no second lead
   sign-off. Do not rerun unrelated passing checks or hold a dependent for a
   routine duplicate acceptance ceremony.
9. If a completed merge or cherry-pick, or a solo task commit, fails affected
   validation, keep the
   failed integrated `HEAD` on the integration branch; do not abort, reset, or
   dispatch dependents from it. If validation changed the worktree, stop until
   those changes are accounted for without discarding user work. Pause further
   integration while the failure is repaired. In a solo run, the lead repairs
   forward from that failed head, self-reviews and commits the repair, then
   reruns affected checks before dependents; skip worker handoff and acceptance.
   In a delegated run, trace the failure to the relevant
   original owner or owners. If attribution is unclear, investigate read-only
   first; assign a new bounded implementation owner only when no prior owner
   fits. Retain the applicable owner handle and give the repair owner the failed
   head SHA, failing output, affected scope, and a checkout under the
   [failed-check repair rules](checkout-lifecycle.md#repair-after-failed-integrated-checks).
   Have that owner repair forward on the fresh branch and return a task-scoped
   commit. Apply step 7 to the repair commit, verify the integration branch
   remains at the failed SHA and clean, then integrate the repair and rerun
   affected checks. Stop if that failed-head state was lost. Keep unrelated
   completed owner branches intact for later integration. Stop if the failed
   state cannot be preserved or a repair cannot pass; never discard the failed
   integrated commit.
10. After all items are integrated, run the full user- and repository-required
    suite on the final integrated HEAD. If it fails, preserve that exact
    integrated head, pause further integration, and repair forward under step 9.
    Give the approved source, repository standards, and joined diff from the
    recorded starting base to one fresh independent read-only reviewer under
    the entrypoint's review contract.
    Return findings to the relevant original owners (the lead when solo). For
    delegated repairs, apply step 7 acceptance; integrate under steps 8-9. After
    any repair,
    rerun affected checks and renew review of the changed range and its
    interactions. Apply [Behavioral review and repair](behavioral-review.md) for
    affected-scope renewal and broadening conditions; preserve the required
    final integrated suite above. Verify
    that combined evidence covers the new final head. Apply the checkout lifecycle
    rules below at completion,
    blockers, and interruption. Finish only when the integration worktree is
    clean, unrelated starting work is preserved, checkout accounting is
    complete, and the entrypoint's finish gate is met.

## Runtime requirements

Implementation-agent requirements apply only to delegated runs; both paths
require an independent final reviewer. Choose agents by capability, not runtime
role name:

- Implementation owner: can edit, run validation and commit in its assigned
  checkout, and can be resumed in the same session for repairs.
- Independent reviewer: starts without the implementation conversation and
  makes no writes. When the runtime cannot enforce read-only access, verify
  afterwards that the reviewer's checkout is unchanged.

Runtime caveats:

- [Claude Code](https://code.claude.com/docs/en/sub-agents): `Explore` and
  `Plan` are one-shot and cannot own an item. The lead creates each run-owned
  worker checkout at the integrated SHA under the checkout lifecycle's
  [create rule](checkout-lifecycle.md#create) and passes the absolute path in
  the brief. Never use
  `Agent(isolation: "worktree")`; it bases on the default branch, not the
  integrated `HEAD`.
- [OpenCode](https://opencode.ai/docs/agents): `build` is a primary agent, not
  a delegable subagent.
- [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent):
  no built-in subagent; inspect its delegation extension and agent
  definitions. A bare or non-resumable Pi cannot own an item: stop and report
  it.

## Worker checkout lifecycle

Apply these rules when worker checkouts exist; a solo run creates none and
retains its integration checkout. Follow the
[checkout lifecycle](checkout-lifecycle.md) for worker checkouts.


## Ownership boundaries

- Keep remote mutations with the controller unless the user explicitly grants
  another owner and repository instructions permit it. PR and tracker delivery
  are outside this workflow.
- Reuse each item owner for its repairs and follow-up checks. Do not split an
  item across agents or transfer it merely to clear a review finding.
- Read-only helpers may discover or review independently. They do not edit,
  commit, or replace an implementation owner.
- Never absorb another item's edits or pre-existing user changes into an
  owner's commit.
