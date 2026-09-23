# Implementation-mode procedure

1. Read the repository instructions and inspect the current branch and worktree.
   Preserve unrelated changes. Stop before delegation when a task-scoped commit
   cannot be produced safely from the current state.
2. Resolve and read the installed `implement` skill. Treat it as a required
   dependency. If it is unavailable, stop before making changes. Report that it
   comes from `mattpocock/skills`, provide
   `npx skills add mattpocock/skills`, and state that the user must select
   `implement`, `tdd`, and `code-review`. Never install them implicitly or
   reproduce the procedure from memory.
3. Build and validate the task graph before dispatch. Require unique stable task
   IDs, explicit dependency lists, declared dependency targets, and an acyclic
   graph. Reserve the case-insensitive task ID `none` for the `Depends on: none`
   root marker. Treat a legacy plan without dependency metadata as a sequential
   chain in listed order. Keep an unsplit request and its checklist in one work item;
   group supplied items only when they cannot validate in separate
   behavior-preserving commits. Record shared-file, interface, and integration
   constraints; tasks with unsafe write overlap are not independent even when
   the graph otherwise makes them ready. Stop on invalid or ambiguous graphs.
4. Dispatch only currently ready tasks whose dependencies have been integrated
   and accepted. Concurrent tasks must be independent, have adequate agent
   capacity, and each receive an isolated worktree based on the same current
   integrated head. If isolation, capacity, or safe independence is unavailable,
   dispatch one task at a time. Dependents cannot start from a prerequisite's
   unintegrated branch.
5. Select an implementation-capable subagent for each dispatched task using
   the runtime mapping in the entrypoint.
   Verify that it can edit, run validation, create the task-scoped commit, and
   continue the same owner session for repairs. Honour applicable user and
   repository agent selections and configured models. If the required capability
   is unavailable, stop and report the missing capability; do not install an
   extension or fall back to controller implementation. If capacity is only
   temporarily unavailable, wait. Retain each owner session handle.
   Give each owner explicit ownership of the work item, its isolated worktree, and
   affected files, tell it that other agents may be editing the codebase, and
   require it to preserve and accommodate unrelated changes. Do not implement
   any part of the item in the controller.
6. Give each owner a decision-complete packet containing:
   - the exact ticket or plan task and its acceptance criteria;
   - the relevant specification and repository instructions;
   - exclusive ownership of that work item in its isolated worktree;
   - the pre-existing worktree state that must be preserved;
   - an instruction to invoke the installed `implement` skill; and
   - an instruction to return the commit, the evidence required by the installed
     `implement` skill's current finish contract, and any unresolved blocker.
7. Wait for dispatched owners. Do not split an item's implementation across
   agents. If a result is incomplete, dirty, uncommitted, or fails a required
   check, return the evidence to that same owner. Stop on a material blocker it
   cannot resolve within the supplied contract.
8. Independently accept each completed task; an owner's report is not acceptance
   evidence. Verify:
   - the owner's isolated branch advanced by at least one task-scoped commit;
   - inspect the complete commit range and diff from its recorded base to the
     task commit for the work item's acceptance criteria and scope;
   - inspect the returned command, complete result, tested revision, and relevant
     input and environment identity;
   - reuse a requested check only when its complete evidence shows success,
     the relevant environment remains unchanged, and neither the user nor
     repository requires a fresh independent run. Also require either the tested
     revision to equal that owner's branch `HEAD`, or that branch `HEAD` to be a
     descendant of the tested revision whose independently inspected diff
     leaves the check's relevant inputs unchanged;
   - repeat each affected check when its evidence is missing, failed, tied to an
     unexplained older revision, affected by a changed relevant input, or subject
     to an explicit freshness or independent-run requirement;
   - confirm the returned evidence satisfies the installed `implement` skill's
     current finish contract; and
   - verify the task-owned diff is empty relative to the recorded pre-existing
     state.
