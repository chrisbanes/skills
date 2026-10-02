---
name: deliver-spec
description: Use when explicitly asked to deliver an approved GitHub or local spec through a reviewed pull request, or when a Project controller delegates one claimed implementation ticket.
compatibility: "Implementation coordination uses implement-with-subagents. Behavior changes require tdd; triage is conditional. Never installs providers."
disable-model-invocation: true
---

# Deliver spec

## Core principle

Deliver one spec through coordinated implementation owners and independent
review. The delivery lead owns architecture, integration, task acceptance,
repairs to lead-owned coordination work, non-merge PR delivery, and final-head
evidence; workers own settled, bounded implementation tasks and their repairs.
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
   checks, feedback, and authority before acting.
2. For a GitHub issue missing `ready-for-agent`, use `triage` and wait for its
   approved outcome; do not change labels yourself. Local sources skip GitHub
   triage but need explicit stakeholder approval. Reuse a current `to-plan`
   plan, or invoke `to-plan` and honor its readiness and publication gates.
3. Before approval or execution, require independent plan review against the
   source, acceptance criteria, code facts, dependencies, and tests. Resolve
   findings through `to-plan` and reapprove repaired conversation plans. Stop
   without a reviewed and approved plan.
4. Reconcile existing implementation and acceptance evidence before dispatch.
   Do not reassign accepted work or reimplement an existing candidate just to
   satisfy worker routing; continue its review and delivery gates. Resolve
   final-reviewer capability before any implementation, including the lead's
   direct-edit exception, and worker capacity before new nontrivial
   implementation or a worker-owned repair. Assign each new settled task to
   one worker, including a single or tightly coupled sequential task; do not
   split one item into artificial pieces. The lead may directly edit only a fully understood,
   low-risk change when handoff clearly costs more than direct editing and no
   useful concurrent work exists. Record that reason. The lead owns only that
   initial direct edit and its repairs; this exception never transfers a
   worker's repair or follow-up. A qualifying initial edit needs no worker.
   Follow the shared [`implement-with-subagents` procedure](../implement-with-subagents/SKILL.md)
   for all other implementation, including single, sequential, and concurrent
   tasks; it owns checkout isolation, ready dispatch, capacity and priority,
   serialization, task acceptance, integration, wait behavior, and same-owner
   repair. Do not require a separate request for parallel work. While workers
   run, advance useful independent coordination. If worker capacity is busy,
   use the caller's supported wait or idle behavior and verify available
   capacity before dispatch; if the runtime lacks the required capability,
   report the blocker rather than falling back to lead implementation.
   Record the fixed base and preserve unrelated user work. For behavior
   changes, require the separately installed `tdd` skill and approved test
   seams before editing; obtain missing seam agreement and stop that behavior
   work if `tdd` is unavailable. Documentation and other work without a
   meaningful test seam use focused validation. Materialize the approved
   source and plan in an owner-only system-temp file for review; recreate it on
   resume.
5. Have each implementation owner self-review its task, commit only task-owned
   changes, and report required checks with the tested revision and results.
   This includes the lead only when the recorded low-risk direct-edit
   exception applies. Accept each delegated task once before integration under
   `implement-with-subagents`; the delivery lead reviews the integrated scope
   and records required checks at the tested revision. Require one
   fresh independent read-only reviewer for every delivery PR. Resolve that
   capability before implementation; if
   unavailable, report the blocker rather than waive review. Use an investigator
   in review mode or equivalent, with no inherited implementation conversation.
   Supply the approved source, plan, repository standards, fixed base, exact
   candidate head, and validation evidence. Require requirements and standards
   findings with evidence and a `ship`, `fix-first`, or `rethink` verdict.
   No external review skill or issue-tracker setup is required. Reuse a current
   final joined review from `implement-with-subagents` when it covers these
   inputs. Add reviewers only for distinct risks or substantial scope.
   Return findings to the implementation owner. After repairs, rerun affected
   checks and review the changed range plus interactions; broaden when earlier
   evidence is invalid or affected scope cannot be bounded. Confirm combined
   evidence covers the final clean head before pushing. Create and verify one
   draft PR for a nonempty integrated diff, or reuse the verified PR on resume.
   Use closing links only for real, verified GitHub issues.
6. Use `shepherd` for CI and reviewer feedback and PR operations. Keep code
   repairs with the original implementation owner; only repairs to the lead's
   permitted initial direct edit remain with the lead. Never move a worker's
   repair to the lead.
   Apply the same TDD, validation, and independent review gates to repairs and
   recheck the final head after each push. Return scope or design changes for a
   decision. Merge only with explicit authority valid for this invocation.
   After about 30 minutes of pending gates, hand back the exact pending checks,
   feedback, PR, and head for later resume.

## Finish gate

Report `ready` only when the final head passes applicable checks and reviews
with findings resolved; `merged` only after authorized merge readback;
`no-change` only when implementation and verification finish with an empty
final diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
