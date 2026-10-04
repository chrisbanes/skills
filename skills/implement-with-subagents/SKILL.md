---
name: implement-with-subagents
description: Use when implementing supplied tickets or plan tasks through worker-owned bounded implementation and lead integration, or when reviewing that orchestration.
compatibility: "Review mode has no external skill dependency. Implementation mode uses Matt Pocock's separately installed `tdd` for behavior changes and one fresh independent read-only reviewer for the final joined branch."
disable-model-invocation: true
---

# Implement with subagents

Use this workflow whenever a delivery lead coordinates settled implementation
tasks, including one task and sequential work. Assign one worker per supplied
work item; do not split a single task into artificial pieces. Reuse a bounded
pool of worker checkouts. The lead validates the task graph, dispatches the
independent ready frontier with disjoint write sets by default, accepts each
task once before integration, and integrates accepted commits in dependency
order. After an ordinary integration, rerun affected checks and release
dependents without a second lead sign-off. Retire eligible surplus checkouts,
preserve task refs, and account for checkout dispositions at completion or
interruption. Keep the lead out of task-owned code and return implementation
repairs to the original worker.

## Select the mode

- Use `review` only to assess supplied orchestration without running it.
- Use `implement` only to execute supplied tickets or plan tasks. This mode
  does not invoke the separate `/implement` skill.

## Check implementation prerequisites

Review mode has no external dependency. For implementation, identify the
behavior-changing items and their user-approved test seams before delegation.
Their owners use the separately installed [`tdd`](https://github.com/mattpocock/skills)
skill directly. If a behavior item has no approved seam, obtain agreement
before dispatch; if `tdd` is unavailable, stop before dispatching that item.
Documentation and other items without a meaningful test seam use focused
validation instead. Never install a dependency implicitly.

Resolve one independent read-only reviewer before delegation. Use a fresh
investigator in review mode (or an equivalent runtime role) with a
self-contained brief: approved source, plan, repository standards, fixed base,
and exact candidate head. Do not inherit the implementation conversation.
Require findings with evidence and a `ship`, `fix-first`, or `rethink` verdict
against both requirements and standards, with the coverage account under
[Behavioral review and repair](references/behavioral-review.md). Apply that
reference during implementation for related boundary repairs and browser failure
diagnostics; PR feedback remains outside this workflow. No external review skill
or tracker setup is required. If independent review cannot run, report the missing
capability; never waive final review. Add reviewers only for distinct risks or
substantial scope that justify separate assignments.

## Review procedure

1. Inspect only permitted repository and orchestration state. Do not start an
   agent, edit, commit, change branches, perform worktree lifecycle operations,
   or contact a remote service.
2. Assess the task graph, safe concurrency, implementation ownership,
   task-scoped commits, owner self-review, focused validation, and controller
   acceptance before integration. An owner's report alone does not satisfy
   task acceptance. Separate worktrees do not make shared-file edits or work
   depending on unintegrated code independent. Check reuse-first allocation,
   distinct slots for active writers, and existing-checkout access for
   read-only helpers.
3. Check that each prerequisite is integrated and its affected validation
   passes at that exact head before releasing a dependent. A passing task
   branch is insufficient when integration changes relevant inputs. Do not
   require a second discretionary lead acceptance after an ordinary merge;
   inspect the joined diff when cross-file interactions, changed shared
   interfaces, or merge resolutions can change meaning. Reuse passing checks
   only when their inputs and
   environment remain unchanged. An accepted item is complete, not assignable
   again.
4. Report the next action, evidence, and any acceptance gap. Stop before
   implementation. Check release eligibility, safe retirement, and checkout
   dispositions without mutating them. For an invalid dependency graph, hold
   dispatch and return the specific defects to the plan owner; do not invent or
   remove tasks or dependencies. Name any affected check that must be rerun at
   the integrated head, even when another blocker also prevents dispatch.

## Implementation mode

Before delegation, read
[the implementation-mode procedure](references/implementation-mode.md)
completely. It owns preflight, dispatch, owner packets, task acceptance,
integration, repairs, and final validation. Stop when a dependency, task-scoped
commit, or capability gate cannot be satisfied; never implement an item in the
controller.

The implementation-mode procedure includes the runtime mapping and owns the
capability checks, dispatch, and acceptance workflow.

## Finish gate

In `review`, finish only with the non-mutating assessment, evidence, and any
acceptance gap. In `implement`, finish only when every queued item has a
task-scoped, self-reviewed commit accepted before integration, all affected
checks and the full required suite pass at the final integrated head, the
joined review is current, and the integration checkout is clean. Preserve any
unrelated user work from the starting checkout. Account for every run-created
worker checkout as retired with verified readback or retained with a reason,
and preserve task branch refs. Eligible retirement failure or missing cleanup
capability leaves the workflow incomplete even when code verification passed.
Report the item-to-commit mapping, exact integrated head, final validation and
review evidence, checkout dispositions, and any blocker; otherwise stop at the
first incomplete gate. PR and tracker delivery are outside this skill.
