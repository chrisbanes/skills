---
name: implement-with-subagents
description: Use when implementing or reviewing the orchestration of supplied tickets or plan tasks through separate implementation subagents, including queue atomicity, task-scoped commit acceptance, and repair ownership.
compatibility: "Review mode has no external skill dependency. Implementation mode requires Matt Pocock's separately installed `implement` workflow; its current contract also invokes `tdd` and `code-review`."
disable-model-invocation: true
---

# Implement with subagents

Keep orchestration and implementation ownership separate: the controller
schedules, and one implementation subagent owns each work item through
completion. Validate task IDs and dependencies before dispatch. Run only ready,
independent tasks concurrently, each in an isolated worktree; integrate accepted
commits in dependency order and recheck affected evidence at the integrated
head. Preserve serial execution when safe isolation or capacity is unavailable.
Return failed acceptance evidence to that same owner rather than repairing it
in the controller or reassigning it.

## Check The Prerequisite

Review mode has no external skill dependency. Implementation mode requires the
`implement` skill from [Matt Pocock's skill set](https://github.com/mattpocock/skills),
which is not bundled with this repository. Install it with
`npx skills add mattpocock/skills`, selecting `implement`, `tdd`, and
`code-review` as required by the current upstream contract. Never install it
implicitly.

## Select the mode

- Use `review` only when the user asks to assess supplied orchestration without
  running it.
- Use `implement` when the user asks to execute the supplied tickets or plan
  tasks.

## Review procedure

1. Inspect only the repository and supplied orchestration state that the user
   permits. Do not start a subagent, edit files, create a commit, or contact a
   remote service.
2. Assess queue atomicity, dependency order, implementation ownership,
   task-scoped acceptance, repair ownership, and controller mutation boundaries.
   Treat an already accepted item as complete rather than assigning it again.
3. Report the next orchestration action, or that no action is needed, with the
   evidence and any unresolved acceptance gap. Stop before the implementation
   procedure.

## Implementation procedure

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
   the runtime mapping below.
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
   dependency order. Check each integration for conflicts and inspect the
   resulting integrated diff. Recheck every affected validation whose inputs
   changed during integration, including tests affected by shared files, generated
   output, shared interfaces, or merge resolution. Evidence from a task worktree
   is stale for changed inputs at the integrated head and must be rerun there. A
   dependent becomes ready only after its prerequisite commit is integrated, its
   affected evidence passes at that head, and it is accepted.
   Before each integration attempt, record the controller-owned integration
   branch name and exact `HEAD` SHA, and verify the integration worktree is
   clean, including no untracked files. If the Git operation conflicts before
   it completes, abort that in-progress operation (`git merge --abort` for a
   merge, `git cherry-pick --abort` for a cherry-pick, or the matching abort
   command for another operation). Verify the same integration branch is at
   the recorded pre-attempt SHA and the worktree is clean before returning the
   conflict to the original task owner. If aborting fails or those checks do
   not pass, stop and report the integration checkout as blocked.

   If the integration operation completes but an affected validation fails,
   do not use an abort command. Restore only the controller-owned integration
   branch to the recorded pre-attempt SHA, and only if its recorded pre-attempt
   state was clean, the current branch is still that integration branch, and
   its `HEAD` is still the exact SHA recorded immediately after the completed
   integration and its worktree is currently clean. Run
   `git reset --hard <recorded-pre-attempt-sha>` under those conditions; do not
   reset task-owned branches or other refs/worktrees, and do not remove
   untracked files or unrelated changes. Then verify the branch
   is at the exact recorded pre-attempt SHA and the integration worktree is
   clean before returning the failing check and evidence to the original task
   owner. If any precondition, restoration, or post-reset verification fails,
   stop and report the integration checkout as blocked. The owner repairs in
   its isolated worktree based on the current integrated head, produces a new
   task-scoped commit, and repeats independent acceptance before integration is
   retried. The controller does not resolve task-owned source conflicts or
   implement fixes.
10. After every repair, repeat the independent commit and diff inspection, then
   reassess the evidence under step 8. Reuse only checks whose relevant inputs
   and environment remain unchanged across the inspected descendant diff; repeat
   affected checks after integrating at the new head. An unexplained older
   revision is stale evidence. After the last accepted item, run any final
   user- or repository-required verification on the integrated revision. If a
   later action changes files, return them to their owner for validation and
   commit.

## Runtime mapping

Default implementation agents by runtime; apply the capability checks in step 5.

| Runtime | Implementation owner |
| --- | --- |
| [Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) | `worker` |
| [Claude Code](https://code.claude.com/docs/en/sub-agents) | `general-purpose` |
| [OpenCode](https://opencode.ai/docs/agents) | `general` subagent; `build` is a primary agent |
| [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) | No built-in subagent role. Inspect the installed delegation extension or package and its agent definitions. The upstream [example extension](https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/extensions/subagent) supplies a sample `worker`, not a core role; verify same-session continuation before using it. |
| Other runtimes | An exposed implementation-capable subagent that satisfies step 5 |

## Ownership boundaries

- Keep remote mutations with the controller unless the user explicitly grants
  a different owner and repository instructions permit it.
- Reuse the owning subagent for review repairs and follow-up checks; do not pay a
  second context-transfer cost for the same item.
- Use read-only helpers only when the owner needs genuinely independent
  discovery. They do not edit, commit, or replace the implementation owner.
- Never absorb another item's edits or pre-existing user changes into the
  current owner's commit.

## Finish gate

In `review`, finish only after reporting the non-mutating assessment, its
evidence, and any acceptance gap without starting implementation. In
`implement`, finish only when every queued item has a task-scoped, reviewed,
verified commit, the final worktree matches the recorded pre-existing state,
and no owner-reported blocker remains. Report the item-to-commit mapping and the
final validation result. Otherwise finish blocked and name the first incomplete
gate.
