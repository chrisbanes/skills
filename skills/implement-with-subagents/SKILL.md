---
name: implement-with-subagents
description: Use when implementing or reviewing the orchestration of supplied tickets or plan tasks through separate implementation subagents, including queue atomicity, task-scoped commit acceptance, and repair ownership.
compatibility: "Review mode has no external skill dependency. Implementation mode requires Matt Pocock's separately installed `implement` workflow; its current contract also invokes `tdd` and `code-review`."
disable-model-invocation: true
---

# Implement with subagents

Keep orchestration and implementation ownership separate: the controller
schedules, and one implementation subagent owns each work item through
completion. Validate task dependencies before dispatch. Run only ready,
independent tasks concurrently in isolated worktrees; integrate accepted commits
in dependency order and recheck affected evidence at the integrated head. Use
serial execution when safe isolation or capacity is unavailable. Return failed
acceptance evidence to the same owner, never repair it in the controller.

## Check the prerequisite

Review mode has no external dependency. Implementation mode requires the
`implement` skill from [Matt Pocock's skill set](https://github.com/mattpocock/skills).
It is not bundled here. Never install it implicitly; report
`npx skills add mattpocock/skills` and require the user to select `implement`,
`tdd`, and `code-review` when it is absent.

## Select the mode

- Use `review` only to assess supplied orchestration without running it.
- Use `implement` only to execute supplied tickets or plan tasks.

## Review procedure

1. Inspect only permitted repository and orchestration state. Do not start an
   agent, edit, commit, or contact a remote service.
2. Assess queue atomicity, dependency order, implementation ownership,
   task-scoped acceptance, repair ownership, and controller mutation boundaries.
   Acceptance requires a task-scoped commit, independent inspection of its full
   diff, and requested task-level validation evidence before advancing. Before
   dispatching a dependent, require each prerequisite to be integrated; inspect
   the joined diff for conflicts and rerun affected validation at that
   integration head. The dependent is ready only after those checks pass; an
   isolated prerequisite commit alone is insufficient. For example, dispatch
   independent `API` and `DOC`, integrate their accepted commits, validate the
   joined head, and only then dispatch `WIRE`. Return failed
   acceptance to the same owner; reuse passing checks only when their inputs and
   environment remain unchanged. An accepted item is complete, not assignable
   again.
3. Report the next action (or no action), evidence, and any acceptance gap. Stop
   before implementation.

## Implementation mode

Before delegation, read
[the implementation-mode procedure](references/implementation-mode.md)
completely. It is mandatory for implementation mode and owns queue construction,
runtime selection, owner packets, independent acceptance, integration, repairs,
and final validation. Stop when its dependency, task-scoped commit, or
capability gate cannot be satisfied; never implement an item in the controller.

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
task-scoped, reviewed, verified commit, the final worktree matches the recorded
pre-existing state, and no owner-reported blocker remains. Report the
item-to-commit mapping and final validation; otherwise finish blocked at the
first incomplete gate.
