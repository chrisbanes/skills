---
name: deliver-spec
description: Use when explicitly asked to deliver an approved GitHub or local spec through a reviewed pull request, or when a Project controller delegates one claimed implementation ticket.
compatibility: "Solo or delegated implementation uses the bundled procedure; triage is conditional. Never installs providers."
---

# Deliver spec

## Core principle

Deliver one approved outcome with proportional validation and independent final
review. The lead owns architecture, integration and delivery, and implements
tightly coupled or sequential work directly by default. Delegate only when
independent work, isolation or specialist investigation justifies the
overhead; available worker capacity alone does not. Preserve explicit ownership,
external-action permissions, execution budgets and invocation-specific merge
authority. Never select work from a Project queue.

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
2. Plan: reuse a current `to-plan` plan; otherwise invoke `to-plan`
   (conversation mode for a local source) and honor its readiness and
   publication gates. A source qualifying for the [fast path](references/fast-path.md)
   applies it instead. For a GitHub issue missing `ready-for-agent`, first use
   `triage` and wait for its approved outcome; do not change labels yourself.
   Local sources skip triage but need explicit stakeholder approval. For an
   approved local source with no plan that does not qualify for the fast path,
   name conversation-mode `to-plan` as the initial route, including when
   answering a resume question.
   Approval covers the accepted contract and only the live qualification
   allowances it explicitly records; do not infer extra attempts or authority.
3. Verify scope and boundaries once. A verified handoff authorizes continuing
   in-scope implementation, testing and repairs in the isolated checkout;
   require no per-file or per-stage permission packets. Reuse valid plans,
   reviews and checks. Require earlier independent review only for a concrete
   risk that must be settled before proceeding, such as freezing experimental
   labels before observing outputs; build work independent of it, such as
   tooling, in parallel rather than after. Keep required deliverables and data-handling and spend limits;
   build no unrequested general infrastructure. Establish reviewer capability from runtime
   metadata, never by spawning a capability-only reviewer. If final review
   cannot run, report that delivery blocker without waiving review.
4. Follow the bundled [implementation procedure](references/implementation-mode.md)
   for solo or delegated work, ownership, isolation and recovery. Implement
   sequential or tightly coupled slices as the lead, not through a worker. Follow the stated repository or user testing policy.
   Reconcile retained work before implementing; never redo accepted work for
   routing.
   Follow [Evidence and review](references/evidence-and-review.md) for testing,
   corrections and the single reusable delivery record. When the source requires
   asynchronous or persistent live qualification, apply
   [Live qualification and failure recovery](references/qualification-failure.md)
   before attempts and resumes; do not add it to ordinary offline work.
5. Self-review the integrated candidate, run affected local and required
   pre-push checks, then give one independent read-only reviewer per delivery
   PR the approved source, repository standards, the exact clean candidate head
   and its validation evidence. Use a fresh agent that makes no
   writes and has no inherited implementation context. Reuse valid
   independent coverage; do not duplicate a plan or implementation review.
   Require evidence-backed findings and a `ship`, `fix-first`, or `rethink`
   verdict. Honor explicitly invoked provider contracts and report missing
   coverage. Return findings to the implementation owner; at the repaired head,
   renew affected checks and review changed ranges and interactions. Broaden only when impact cannot
   be bounded or an explicit requirement demands it. Confirm combined coverage
   of the final clean head before pushing. If finished, verified work leaves
   the final diff empty, report `no-change`; a starting empty diff is not
   `no-change`. Otherwise create one draft PR, or reuse the existing PR, and
   verify its head is the reviewed head. Apply
   [PR review timing](references/pr-review-timing.md): start applicable external review
   while CI runs, using verified draft support or earlier PR readiness when
   permitted. Keep delivery `pending` until all final-head gates pass. Use
   closing links only for verified GitHub issues.
6. `shepherd` owns CI, feedback and every PR operation. Keep repairs with their
   implementation owner; renew affected checks and focused review at the
   repaired head before pushing. Routine implementation or fixture corrections preserving
   requirements, coverage, architecture and authority proceed under the existing
   approval; record them briefly. Material changes require the appropriate
   decision and replan before affected work continues. Weakened qualification
   or expanded permissions are material. Merge only with explicit authority
   valid for this invocation. After about 30 minutes of pending gates, hand back
   the exact pending checks, feedback, PR and head for later resume.

## Finish gate

Report `ready` only when the final head passes required checks and reviews
with findings resolved and evidence applicable to that clean head;
`merged` only after authorized merge readback;
`no-change` only when implementation and verification finish with an empty
final diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
