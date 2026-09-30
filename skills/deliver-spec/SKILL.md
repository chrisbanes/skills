---
name: deliver-spec
description: Use when explicitly asked to deliver one approved GitHub or local spec through a reviewed pull request, or delegated one claimed implementation ticket by a running Project controller.
compatibility: "Requires implement-with-subagents; triage is conditional. External dependencies follow provider gates. Never installs providers."
disable-model-invocation: true
---

# Deliver spec

## Core principle

Coordinate one spec through existing skills. Own PR identity and final-head
evidence; leave planning, implementation, and PR repairs with their providers.
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
4. Resolve `implement-with-subagents` in implementation mode; honor its current
   prerequisite, task, and finish gates. Never install providers. Materialize
   GitHub or in-chat source and plan in an owner-only system-temp file; recreate
   it on resume. Pass approved `to-plan` slices as plan tasks with the approved
   source path, plan, repository standards, and verified fixed-point base. After
   the provider finishes, create and verify exactly one draft PR if the final
   integrated diff is non-empty, or reuse the verified PR on resume. Use closing
   links only for real, verified GitHub issues, never for local sources or plan
   slices.
5. Use the provider's final joined review as the code gate; do not repeat it at
   the same head. Verify it covered the approved source and standards even if
   commits cite another issue; correct or stop. Resolve findings and re-review
   affected changes on the final PR head; stop if neither its `code-review`
   route nor its allowed local-spec fallback can run.
6. Use `shepherd` to triage CI and reviewer feedback and handle PR operations;
   override its direct code-repair step. Route code repairs through
   `implement-with-subagents`, then require its final checks and joined review
   at the new head before the lead pushes. Return scope or design changes for
   a decision. Recheck the final head after each push. Merge only with explicit
   authority valid for this invocation. After about 30 minutes of pending gates,
   hand back the exact pending checks, feedback, PR, and head for later resume.

## Finish gate

Report `ready` only when the final head passes applicable checks and reviews
with findings resolved; `merged` only after authorized merge readback;
`no-change` only when the provider finishes with an empty final integrated
diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
