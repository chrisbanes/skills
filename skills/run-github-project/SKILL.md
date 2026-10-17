---
name: run-github-project
description: Use when asked to set up, review, or operate a repository's GitHub Project workflow, including ready claims, role-labelled human work, unknown remote mutation outcomes, Todo triage, epics, checkpoints, next-issue execution, or an authorized drain.
compatibility: "External skill providers are mode-specific: review and setup require none; execution, triage, and Wayfinder lanes use the providers documented in references/workflow-providers.md."
disable-model-invocation: true
---

# Run GitHub Project

## Core principle

The Project is the live control plane: fresh board state and this run's
operation-specific grants decide every claim, write and finish.
Default lanes are `Backlog` → `Todo` → `Ready to implement` → `In progress` →
`Done`; resolve them through the trusted binding's verified option IDs.

## Invariants

1. **Column authority:** current column membership authorizes a ticket, never transition history. Backlog is read-only: never claim, plan, triage, close epics or resume cleanup there; only humans move items out. Automatic work starts at Todo.
2. **Live authority:** claims, selection, merge, recovery and finish need complete fresh state; caches and partial reads are hints; rehydrate only changed or unverified records. Recheck operation-specific authority before each claim, write or merge, even from a reused snapshot; ranker eligibility grants nothing.
3. **Controller ownership:** only the controller claims, assigns, mutates shared Project state, merges, closes issues and reconciles; a ticket agent owns only its worktree, branch and non-merge PR changes.
4. **Unknown outcomes:** reconcile an unknown or failed mutation or publication before retrying, freeing capacity or reporting success.
5. **Preservation:** keep blocked, dependency-gated and human work in its frontier with owner, claim, slot, draft, artifacts, grants and budgets; never change state to empty the queue. Released capacity resumes only in free slots.
6. **Retained owner:** feedback, repairs and amendments keep the owner, claim and slot without a Todo/Ready reset; renew affected checks and reviews at the final head, never relying on earlier-head evidence.
7. **No invented gates:** never infer a permission, capacity limit, provider or prerequisite the supplied state lacks; independent runnable work continues while others wait.
8. **Supplied state:** decide review, setup or analysis from supplied complete state without another Project or repository read (still read references); judge the described environment, not providers missing from this workspace. A validated proposed diff is `configuration-ready-to-commit` even unwritten and uncommitted. Profile selection calls no routing service and grants no claim or merge authority; ignore legacy routing fields without editing them.
9. **No escape hatch:** renewal or amendment never resumes parked CI, grants live turns or resets qualification. Unknown or stale evidence blocks dependants; material architecture changes need full replan and review; changed authority or qualification needs a stakeholder or source decision.

A verified handoff covers in-scope implementation, tests and repairs under
`deliver-spec`, with one independent integrated-candidate review. Replans keep
verified plan state; true human work returns to a decision pause. `drain` parks
verified authority pauses and qualifying terminal required-CI claims outside
capacity before refreshing; in `next`, a required-CI stall keeps its slot. A
wrong plan seam still failing after one diagnosis and two repairs needs the
replan packet; a repeated non-CI failure stays with its owner, who asks one
capability-selected read-only evidence helper and resumes only on new direction,
else reports the exact blocker.

## Select the mode

- `review`: inspect or explain only. `setup`: configure or validate the binding only.
- `next`: default; at most one selected issue; returns `waiting-for-human` without waiting. A named Wayfinder child stays `next`.
- `drain`: only on explicit drain/run-all/until-empty request; no ticket cap. With only remote or human waits left it runs the read-only [Project Watcher](references/drain-scheduler.md#project-watcher), never replacing the Refresh Gate.

`--auto-merge` grants merge authority for this invocation; otherwise deliver
ready PRs and pause only merges.

## Read before acting

| Mode | Mandatory reference |
| --- | --- |
| `review` or `setup` | [Review and setup](references/review-and-setup.md) |
| `next` or `drain` | [Review and setup](references/review-and-setup.md) for binding validation, then [execution controller](references/execution-controller.md) and [ticket lifecycle](references/ticket-lifecycle.md) |

Execution also reads [workflow providers](references/workflow-providers.md)
first (never install one implicitly), [authority and pauses](references/authority-and-pauses.md),
and [review contracts](references/review-contracts.md) before acceptance work;
`drain` reads [drain scheduler](references/drain-scheduler.md) completely before
drain queue work. Read the matching section first, even for analysis:

| Question involves | Read |
| --- | --- |
| Pre-dispatch readiness, qualification, live turns | [Unattended readiness](references/execution-controller.md#unattended-readiness) |
| Capacity, shared paths, refresh, timing, CI parking | [Drain scheduler](references/drain-scheduler.md) |
| Planner yield, amendment, replan | [Todo lane](references/todo-lane.md#yield-a-planner-for-delivery) |
| Configuration change or renewal | [Project config](references/project-config.md#renew-presentation-only-configuration) |
| Agent profiles or helper assignment | [Agent routing](references/agent-routing.md) |

## Answer each item

Per ticket or scenario, give its classification and safe next action, exact
preserved state and resume evidence (never the blocked operation's own result), and checks
repeated before execution.
For a repeated cycle, compare the previous cycle's evidence and give one
bounded next action or the exact blocker.

## Final report

Use the lane's terminal state and report contract. Lead with the outcome,
blockers with resume conditions, and the user's next action; unresolved
prerequisites are partial work, not an empty drain; audit detail goes last. Report intervals under the
[timing procedure](references/drain-scheduler.md#phase-timing-and-stalls).
