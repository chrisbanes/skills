---
name: implement-with-subagents
description: Use when implementing or reviewing the orchestration of supplied tickets or plan tasks through separate implementation subagents, including queue atomicity, task-scoped commit acceptance, and repair ownership, with an installed implement skill.
disable-model-invocation: true
---

# Implement with subagents

Keep orchestration and implementation ownership separate: the controller
schedules, and one implementation subagent owns each independent work item
through completion. Keep changes that cannot validate apart in one item, accept
its task-scoped commit before advancing, and return failed acceptance evidence
to that same owner rather than repairing it in the controller or reassigning it.

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
   dependency. If it is unavailable, stop before making changes and report the
   missing dependency; never reproduce its procedure from memory.
3. Build a dependency-ordered queue. Keep an unsplit request and its checklist
   in one work item; group supplied items only when they cannot validate in
   separate behavior-preserving commits.
4. Process one item at a time. Record `HEAD` and the pre-existing worktree state
   before each item; accept the preceding item before starting the next.
5. Select the portable **Solver** role and map it to the
   runtime's implementation-capable subagent type. Record the portable role and
   actual runtime selection when the environment exposes it. Spawn one owner.
   Do not implement any part of the item in the controller. If an implementation
   slot is temporarily unavailable, wait for capacity. If subagents cannot be
   started, stop and report the blocker rather than falling back to controller
   implementation.
6. Give that owner a decision-complete packet containing:
   - the exact ticket or plan task and its acceptance criteria;
   - the relevant specification and repository instructions;
   - exclusive ownership of that work item on the current branch;
   - the pre-existing worktree state that must be preserved;
   - an instruction to invoke the installed `implement` skill; and
   - an instruction to return the commit, the evidence required by the installed
     `implement` skill's current finish contract, and any unresolved blocker.
7. Wait for that owner before starting another. Do not split its implementation
   across agents. If the result is incomplete, dirty, uncommitted, or fails a
   required check, return the evidence to the same owner. Stop on a material
   blocker it cannot resolve within the supplied contract.
8. Independently accept the item before advancing; an owner's report is not
   acceptance evidence. Verify:
   - verify `HEAD` advanced by at least one task-scoped commit;
   - inspect the complete commit range and diff from the recorded `HEAD` to the
     current `HEAD` for the work item's acceptance criteria and scope;
   - rerun the verification requested by the user and repository for this item;
   - confirm the returned evidence satisfies the installed `implement` skill's
     current finish contract; and
   - verify the task-owned diff is empty relative to the recorded pre-existing
     state.
9. Repeat step 8 after every repair. After the last accepted item, run any final
   user- or repository-required verification. If a later action changes files,
   return them to their owner for validation and commit.

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
