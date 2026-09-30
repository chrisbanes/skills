---
name: implement-with-subagents
description: Use when implementing or reviewing the orchestration of supplied tickets or plan tasks through separate implementation subagents, including dependency order, task-scoped acceptance, and repair ownership.
compatibility: "Review mode has no external skill dependency. Implementation mode uses Matt Pocock's separately installed `tdd` for behavior changes and `code-review` for the final joined branch when its tracker setup is available."
disable-model-invocation: true
---

# Implement with subagents

Keep implementation ownership with one subagent per work item and reuse a
bounded pool of worker checkouts. The controller validates the task graph,
dispatches independent ready work in distinct checkouts, accepts each task once
before integration, and integrates accepted commits in dependency order. After
an ordinary integration, rerun affected checks and release dependents without
a second lead sign-off. Retire eligible surplus checkouts, preserve task refs,
and account for checkout dispositions at completion or interruption. Keep the
controller out of task-owned code and return repairs to the relevant owner.

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

Resolve the final review capability before delegation. Use the separately
installed `code-review` skill on the joined branch when its issue-tracker setup
is available. Its two reviewers are a justified exception to a repository's
one-auxiliary default. If missing tracker setup prevents that skill from
running against a supplied local spec, use a fresh independent read-only
reviewer against that spec and the repository standards. If neither route is
available, stop and report the
missing capability. Do not require issue-tracker setup solely to review a
local-spec run.

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

## Runtime mapping

Select an implementation-capable owner and apply the implementation procedure's
capability checks:

| Runtime | Implementation owner |
| --- | --- |
| [Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) | `worker` |
| [Claude Code](https://code.claude.com/docs/en/sub-agents) | `general-purpose` |
| [OpenCode](https://opencode.ai/docs/agents) | `general` subagent; `build` is primary |
| [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) | No built-in role; inspect its delegation extension and agent definitions. A bare or non-resumable Pi cannot own an item: stop and report it. |
| Other runtimes | An exposed implementation-capable subagent that passes the checks |

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