9. Integrate accepted commits into the controller's integration branch in
   dependency order and check each integration for conflicts. After an
   integration operation completes, record the integration branch and its exact
   `HEAD` SHA as that attempt's post-integration SHA before inspecting the
   integrated diff or running affected checks. Recheck every affected
   validation whose inputs changed during integration, including tests affected
   by shared files, generated output, shared interfaces, or merge resolution.
   Evidence from a task worktree is stale for changed inputs at the integrated
   head and must be rerun there. A dependent becomes ready only after its
   prerequisite commit is integrated, its affected evidence passes at that
   head, and it is accepted.
   Before each integration attempt, record the controller-owned integration
   branch name and exact `HEAD` SHA, and verify the integration worktree is
   clean, including no untracked files. If the Git operation conflicts before
   it completes, abort that in-progress operation (`git merge --abort` for a
   merge, `git cherry-pick --abort` for a cherry-pick, or the matching abort
   command for another operation). Verify the same integration branch is at
   the recorded pre-attempt SHA and the worktree is clean before returning the
   conflict to the original task owner. Give that same owner the exact
   pre-attempt SHA and conflict evidence. Have them create a new task-owned
   repair branch and isolated worktree from that integrated SHA (for example,
   `git worktree add -b <repair-branch> <repair-path>
   <recorded-pre-attempt-sha>`), then replay their task-scoped commit(s) there
   in order (for example, `git cherry-pick <task-commit-sha>`). The owner
   resolves any replay conflict in that isolated worktree, completes the
   replay, and returns a new task-scoped commit with fresh affected evidence
   for independent acceptance. Do not retry the stale task branch unchanged.
   If aborting fails or the controller checks do not pass, stop and report the
   integration checkout as blocked.

   If the integration operation completes but an affected validation fails,
   do not use an abort command. Preserve the failed integrated tree first: use
   a fresh controller-owned recovery branch named for the task and attempt,
   pointing to the recorded post-integration SHA. Require that this branch name
   does not already exist; create it without force with
   `git branch <recovery-branch> <recorded-post-integration-sha>` and verify
   `git rev-parse <recovery-branch>` resolves to the exact post-integration
   SHA. If the tree cannot be preserved and verified, stop and report the
   integration checkout as blocked without resetting it.

   Restore only the controller-owned integration branch to the recorded
   pre-attempt SHA, and only if its recorded pre-attempt state was clean, the
   current branch is still that integration branch, its `HEAD` is still the
   exact post-integration SHA, and its worktree is currently clean. Run
   `git reset --hard <recorded-pre-attempt-sha>` under those conditions; do not
   reset task-owned branches or other refs/worktrees, and do not remove
   untracked files or unrelated changes. Then verify the integration branch is
   at the exact recorded pre-attempt SHA and clean, and the recovery branch
   still resolves to the exact post-integration SHA, before handing off the
   failing check. Give the original task owner that recovery branch and SHA;
   have the owner create a new task-owned repair branch and isolated worktree
   from that recovery ref (for example, `git worktree add -b <repair-branch>
   <repair-path> <recovery-branch>`), then make the task-scoped repair there.
   After independent acceptance, inspect the complete repaired branch range
   from the recorded pre-attempt SHA and integrate the entire repaired task
   branch in dependency order, including both the original task change from the
   failed integration and its repair commits. Do not cherry-pick only the
   repair commit. Rerun affected evidence on the reintegrated tree. If any
   precondition, restoration, preservation, or verification fails, stop and
   report the integration checkout as blocked. The controller does not resolve
   task-owned source conflicts or implement fixes.
10. After every repair, repeat the independent commit and diff inspection, then
   reassess the evidence under step 8. Reuse only checks whose relevant inputs
   and environment remain unchanged across the inspected descendant diff; repeat
   affected checks after integrating at the new head. An unexplained older
   revision is stale evidence. After the last accepted item, run any final
   user- or repository-required verification on the integrated revision. If a
   later action changes files, return them to their owner for validation and
   commit.


## Ownership boundaries

- Keep remote mutations with the controller unless the user explicitly grants a
  different owner and repository instructions permit it.
- Reuse the owner for review repairs and follow-up checks; do not transfer the
  same item to a second context.
- Read-only helpers may provide genuinely independent discovery only. They do
  not edit, commit, or replace the owner.
- Never absorb another item's edits or pre-existing user changes into an owner's
  commit.
