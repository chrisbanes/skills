---
name: run-project
description: Use when explicitly asked to set up, review or run a project board, select its next eligible ticket, or drain its authorized work.
compatibility: "External skill providers are mode-specific: review and setup require none; execution, triage, and Wayfinder lanes use the providers documented in references/workflow-providers.md."
disable-model-invocation: true
---

# Run project

## Core principle

The bound scope is the live control plane: fresh board state and this run's
operation-specific grants decide every claim, write and finish.
Default lanes are `Todo` → `In Progress` → `Done`; resolve them
through the resolved binding's claim and completion markers. Implementation readiness is
derived from Todo, `ready-for-agent`, and a verified active plan leaf.

Resolve the requested board scope. A Jira board configuration can select a
parent tree explicitly. A named issue routes to `deliver-issue` without
claiming it here. Selecting one board candidate does not broaden its authority
to descendants.

Select roles independently under [Delivery bindings](references/provider-bindings.md).
Use the [GitHub](references/github-binding.md), [Jira](references/jira-binding.md)
(including JQL boards), or GitLab [tracker](references/gitlab-binding.md#tracker-operations)
and [code-host](references/gitlab-binding.md#code-host-operations) procedures.
Preserve durable marker formats.

## Invariants

1. **Label authority:** eligibility requires a human-applied next-action role and `parked: false`; current Status routes the lane, never grants authority. Unlabelled Todo is the backlog. Keep `ready-for-agent` through active work; its removal stops writers and releases capacity while preserving assignment and all artifacts. Only a human restoring it permits recovery; the controller never adds or restores it, including triage and retries.
2. **Live authority:** claims, selection, merge, recovery and finish need complete fresh state; caches and partial reads are hints; rehydrate only changed or unverified records. Recheck operation-specific authority before each claim, write or merge, even from a reused snapshot; ranker eligibility grants nothing.
3. **Controller ownership:** only the controller claims, assigns, mutates shared Project state, merges, closes issues and reconciles; a ticket agent owns only its worktree, branch and non-merge PR changes.
4. **Unknown outcomes:** reconcile an unknown or failed mutation or publication before retrying, freeing capacity or reporting success.
5. **Preservation:** keep blocked, dependency-gated and human work in its frontier with owner, claim, slot, draft, artifacts, grants and budgets; never change state to empty the queue. Released capacity resumes only in free slots.
6. **Retained owner:** feedback, repairs and amendments keep the owner, claim and slot without a Todo reset; renew affected checks and reviews at the final head, never relying on earlier-head evidence.
7. **No invented gates:** never infer a permission, capacity limit, provider or prerequisite the supplied state lacks; independent runnable work continues while others wait.
8. **Supplied state:** decide review, setup or analysis from supplied complete state without another Project or repository read (still read references); judge the described environment, not providers missing from this workspace. A validated proposed diff is `configuration-ready-to-commit` even unwritten and uncommitted. Profile selection calls no routing service and grants no claim or merge authority; ignore legacy routing fields without editing them.
9. **No escape hatch:** renewal or amendment never resumes parked CI, grants live turns or resets qualification. Unknown or stale evidence blocks dependants; material architecture changes need full replan and review; changed authority or qualification needs a stakeholder or source decision.

A verified handoff covers in-scope implementation, tests and repairs under
the bundled [controller handoff](references/project-handoff.md), with one independent integrated-candidate review. Replans keep
verified plan state; true human work returns to a decision pause. `drain` parks
verified authority pauses and qualifying terminal required-CI claims outside
capacity before refreshing; in `next`, a required-CI stall keeps its slot. A
wrong plan seam still failing after one diagnosis and two repairs needs the
replan packet; a repeated non-CI failure stays with its owner, who asks one
capability-selected read-only evidence helper and resumes only on new direction,
else reports the exact blocker.

## Procedure

1. Resolve the selected binding and mode below.
2. Read every mandatory reference for that mode before acting.
3. Apply the invariants, lane and scheduler procedures through the binding;
   keep shared state and merge authority with the controller.
4. Answer every item and pass the final report gate below.

## Select the mode

- `review`: inspect or explain only. `setup`: configure or validate the binding, including explicitly approved legacy migration through the binding.
- `next`: default; at most one selected issue; after the startup merge decision settles, returns `waiting-for-human` without further waiting. A named Wayfinder child stays `next`.
- `drain`: only on explicit drain/run-all/until-empty request; no ticket cap. Use the selected tracker’s [remote wait procedure](references/drain-scheduler.md#project-watcher) when only remote or human waits remain.

Resolve merge permission once at startup under
[run authority](references/authority-and-pauses.md): honor an explicit merge or
no-merge instruction; otherwise ask with a 60-second default-no deadline while
delivery continues. Without permission, deliver ready PRs and pause only merges.

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
| Configuration change or renewal | [Project config](references/github-binding.md#renew-presentation-only-configuration) |
| Agent profiles or helper assignment | [Agent routing](references/agent-routing.md) |

## Answer each item

Per ticket or scenario, give its classification and safe next action, exact
preserved state and resume evidence (never the blocked operation's own result), and checks
repeated before execution.
For a repeated cycle, compare the previous cycle's evidence and give one
bounded next action or the exact blocker.

## Finish gate and report

Finish only when the selected lane's terminal conditions pass; otherwise
preserve and report its exact pending or blocked state. Use its report contract.
Lead with the outcome,
blockers with resume conditions, and the user's next action; unresolved
prerequisites are partial work, not an empty drain; audit detail goes last. Report intervals under the
[timing procedure](references/drain-scheduler.md#phase-timing-and-stalls).
