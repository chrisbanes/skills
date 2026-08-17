---
name: implement-with-subagents
description: Use when supplied tickets or plan tasks must be implemented sequentially by separate implementation subagents through an installed implement skill, without controller implementation fallback.
---

# Implement with subagents

Keep orchestration and implementation ownership separate: the controller
schedules, and one implementation subagent owns each independent work item
through completion.

## Procedure

1. Read the repository instructions and inspect the current branch and worktree.
   Preserve unrelated changes. Stop before delegation when a task-scoped commit
   cannot be produced safely from the current state.
2. Resolve and read the installed `implement` skill. Treat it as a required
   dependency. If it is unavailable, stop before making changes and report the
   missing dependency; never reproduce its procedure from memory.
3. Build the work queue from the supplied tickets or plan tasks:
   - preserve explicit boundaries and dependency order;
   - treat an unsplit implementation request as one work item;
   - keep checklist steps inside their containing work item; and
   - group supplied items only when they cannot safely produce separate,
     behavior-preserving commits.
4. Process the queue sequentially on the current branch. Before each item,
   record `HEAD` and require the preceding item to be committed with a clean
   task-owned diff relative to the recorded pre-existing worktree state.
5. Select the portable **Solver** role for the next item and map it to the
   runtime's implementation-capable subagent type. Record the portable role and
   actual runtime selection when the environment exposes it. Spawn one owner.
   Do not implement any part of the item in the controller. If an implementation
   slot is temporarily unavailable, wait for capacity. If subagents cannot be
   started, stop and report the blocker rather than falling back to controller
   implementation.
6. Give the owner a decision-complete packet containing:
   - the exact ticket or plan task and its acceptance criteria;
   - the relevant specification and repository instructions;
   - exclusive ownership of that work item on the current branch;
   - the pre-existing worktree state that must be preserved;
   - an instruction to invoke the installed `implement` skill; and
   - an instruction to return the commit, the evidence required by the installed
     `implement` skill's current finish contract, and any unresolved blocker.
7. Wait for that owner to finish before starting another. Do not split its
   implementation across additional agents. When its result is incomplete,
   dirty, uncommitted, or fails a required check, send the evidence back to the
   same owner and let it repair its item. Stop on a material blocker the owner
   cannot resolve within the supplied contract.
8. Independently accept the item before advancing. Treat the owner's report as
   claims rather than acceptance evidence:
   - verify `HEAD` advanced by at least one task-scoped commit;
   - inspect the complete commit range and diff from the recorded `HEAD` to the
     current `HEAD` for the work item's acceptance criteria and scope;
   - rerun the verification requested by the user and repository for this item;
   - confirm the returned evidence satisfies the installed `implement` skill's
     current finish contract; and
   - verify the task-owned diff is empty relative to the recorded pre-existing
     state.
9. Send every failed acceptance check back to the same owner, then repeat step 8.
   Start the next item only after acceptance passes. After the last item, run any
   final verification required by the user or repository that the item-level
   acceptance passes did not cover. If a later action changes files, return the
   changes to their owning subagent for validation and commit.

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

Finish only when every queued item has a task-scoped, reviewed, verified commit,
the final worktree matches the recorded pre-existing state, and no
owner-reported blocker remains. Report the item-to-commit mapping and the final
validation result. Otherwise finish blocked and name the first incomplete gate.

## RED/GREEN agent scenarios

For each scenario, establish RED by omitting the relevant rule, then restore the
skill and require the GREEN outcome.

1. Two supplied tickets touch different modules and the second depends on the
   first. RED implements in the controller or starts both agents concurrently.
   GREEN sends the first ticket to one Solver owner using `implement`, accepts
   its commit independently, then sends the second ticket to a fresh owner on
   the updated branch.
2. Novel case: the first owner reports success, but controller inspection finds
   a required assertion missing from the committed diff. RED trusts the report
   or starts the next work item. GREEN returns the failed acceptance evidence to
   the same owner, then reinspects the repair and reruns verification.
3. Missing-dependency case: `implement` is not installed. RED copies its
   remembered behavior or lets the controller implement. GREEN stops before
   mutation and reports the required dependency.
4. Over-application counterexample: one ticket contains four TDD checklist
   steps that share a seam. GREEN assigns the whole ticket to one owner and
   does not create four agents.
5. Coupling counterexample: two plan tasks must change the same atomic schema
   and cannot pass validation independently. GREEN groups them into one work
   item for one owner and records why separate commits would be unsafe.
