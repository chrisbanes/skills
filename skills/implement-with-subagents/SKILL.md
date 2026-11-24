---
name: implement-with-subagents
description: Use when implementing supplied tickets or plan tasks, resuming a delivery handoff for a triaged repair, or reviewing implementation orchestration.
compatibility: "Implementation requires independent read-only review. Use the installed tdd skill when user or repository policy requires it."
---

# Implement with subagents

## Core principle

Choose implementation ownership once from the whole task graph and the effective
implementation settings. Default to the lead for a single item or a graph with
no parallel point. When the graph has parallel work, assign every item to a
worker, including sequential heads and tails.
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
2. Assess the whole task graph and its recorded preflight choice using
   [Implementation ownership](references/subagent-selection.md#implementation-ownership)
   and the supplied policy, effective settings, authority and capacity.
   Flag an unnecessary serial worker or a split serial handoff. Accept one
   capable worker for a serial run with required settings the lead cannot meet
   when the worker is authorized and meets them. Solo runs use self-review.
   A graph with any parallel point assigns every item to workers, including
   sequential heads and tails. For delegated runs, assess task-scoped commits,
   owner self-review, focused validation, and controller acceptance before
   integration. An owner's report alone does not satisfy task acceptance.
   Separate worktrees do not make shared-file edits or work
   depending on unintegrated code independent. Treat supplied readiness,
   independence and capacity as authoritative: in delegated runs, dispatch the
   eligible ready frontier concurrently within capacity. Report any required
   routing mismatch and the safe resume action. Assess testing prerequisites
   against the supplied user and repository policy.
   Check reviewer capability before implementation. Check reuse-first allocation,
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
   integrated head. Leave accepted items with passing integrated checks complete.
   If an integrated check fails, assess how the original owner repairs forward.
   In a solo run, the lead repairs in the integration checkout. In a delegated
   run, assess the worker's route under the
   [failed-check repair rules](references/checkout-lifecycle.md#repair-after-failed-integrated-checks).
4. Report the next action, evidence, and any acceptance gap. Stop before
   implementation. Check release eligibility, safe retirement, and checkout
   dispositions without mutating them. For an invalid dependency graph or unsafe
   overlap, hold dispatch and return the specific defects to the plan owner; do
   not invent ordering or remove tasks or dependencies. Name any affected check that must be rerun at
   the integrated head, even when another blocker also prevents dispatch.

## Implementation mode

### Prerequisites

Follow user and repository testing policy. Choose meaningful behavioral tests at
established boundaries. When the user or repository requires the [`tdd` skill](https://github.com/mattpocock/skills),
use its agreed seam and red-before-green procedure. If that provider or required
agreement is missing, hold the affected item and report what it needs. Never
install a provider implicitly. Use focused validation for documentation and
configuration changes.

Verify independent read-only review capability from runtime metadata before
implementation. Hold implementation if review cannot run. Use a fresh reviewer
without inherited implementation context. Supply the approved source, plan,
repository standards, applicable review contracts, fixed base and exact head.
Require evidence-backed findings and a `ship`, `fix-first` or `rethink` verdict.
Apply [Behavioral review and repair](references/behavioral-review.md) for
boundary repairs, browser diagnostics and review coverage. Add reviewers only
for distinct risks or substantial scope.

Read the [implementation procedure](references/implementation-mode.md) before
starting. For a triaged PR finding, use its
[repair procedure](references/implementation-mode.md#resume-a-delivery-repair).

## Finish gate

In `review`, return the read-only assessment, evidence and acceptance gaps.

In `implement`, return the fixed base, clean integrated head, item-to-commit
and repair-owner mapping, validation and independent review covering that head.
Every changed item needs a self-reviewed commit, accepted before integration
when delegated. Preserve user work and task branches, and
[account for each worker checkout](references/checkout-lifecycle.md#account).
Report incomplete cleanup or another unmet gate as a blocker.

For delivery, identify each required suite that equivalent PR CI will run on
that commit. The controller takes the reviewed candidate and pending checks
through publication. Direct runs require the full suite before completion.
