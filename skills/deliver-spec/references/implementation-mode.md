# Implementation-mode procedure

1. Read repository instructions and record the starting branch, exact `HEAD`,
   and worktree status. Stop before delegation if the starting checkout has
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
   spec or tickets. If a seam is missing, obtain agreement before dispatching
   that item. Read the installed `tdd` skill and give its path to the owner;
   stop before behavior work when it is unavailable. Identify the final review
   capability before delegation: one fresh independent read-only reviewer
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
4. Keep the integration checkout stable and prepare the ready frontier.
   Reconcile prior task acceptance and integration evidence first. Do not
   reassign an accepted task or repeat implementation merely to satisfy worker
   routing; resume integration, review, or delivery from the verified current
   state. Resolve worker capacity before dispatching new implementation or a
   required repair. Wait until step 5 confirms capability before dispatching.
   Assign even one supplied item to one worker; reuse a suitable worker checkout
   for sequential items rather than keeping implementation in the lead. For
   multiple items, actively dispatch all plan-proven independent ready items
   with disjoint write sets by default. Each concurrent writer needs a distinct
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
   integrated head. Do not start it from a prerequisite's unintegrated branch.
   Give read-only helpers access to an existing checkout without allocating a
   worker slot, and never switch a checkout used by an active owner or process.
5. Select an implementation-capable subagent using the runtime mapping below
   and the shared [selection and handoff reference](subagent-selection.md).
   Confirm it can edit, validate, commit, and resume the same owner session for
   repairs. Honour configured agents, models, and user selections. If a
   required capability is unavailable, stop rather than implementing in the
   lead; wait for temporarily unavailable capacity. Use the caller's supported
   wait or idle behavior for the coordinator while workers run, and verify
   capacity again after resuming; do not assume a blocking wait releases the
   caller's slot. Retain each owner handle. Give each owner a decision-complete
   packet with pointers to the exact task, spec, approved test seams where
   applicable, repository instructions, recorded base SHA, exact checkout path,
   task branch, owned files, acceptance criteria, and focused validation.
   State that other agents may be editing independently, and require preservation of unrelated
   changes. Dispatch the ready frontier only after this capability check passes.
6. Have each owner implement only its item. For behavior changes, invoke `tdd`
   directly at the approved test seams and follow its red-green loop. For
   documentation or configuration without a meaningful test seam, use focused
   validation and record why TDD does not apply. Require focused checks, owner
   self-review against the task and repository standards, a task-scoped commit,
   and a report containing the commit SHA, complete command results, tested
   revision, relevant input and environment identity, and blockers. Run a
   broader check here only when the user or repository requires it. Do not
   invoke the separate `/implement` skill.
7. Perform the lead's one task acceptance before integration. Independently
   inspect the complete commit range and diff from the recorded base for task
   scope and criteria. Verify the owner's branch advanced by a task-scoped
   commit and its worktree is clean. Inspect complete check output, exit status,
   tested revision, and relevant inputs and environment. Reuse passing evidence
   only when the environment remains unchanged and the tested revision is the
   branch `HEAD`, or an inspected descendant changed no relevant inputs. Repeat
   an affected check when evidence is missing, failed, stale, or explicitly
   required fresh. An owner's assertion is not acceptance. Return incomplete
   work to the same owner for repair and repeat this check on its new commit.
8. While workers run, advance useful independent coordination work that does
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

   After a completed integration, record its exact post-integration `HEAD`.
   Recheck only validation affected by changed inputs at that head, including
   shared interfaces, generated output, and merge or cherry-pick resolutions.
   Inspect the joined diff when cross-file interactions or conflict resolutions
   can change meaning. Release a worker checkout only under the lifecycle gate
   below. When checks pass, release newly ready dependents with no second lead
   sign-off. Do not rerun unrelated passing checks or hold a dependent for a
   routine duplicate acceptance ceremony.
