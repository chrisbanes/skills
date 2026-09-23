---
name: run-github-project
description: Use when asked to set up, review, or operate a repository's GitHub Project workflow, including ready claims, human-owned Planning work, unknown remote mutation outcomes, Backlog triage, epics, checkpoints, next-issue execution, or an authorized drain.
compatibility: "External skill providers are mode-specific: review and setup require none; execution, triage, and Wayfinder lanes use the providers documented in references/workflow-providers.md."
disable-model-invocation: true
---

# Run GitHub Project

The Project is the live control plane. Apply these invariants throughout:

1. **Live authority:** claims, selection, and finish decisions require complete,
   fresh GitHub and Project state; cache and partial reads are hints only.
2. **Controller ownership:** only the controller claims, assigns, mutates shared
   Project state, merges, closes issues, and reconciles. A ticket agent owns its
   worktree, branch, and non-merge PR mutations only.
3. **Unknown outcomes:** reconcile a failed or timed-out remote mutation before
   retrying or reporting success.
4. **Preservation:** retain blocked, dependency-gated, and human-owned work in
   its authoritative frontier or partial-drain report; never change state merely
   to make the queue appear empty.

Preserve Planning authority through contract-preserving replans, return true
human work to Backlog, and in `drain` pair occupied slots with warm worktrees
and persistent ticket agents. Park only qualifying terminal required-CI claims
outside capacity before refreshing the control plane.

## Select the mode

- `review`: inspect or explain only; no operation.
- `setup`: configure, validate, or repair the binding only; no Project work.
- `next`: default execution; process at most one selected issue.
- `drain`: only on explicit drain/run-all/repeat/until-empty request.

A named Wayfinder child remains `next`; it grants neither drain authority nor a
claim bypass. Before any mode-specific action, read the matching mandatory lane:

| Mode | Mandatory reference |
| --- | --- |
| `review` or `setup` | [Review and setup](references/review-and-setup.md) |
| `next` or `drain` | [Execution controller](references/execution-controller.md), then [ticket lifecycle](references/ticket-lifecycle.md) |

For execution, read [workflow providers](references/workflow-providers.md)
before preconditions; it is authoritative on required, conditional, optional
providers, sources, installation commands, and lane-specific fallback. Never
install a provider implicitly. Read all providers and specialist contracts
required by the execution-controller lane before their relevant action.

## Cross-mode boundaries

`review` may inspect only permitted repository, supplied, and read-only remote
state. It never configures, ranks, claims, transitions, triages, plans,
delegates, mutates, pushes, merges, or closes. Finish `review-complete` with
evidence, safe next action, and uncertainty, or `review-blocked`.

`setup` reads the configuration required to produce and validate a binding but
requires neither execution dependencies or authority nor clean execution state.
It never ranks/claims, changes Project/issue/PR state, creates worktrees, plans,
implements, pushes, or merges. It finishes only `configuration-valid`,
`configuration-ready-to-commit`, or `configuration-blocked`.

`next` and `drain` require the controller and lifecycle lanes. Standing authority
expires on stop, timeout, crash, or interruption. Do not support publish-only
mode or impose a skill-defined ticket cap in `drain`.

## Final report

The selected lane defines terminal state and report evidence. `setup` reports
only identity, configuration files/read-or-changed, live validation, unresolved
values, committed-base state, and one configuration result. Execution reports
mode, capacity, configuration digest, live queries, authority, scheduler,
providers, routing ledger, frontiers, parked/triage/reconciliation outcomes, and
per-ticket selection, lease/plan, branch/commit/PR, verification/review,
reconciled mutation/merge, and final preserved or cleaned state.
