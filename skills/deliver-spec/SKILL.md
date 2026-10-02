---
name: deliver-spec
description: Use when explicitly asked to deliver an approved GitHub or local spec through a reviewed pull request, or when a Project controller delegates one claimed implementation ticket.
compatibility: "Implementation coordination uses the bundled procedure. Behavior changes require the separately installed tdd skill; triage is conditional. Never installs providers."
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
4. Reconcile implementation and acceptance evidence before dispatch; never
   reassign accepted work or reimplement a current candidate just to satisfy
   worker routing. Resolve final-reviewer capability before any implementation
   and worker capability/capacity before new nontrivial work or a worker repair.
   Before either implementation path, record the fixed base and use a clean
   task checkout. Stop if unrelated uncommitted changes are present. Reuse a
   suitable clean checkout; create isolated worktrees only when concurrency or
   repository isolation requires them.
   Assign each new settled task to a worker, including one task in sequential
   work; do not split tasks artificially. The lead may directly edit only a
   fully understood, low-risk change when handoff clearly costs more and no
   useful concurrent work exists. Record that reason; the lead owns repairs to
   this initial edit, never a worker's task. This exception needs no worker.
   Otherwise follow the bundled [implementation procedure](references/implementation-mode.md)
   for single, sequential and concurrent tasks. It owns worker capability,
   isolation, dispatch, capacity, acceptance, integration, waiting and
   same-owner repair. Dispatch proven independent work by default without a
   separate request for parallelism; keep making useful independent progress
   while workers run. For
   behavior changes, require approved test seams and the separately installed
   `tdd` skill before editing; stop if unavailable. Use focused validation when
   there is no meaningful test seam. Follow [Evidence and review](references/evidence-and-review.md)
   for evidence provenance, applicability, amendment reuse and reviewer packets.
5. Each implementation owner self-reviews, commits only task-owned changes,
   and reports required checks with provenance under Evidence and review; this
   also applies to the lead's qualifying edit. Accept each delegated task once
   before integration. Require one fresh independent read-only reviewer per
   delivery PR, with capability resolved before implementation. If unavailable,
   report a blocker; never waive review. Use an investigator in review mode or
   equivalent without inherited implementation context. Give it the local
   evidence reference's owner-only packet, including prior findings and
   dispositions. Require evidence-backed requirements and standards findings
   with a `ship`, `fix-first`, or `rethink` verdict. Honor explicitly invoked
   provider contracts, scope, roles, capacity and output; report missing
   coverage rather than narrowing or substituting. The default route needs no
   external review skill or tracker. Reuse a current joined review from the
   bundled procedure only when it covers the exact inputs; add reviewers only
   for distinct risks or substantial scope. Return findings to the owner. After
   repairs, rerun affected checks and review changed ranges and interactions;
   broaden when evidence is invalid or scope cannot be bounded. Confirm combined
   coverage of the final clean head before pushing. Create and verify one draft
   PR for a nonempty integrated diff, or reuse the verified PR on resume. Use
   closing links only for verified GitHub issues.
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
with findings resolved and evidence applicable to that clean head;
`merged` only after authorized merge readback;
`no-change` only when implementation and verification finish with an empty
final diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