9. If a completed merge or cherry-pick fails affected validation, keep the
   failed integrated `HEAD` on the integration branch; do not abort, reset, or
   dispatch dependents from it. If validation changed the worktree, stop until
   those changes are accounted for without discarding user work. Pause further
   integration while the failure is repaired. Trace the failure to the relevant
   original owner or owners. If attribution is unclear, investigate read-only
   first; assign a new bounded implementation owner only when no prior owner
   fits. Retain the applicable owner handle and give the repair owner the failed
   head SHA, failing output, affected scope, and an idle suitable worker
   checkout under the lifecycle rules below. Have that owner create a fresh
   unique branch from the failed head and repair forward with a task-scoped
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
    Return findings to the relevant original owners, accept their task-scoped
    repairs under step 7, and integrate them under steps 8-9. After any repair,
    rerun affected checks and renew review of the changed range and its
    interactions. Repeat the full suite or full review when required or when
    prior evidence is invalid or the affected scope cannot be bounded. Verify
    that combined evidence covers the new final head. Apply the checkout lifecycle
    rules below at completion,
    blockers, and interruption. Finish only when the integration worktree is
    clean, unrelated starting work is preserved, checkout accounting is
    complete, and the entrypoint's finish gate is met.

## Runtime mapping

Select an implementation-capable owner and apply the capability checks above:

| Runtime | Implementation owner |
| --- | --- |
| [Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) | `worker` |
| [Claude Code](https://code.claude.com/docs/en/sub-agents) | `general-purpose` |
| [OpenCode](https://opencode.ai/docs/agents) | `general` subagent; `build` is primary |
| [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) | No built-in role; inspect its delegation extension and agent definitions. A bare or non-resumable Pi cannot own an item: stop and report it. |
| Other runtimes | An exposed implementation-capable subagent that passes the checks |

## Worker checkout lifecycle

Maintain this record in the workflow's existing reporting context, not a new
committed ledger. Record each checkout's provenance and runtime identity, exact
path, owner, task branch and base, accepted commits, integration and check
evidence, active use, and disposition. Distinguish the stable integration
checkout, run-created worker slots, and pre-existing or adopted checkouts.
Never infer ownership from a directory name. Pre-existing, adopted, pinned,
and shared checkouts are not automatically retired.

Release a slot only after its accepted task commit and original branch ref are
recorded and preserved, integration succeeds, affected checks pass at the exact
integrated SHA, its owner and processes stop using it, it is clean, and needed
untracked or ignored artifacts are accounted for. Otherwise retain it. Before
reuse, create a fresh unique task branch from the recorded current integrated
SHA, verify the branch and SHA, and hand off the exact path, branch, base, and
instructions. Never reset or delete an old branch to reuse its checkout.

Retire released surplus slots when remaining work no longer needs their
capacity, retaining one for sequential work and only justified capacity for
future concurrent writers. At completion, retire all eligible run-created
worker slots. On a blocker or interruption, retire eligible surplus when
execution remains available; retain active, unfinished, failing, dirty, or
otherwise unsafe checkouts. If interruption prevents cleanup, report it at the
next opportunity. Preserve the integration checkout, user work, and required
ignored artifacts. Do not force cleanup to meet a capacity cap.

Use the runtime's native operation for managed worktrees and verify retirement
through provider inventory. For plain Git worktrees owned by the run, remove
only the exact eligible path without force and verify it is absent from
`git worktree list --porcelain`. Never shell-delete a managed checkout, force
removal, prune globally, or delete branch refs. If ownership or eligibility is
uncertain, retain and report the checkout.

Account for every run-created checkout as retired with verified readback or
retained with a reason. Record the integration checkout as retained and explain
retained exclusions. If eligible retirement fails or cleanup capability is
missing, report code verification separately and mark the workflow
cleanup-incomplete; do not claim overall completion. Include the exact path,
error, and provider readback. Do not retry blindly.


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
