---
name: run-github-project
description: Use when asked to set up, review, or operate a repository's GitHub Project workflow, including ready claims, role-labelled human work, unknown remote mutation outcomes, Todo triage, epics, checkpoints, next-issue execution, or an authorized drain.
compatibility: "External skill providers are mode-specific: review and setup require none; execution, triage, and Wayfinder lanes use the providers documented in references/workflow-providers.md."
disable-model-invocation: true
---

# Run GitHub Project

Use `Backlog` → `Todo` → `Ready to implement` → `In progress` → `Done` as
the default board lanes. `Todo` queues planning. Resolve lane names in this
procedure and its references through the trusted binding's verified names and
option IDs; preserve existing configured names. Current column membership
supplies ticket authorization; never inspect column transition history for
permission, plan freshness, or a Ready handoff. Backlog is read-only: never
claim, plan, triage, close epics, resume cleanup, or promote its items. Only
humans move items out of Backlog. Continue automatic work only in Todo and
later applicable columns, subject to ownership, dependencies, plan integrity,
and the current run's operation-specific grants.

The Project is the live control plane. Apply these invariants throughout:

1. **Live authority:** claims, selection, and finish decisions require complete,
   fresh GitHub and Project state; cache and partial reads are hints only.
2. **Controller ownership:** only the controller claims, assigns, mutates shared
   Project state, merges, closes issues, and reconciles. A ticket agent owns its
   worktree, branch, and non-merge PR mutations only.
3. **Unknown outcomes:** reconcile a failed or timed-out remote mutation before
   retrying or reporting success.
4. **Preservation:** retain blocked, dependency-gated, and role-labelled human work in
   its authoritative frontier or partial-drain report; never change state merely
   to make the queue appear empty.

Preserve verified plan state through contract-preserving replans, return true
human work to a decision pause, and in `drain` pair occupied slots with warm worktrees
and persistent ticket agents. Park verified authority pauses and qualifying
terminal required-CI claims outside capacity before refreshing the control plane.

## Select the mode

- `review`: inspect or explain only; finish under the review contract.
- `setup`: configure or validate the binding only; finish under the setup contract.
  Neither mode dispatches Project work or requires execution dependencies.
- `next`: default execution; process at most one selected issue.
- `drain`: only on explicit drain/run-all/repeat/until-empty request; no
  skill-defined ticket cap. A merge pause remains resumable work.

A named Wayfinder child remains `next`; it grants neither drain authority nor a
claim bypass. Before any mode-specific action, read the matching mandatory lane:

| Mode | Mandatory reference |
| --- | --- |
| `review` or `setup` | [Review and setup](references/review-and-setup.md) |
| `next` or `drain` | [Review and setup](references/review-and-setup.md) for binding validation, then [execution controller](references/execution-controller.md) and [ticket lifecycle](references/ticket-lifecycle.md) |

For execution, read [workflow providers](references/workflow-providers.md)
before preconditions; it is authoritative on required, conditional, optional
providers, sources, installation commands, and lane-specific fallback. Never
install a provider implicitly. Read all providers and specialist contracts
required by the execution-controller lane before their relevant action.
Read [run authority and ticket pauses](references/authority-and-pauses.md).
Use `next --auto-merge` or `drain --auto-merge` to grant merge authority for this
invocation. Without it, deliver to ready PRs and pause only their merges while
the board continues.
When the trusted configuration enables agent profiles, read
[agent routing](references/agent-routing.md) before assigning a planner, ticket
agent, or helper.
For `drain`, read [drain scheduler](references/drain-scheduler.md) completely
before drain queue work. For `next` or `drain`, read
[review contracts](references/review-contracts.md) completely before acceptance
work.

## Final report

Use the selected lane's terminal state and report contract. Lead an execution
report with the outcome, completed tickets, work still moving, exact blockers,
and the user's next action, if any. Link to durable issue, PR, and checkpoint
evidence instead of repeating unchanged queries or no-op events. Keep mode,
capacity, configuration digest, live-query and authority evidence, routing
ledger, frontiers, parked/triage/reconciliation outcomes, and per-ticket
selection, lease/plan, branch/commit/PR, verification/review, reconciled
mutation/merge, and preserved or cleaned state available in a concise appendix
when needed to audit a decision or resume work.
