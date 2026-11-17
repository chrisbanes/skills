# Deliver an approved outcome

Use this internal procedure for one approved delivery outcome after the owning
controller has resolved scope, planning, ownership and operation grants. An outcome
may cover several issues when the approved plan groups them. This procedure
never selects a queue or expands a delegated scope.

## Procedure

1. Verify scope and boundaries once. A verified handoff authorizes continuing
   in-scope implementation, testing and repairs in the isolated checkout;
   require no per-file or per-stage permission packets. Reuse valid plans,
   reviews and checks. Require earlier independent review only for a concrete
   risk that must be settled before proceeding, such as freezing experimental
   labels before observing outputs; build work independent of it, such as
   tooling, in parallel rather than after. Keep required deliverables and data-handling and spend limits;
   build no unrequested general infrastructure. Establish reviewer capability from runtime
   metadata, never by spawning a capability-only reviewer. If final review
   cannot run, report that delivery blocker without waiving review.
2. Follow the bundled [implementation procedure](implementation-mode.md)
   for ownership preflight, isolation and recovery. Follow the stated
   repository or user testing policy with the selected owner.
   Reconcile retained work before implementing; never redo accepted work for
   routing.
   Follow [Evidence and review](evidence-and-review.md) for testing,
   corrections, revision-isolated evidence and the single reusable delivery
   record. When the source requires
   asynchronous or persistent live qualification, apply
   [Live qualification and failure recovery](qualification-failure.md)
   before attempts and resumes; do not add it to ordinary offline work.
3. Self-review the integrated candidate, run affected local and required
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
   `no-change`. Otherwise open or update one draft change request through the
   code-host binding and verify its head is the reviewed head. Apply
   [PR review timing](pr-review-timing.md): start applicable external review
   while CI runs, using verified draft support or earlier PR readiness when
   permitted. Keep delivery `pending` until all final-head gates pass. Link and
   verify the tracker item and closure intent under Delivery bindings;
   closing keywords require explicit closure authority for the intended issue
   set and verified native closure for the selected provider pair.
4. `shepherd` coordinates CI, feedback and change-request operations through
   the selected code-host binding. Keep repairs with their
   implementation owner; renew affected checks and focused review at the
   repaired head before pushing. Routine implementation or fixture corrections preserving
   requirements, coverage, architecture and authority proceed under the existing
   approval; record them briefly. Material changes require the appropriate
   decision and replan before affected work continues. Weakened qualification
   or expanded permissions are material. Merge only with explicit authority
   valid for this invocation. Verify merge through the code-host binding, then
   reconcile native closure or perform the authorized tracker close under
   Delivery bindings. For standalone tree delivery, the
   [issue lifecycle](issue-lifecycle.md#wait-and-resume) owns bounded waiting after
   independent runnable work is exhausted. Board-owned work follows its controller's
   cadence. Retain the exact pending checks, feedback, PR and head for later resume.

## Finish gate

Report `ready` only when the final head passes required checks and reviews
with findings resolved and evidence applicable to that clean head;
`merged` only after authorized merge readback, reporting tracker closure
separately and never declaring a ticket complete before verified closure;
`no-change` only when implementation and verification finish with an empty
final diff; `pending` with exact outstanding gates; otherwise `blocked` with the
needed decision or capability. Preserve the PR and source pointers on pending
or blocked runs. Do not report a prior head as the reviewed result.
