# Implementation-mode procedure

1. Read repository instructions and record the starting branch, exact `HEAD`,
   and worktree status. Stop before delegation if the starting checkout has
   unrelated uncommitted changes. Identify or create a clean integration branch
   from that `HEAD`, and record its base SHA. Do not stash, reset, or absorb
   user work.
2. Resolve the implementation prerequisites in the entrypoint. For each
   behavior-changing item, identify user-approved test seams in the supplied
   spec or tickets. If a seam is missing, obtain agreement before dispatching
   that item. Read the installed `tdd` skill and give its path to the owner;
   stop before behavior work when it is unavailable. Identify the final review
   route before delegation: installed `code-review` with tracker setup, or an
   independent read-only reviewer when missing tracker setup prevents that
   skill from reviewing a supplied local spec. Stop if neither can run.
3. Build and validate the task graph. Require unique stable task IDs, explicit
   dependency lists, declared dependency targets, and an acyclic graph. Reserve
   the case-insensitive task ID `none` for the `Depends on: none` root marker.
   Treat a legacy plan without dependency metadata as a sequential chain in
   listed order. Keep an unsplit request and its checklist in one work item;
   group supplied items only when they cannot validate in separate
   behavior-preserving commits. Record shared-file, interface, and integration
   constraints. Stop on invalid or ambiguous graphs rather than choosing a
   new dependency for the plan owner.
4. Dispatch the ready frontier. Concurrent items must be independent, have
   adequate agent capacity, and each receive an isolated worktree based on the
   same current integrated `HEAD`. This explicit workflow invocation permits
   multiple implementation owners for safe independent items despite a
   one-auxiliary default. Serialize unsafe overlap or unavailable isolation or
   capacity. A dependent is ready only after every prerequisite is integrated
   and its affected checks pass at that integrated head. Do not start it from
   a prerequisite's unintegrated branch.
5. Select an implementation-capable subagent using the entrypoint's runtime
   mapping and the shared [selection and handoff reference](subagent-selection.md).
   Confirm it can edit, validate, commit, and resume the same owner session for
   repairs. Honour configured agents, models, and user selections. If a
   required capability is unavailable, stop rather than implementing in the
   controller; wait for temporarily unavailable capacity. Retain each owner
   handle. Give each owner a decision-complete packet with pointers to the
   exact task, spec, approved test seams where applicable, repository
   instructions, recorded base SHA, owned files, acceptance criteria, and
   focused validation. State that other agents may be editing independently,
   and require preservation of unrelated changes.
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
8. Integrate accepted task commits in dependency order. Before each attempt,
   record the integration branch and exact pre-attempt SHA and verify its
   worktree is clean, including untracked files. If the Git operation conflicts
   before completion, abort that operation and verify the branch is again at
   the recorded SHA and clean. Stop if that state cannot be restored. Give the
   conflict and pre-attempt SHA to the original owner, who replays its work in
   a new isolated task branch from that SHA and returns a task-scoped commit
   with fresh affected evidence.
   Never resolve task-owned source conflicts in the controller.

   After a completed integration, record its exact post-integration `HEAD`.
   Recheck only validation affected by changed inputs at that head, including
   shared interfaces, generated output, and merge or cherry-pick resolutions.
   Inspect the joined diff when cross-file interactions or conflict resolutions
   can change meaning. When checks pass, release newly ready dependents with
   no second lead sign-off. Do not rerun unrelated passing checks or hold a
   dependent for a routine duplicate acceptance ceremony.
9. If a completed merge or cherry-pick fails affected validation, keep the
   failed integrated `HEAD` on the integration branch; do not abort, reset, or
   dispatch dependents from it. If validation changed the worktree, stop until
   those changes are accounted for without discarding user work. Pause further
   integration while the failure is repaired. Trace the failure to the relevant
   original owner or owners. If attribution is unclear, investigate read-only
   first; assign a new bounded implementation owner only when no prior owner
   fits. Give each repair owner the failed head SHA, failing output, and
   affected scope. Have that owner create an isolated branch from
   the failed head and repair forward with a task-scoped commit. Apply step 7
   to the repair commit, verify the integration branch remains at the failed
   SHA and clean, then integrate the repair and rerun affected checks. Stop if
   that failed-head state was lost. Keep unrelated completed owner branches
   intact for later integration. Stop if the failed state cannot be preserved
   or a repair cannot pass; never discard the failed integrated commit.
10. After all items are integrated, run the full user- and repository-required
    suite on the final integrated HEAD. Review the joined diff from the recorded
    starting base with `code-review` when its tracker setup is available. If
    missing tracker setup prevents it from reviewing a supplied local spec,
    give that spec, the repository standards, and joined diff to a fresh
    independent read-only reviewer.
    Return findings to the relevant original owners, accept their task-scoped
    repairs under step 7, and integrate them under steps 8-9. After any repair,
    rerun affected checks, the full required suite, and the joined review at
    the new final head. Do not treat review or test evidence from an earlier
    head as final. Finish only when the integration worktree is clean,
    unrelated starting work is preserved, and the entrypoint's finish gate is
    met.

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
