---
name: deliver-issue
description: Use when explicitly asked to deliver a named tracker issue and its descendants, including clarification, planning, implementation and reviewed delivery.
disable-model-invocation: true
compatibility: "Requires a supported tracker/code-host binding and independent final review; never installs providers."
---

# Deliver issue

## Core principle

Deliver the named issue's outcome within its verified scope and invocation
permissions; one controller retains ownership from clarification through closure.

## Procedure

1. Resolve the named tracker issue against the verified repository. Local specs
   belong to the external `implement` workflow: return that route without creating
   an issue or executing delivery. Use `run-project` for board selection.
2. For an active board controller's verified single-ticket handoff, read the
   bundled [controller handoff](references/project-handoff.md) and follow it
   instead of standalone control. Inherit only the selected ticket scope, never
   its whole tree automatically. The board retains claims, shared state and
   merge/closure authority. A direct invocation encountering an existing
   controller returns to it without claiming or launching another scheduler.
3. Otherwise read [Issue lifecycle](references/issue-lifecycle.md) completely,
   then [Delivery bindings](references/provider-bindings.md) and the selected
   binding's issue operations. On GitHub read
   [Direct issue scope](references/github-binding.md#direct-issue-scope).
   For a Jira Cloud key read [Scope and readiness](references/jira-binding.md#scope-and-readiness)
   and the Jira tracker operations.
   For GitLab read the selected [tracker](references/gitlab-binding.md#tracker-operations)
   or [code-host](references/gitlab-binding.md#code-host-operations) operations.
   Resolve the complete root/descendant graph, holds, ownership, approved plans,
   pending outcomes and invocation grants before planning or writing.
4. Follow the issue lifecycle for clarification, planning, dependencies and
   scheduling. For each approved outcome follow the bundled
   [delivery lifecycle](references/delivery-lifecycle.md),
   [implementation procedure](references/implementation-mode.md) and
   [evidence and review](references/evidence-and-review.md).
   Preserve existing plans and use the PR boundaries in the
   [tree delivery procedure](references/issue-lifecycle.md#deliver-the-tree).
   Keep repairs with their owner.
5. Reconcile exact-head checks/reviews and explicit merge/closure grants through
   the binding. Follow the issue lifecycle's bounded waiting and resume procedure;
   board handoffs follow their controller's cadence instead.

## Finish gate

Use the issue lifecycle's outcome report. Ready PRs are pending issue completion
until permitted merge and closure are verified; closed children alone do not
satisfy the root's acceptance criteria. Preserve exact artifacts, outstanding
gates and resume conditions on pending or blocked work. Finish only when the
selected scope's acceptance and closure conditions have authoritative readback.
