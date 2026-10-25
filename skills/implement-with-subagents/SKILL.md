---
name: implement-with-subagents
description: Use when implementing supplied tickets or plan tasks with solo or worker-owned implementation selected from the task graph, or when reviewing that orchestration.
compatibility: "Review mode has no external skill dependency. Implementation mode uses Matt Pocock's separately installed `tdd` for behavior changes and one fresh independent read-only reviewer for the final joined branch."
disable-model-invocation: true
---

# Implement with subagents

## Core principle

Choose implementation ownership once from the whole task graph. Keep a single
item or a graph with no parallel point in the lead; when the graph has parallel
work, assign every item to a worker, including sequential heads and tails.
Preserve dependency checks and independent final review in both paths. Keep
repairs with the implementation owner and reuse a bounded pool of worker
checkouts when delegating.

## Select the mode

- Use `review` only to assess supplied orchestration without running it; it
  has no external dependency.
- Use `implement` only to execute supplied tickets or plan tasks. This mode
  does not invoke the separate `/implement` skill.

## Review procedure

1. Inspect only permitted repository and orchestration state. Do not start an
   agent, edit, commit, change branches, perform worktree lifecycle operations,
   or contact a remote service.
2. Assess the whole task graph and its recorded preflight choice. Flag a
   forced worker for a single item or graph with no parallel point; the lead
   implements those runs with self-review and no separate task acceptance.
   A graph with any parallel point assigns every item to workers, including
   sequential heads and tails. For delegated runs, assess task-scoped commits,
   owner self-review, focused validation, and controller acceptance before
   integration. An owner's report alone does not satisfy task acceptance.
   Separate worktrees do not make shared-file edits or work
   depending on unintegrated code independent. Treat supplied readiness,
   independence and capacity as authoritative: in delegated runs, dispatch the
   whole ready frontier concurrently. A prerequisite the state does not show
   missing,
   including test seams, `tdd` and reviewer capability, is an execution-time
   check, not a dispatch hold. Check reuse-first allocation,
   distinct slots for active writers, and existing-checkout access for
   read-only helpers.
3. Release a dependent only after each prerequisite's task commit is
   integrated without conflicts, accepted first when delegated, and its affected
   checks rerun and
   pass at that exact integrated head; a passing task branch is not enough. Do
   not require a second discretionary lead acceptance after an ordinary merge;
   inspect the joined diff when cross-file interactions, changed shared
   interfaces, or merge resolutions can change meaning. Reuse a passing check
   only when inspection shows its inputs and environment unchanged at the
   integrated head. An accepted item is complete, not assignable
   again.
4. Report the next action, evidence, and any acceptance gap. Stop before
   implementation. Check release eligibility, safe retirement, and checkout
   dispositions without mutating them. For an invalid dependency graph or unsafe
   overlap, hold dispatch and return the specific defects to the plan owner; do
   not invent ordering or remove tasks or dependencies. Name any affected check that must be rerun at
   the integrated head, even when another blocker also prevents dispatch.

## Implementation mode

### Prerequisites

Identify the behavior-changing items and their user-approved test seams before
implementation.
Their owners use the separately installed [`tdd`](https://github.com/mattpocock/skills)
skill directly. If a behavior item has no approved seam, obtain agreement
before implementing that item; if `tdd` is unavailable, stop before behavior work.
Documentation and other items without a meaningful test seam use focused
validation instead. Never install a dependency implicitly.

Establish independent read-only review capability before implementation in either
path; do not launch a capability-only reviewer. For final review, use a fresh
agent that makes no writes and does not inherit the implementation
conversation, with a self-contained brief: approved source, plan, repository standards, fixed base,
and exact candidate head. Require findings with evidence and a `ship`, `fix-first`, or `rethink` verdict
against both requirements and standards, with the coverage account under
[Behavioral review and repair](references/behavioral-review.md). Apply that
reference during implementation for related boundary repairs and browser failure
diagnostics; PR feedback remains outside this workflow. No external review skill
or tracker setup is required. If independent review cannot run, report the missing
capability; never waive final review. Add reviewers only for distinct risks or
substantial scope that justify separate assignments.

Before implementation, read
[the implementation-mode procedure](references/implementation-mode.md)
completely. It owns preflight, dispatch, owner packets, task acceptance,
integration, repairs, and final validation. Stop when a dependency, task-scoped
commit, or capability gate cannot be satisfied. In a delegated run, wait for
worker capacity rather than switching to lead implementation.

## Finish gate

In `review`, finish only with the non-mutating assessment, evidence, and any
acceptance gap. In `implement`, finish only when every queued item has a
task-scoped, self-reviewed commit (accepted before integration when delegated),
all affected checks and the full required suite pass at the final integrated head, the
joined review is current, and the integration checkout is clean. Preserve any
unrelated user work from the starting checkout. Account for every run-created
worker checkout as retired with verified readback or retained with a reason,
and preserve task branch refs. Eligible retirement failure or missing cleanup
capability leaves the workflow incomplete even when code verification passed.
Report the item-to-commit mapping, exact integrated head, final validation and
review evidence, checkout dispositions, and any blocker; otherwise stop at the
first incomplete gate. PR and tracker delivery are outside this skill.
