---
name: deliver-spec
description: Use when explicitly asked to deliver one approved GitHub or local spec through a reviewed pull request, or delegated one claimed implementation ticket by a running Project controller.
compatibility: "Behavior changes require tdd; triage is conditional. Parallel implementation may use implement-with-subagents. Never installs providers."
disable-model-invocation: true
---

# Deliver spec

## Core principle

Deliver one spec with a single implementation owner and independent review.
Own implementation, repairs, PR identity, and final-head evidence; delegate
independent subtasks only when useful.
Manage approval in standalone mode; accept the controller's verified authority
in Project mode. Never select work from a Project queue.

## Select the mode

For an active `run-github-project` controller's verified ticket handoff, read
[Project controller handoff](references/project-handoff.md) and apply its
procedure instead of the standalone approval, merge, and timeout rules below.
The Project controller retains all shared state and merge authority.
For a direct named-spec request, use the standalone procedure below; if a
Project run already owns that issue, return it to that controller.

## Procedure

1. Resolve the named source, repository, approved contract, and any existing
   branch or PR from fresh state. On resume, reconcile the PR, exact head,
   checks, feedback, and authority before acting. For integration amendments,
   use [Evidence and review](references/evidence-and-review.md) to verify the
   installed planner contract and retained work before consuming any delta.
2. For a GitHub issue missing `ready-for-agent`, use `triage` and wait for its
   approved outcome; do not change labels yourself. Local sources skip GitHub
   triage but need explicit stakeholder approval. Reuse a current `to-plan`
   plan, or invoke `to-plan` and honor its readiness and publication gates.
3. Before approval or execution, require independent plan review against the
   source, acceptance criteria, code facts, dependencies, and tests. Resolve
   findings through `to-plan` and reapprove repaired conversation plans. Stop
   without a reviewed and approved plan.
4. Keep implementation with the delivery lead by default. Record the fixed
   base and use a clean task checkout, preserving unrelated user work. Implement
   approved slices in dependency order and validate their acceptance criteria.
   Read [Evidence and review](references/evidence-and-review.md) before
   implementation and apply its reuse and validation procedure.
   For behavior changes, require the separately installed `tdd` skill and
   approved test seams before editing; obtain missing seam agreement and stop
   that behavior work if `tdd` is unavailable. Documentation and other work
   without a meaningful test seam use focused validation. Materialize the
   reviewer packet from [Evidence and review](references/evidence-and-review.md)
   in an owner-only system-temp file; recreate it on resume.
   Use `implement-with-subagents` only for explicitly requested orchestration
   or independently useful parallel tasks. Honor its ownership, isolation,
   acceptance, integration, and repair gates when selected. Keep a single
   tightly coupled task with the delivery lead; do not require a child worker
   or extra worktree solely to separate implementation from coordination.
5. Self-review the task scope, commit only task-owned changes, and run the
   required checks with the provenance and applicability recorded under
   [Evidence and review](references/evidence-and-review.md). Require one
   fresh independent read-only reviewer for every delivery PR. Resolve that
   capability before implementation; if
   unavailable, report the blocker rather than waive review. Use an investigator
   in review mode or equivalent, with no inherited implementation conversation.
   Supply the self-contained reviewer packet, including prior findings,
   dispositions and outstanding coverage. Require requirements and standards
   findings with evidence and a `ship`, `fix-first`, or `rethink` verdict.
   The default route requires no external review skill or issue-tracker setup.
   Honor an explicitly invoked provider's actual contract under the reference;
   report missing scope or capacity rather than narrowing its invocation. Reuse
   a current final joined review from `implement-with-subagents` when it covers these
   inputs. Add reviewers only for distinct risks or substantial scope.
   Return findings to the implementation owner. After repairs, rerun affected
   checks and review the changed range plus interactions; broaden when earlier
   evidence is invalid or affected scope cannot be bounded. Confirm combined
   evidence covers the final clean head before pushing. Create and verify one
   draft PR for a nonempty integrated diff, or reuse the verified PR on resume.
   Use closing links only for real, verified GitHub issues.
6. Use `shepherd` for CI and reviewer feedback and PR operations. Keep code
   repairs with the delivery lead, or the original task owner when delegated.
   Apply the same TDD, validation, and independent review gates to repairs and
   recheck the final head after each push. Return scope or design changes for a
   decision. Merge only with explicit authority valid for this invocation.
   After about 30 minutes of pending gates, hand back the exact pending checks,
   feedback, PR, and head for later resume.

## Finish gate

Report `ready` only when the final head passes applicable checks and reviews
with findings resolved and evidence applicable to that clean head;
`merged` only after authorized merge readback;
`no-change` only when implementation and verification finish with an empty
final diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
