---
name: deliver-issue
description: Use when explicitly asked to deliver a named tracker issue and its descendants, including clarification, planning, implementation and reviewed delivery.
disable-model-invocation: true
compatibility: "Requires a supported tracker/code-host binding and the installed implement-with-subagents skill for implementation and repair."
---

# Deliver issue

## Core principle

Deliver the named issue's outcome within its verified scope and invocation
permissions; one controller retains ownership from clarification through closure.

## Assess supplied state

When asked to assess supplied state, take capabilities, approval and authority
from the supplied facts. Use this checklist to answer. Leave cited plan files
and installed executor entrypoints unopened. Consult a delivery reference only
for an unresolved decision within the permitted read scope.

1. **Implementation handoff.** Name `implement-with-subagents` as the executor
   for each approved outcome. Use one PR for a single cohesive outcome. For
   an issue tree, preserve the supplied PR boundaries and dependency order.
   Reuse accepted plan evidence and preserve testing policy. Assign tightly
   coupled serial edits and repairs to the lead by default. Use workers when
   independence, isolation or an explicit implementation requirement
   justifies them.
2. **Candidate decision.** For each changed candidate, require one fresh
   independent read-only reviewer to check the approved source, repository
   standards, validation evidence and exact clean candidate HEAD. Use the
   available runtime reviewer. Apply CI and external-review gates only when
   the supplied policy requires them. Verify the draft PR points to the
   reviewed head. For no-change, require verified acceptance and an empty
   final diff after implementation and verification.
3. **Repair and publication.** Name `shepherd` for CI, PR feedback and the
   verified repair push. Resume the same `implement-with-subagents` executor
   and original implementation owner for edits. Renew affected checks and
   review on the repaired head before `shepherd` pushes it. Reuse unaffected
   evidence.
4. **Authority.** State which merge and closure grants are present. Keep
   work pending when a necessary grant or current-head evidence is missing.
   For a separate plan awaiting approval, request it with the outcome,
   approach and validation from the supplied plan details. Cite the supplied
   plan pointer as given.

Finish with these decisions and any gaps in the supplied evidence. Stop here
for a supplied-state assessment.

## Live delivery procedure

1. For a local spec with no tracker item, return the route through `to-plan`
   in conversation mode for one plan, then `implement-with-subagents` for one MR.
   Stop there without creating an issue or executing delivery. Use `run-project`
   for board selection. Otherwise resolve the named tracker issue against the
   verified repository.
2. For an active board controller's verified single-ticket handoff, read the
   bundled [controller handoff](references/project-handoff.md) and follow it
   instead of standalone control. Inherit only the selected ticket scope, never
   its whole tree automatically. The board retains claims, shared state and
   merge/closure authority. A direct invocation encountering an existing
   controller returns to it without claiming or launching another scheduler.
3. Otherwise read [Issue lifecycle](references/issue-lifecycle.md) completely,
   then [Delivery bindings](references/provider-bindings.md) and the selected
   binding's issue operations. For a GitHub tracker read
   [Direct issue scope](references/github-delivery.md#direct-issue-scope).
   For a Jira Cloud key read [Scope and readiness](references/jira-binding.md#scope-and-readiness)
   and the Jira tracker operations.
   For GitLab read the selected [tracker](references/gitlab-binding.md#tracker-operations)
   or [code-host](references/gitlab-binding.md#code-host-operations) operations.
   Resolve the complete root/descendant graph, holds, ownership, approved plans,
   pending outcomes and invocation grants before planning or writing.
4. Follow the issue lifecycle for clarification, planning, dependencies and
   scheduling. After verifying readiness in standalone delivery, use
   [Bug diagnosis](references/bug-diagnosis.md) for a bug with clear expected
   behavior and no current plan when the evidence leaves the fix speculative.
   Do this before choosing the fast path or drafting an implementation plan.
5. Preserve existing plans and the
   [tree's PR boundaries](references/issue-lifecycle.md#deliver-the-tree).
   Use the [delivery lifecycle](references/delivery-lifecycle.md) to hand off
   implementation, qualify the candidate, publish and route repairs. Apply
   [evidence and review](references/evidence-and-review.md) at the candidate
   and repair gates.
6. Reconcile exact-head checks/reviews and explicit merge/closure grants through
   the binding. Follow the issue lifecycle's bounded waiting and resume procedure;
   board handoffs follow their controller's cadence instead.

## Finish gate

Use the issue lifecycle's outcome report. Ready PRs are pending issue completion
until permitted merge and closure are verified; closed children alone do not
satisfy the root's acceptance criteria. Preserve exact artifacts, outstanding
gates and resume conditions on pending or blocked work. Finish only when the
selected scope's acceptance and closure conditions have authoritative readback.
