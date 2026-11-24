---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests, including triaging review feedback, CI failures, and routine follow-up."
---

# Shepherd

## Core principle

Batch each target's actionable feedback into one verified push. Resolve
addressed threads after replying and pushing. Merge only with authority.

## Procedure

1. Identify the platform from `git remote get-url origin`. Use `gh` for GitHub
   or `glab` for GitLab. Escalate ambiguous targets or platforms. For a one-off
   inspection or no open targets, report the state and stop. Project controllers
   and ticket agents follow Project waiting rules. Otherwise, when the host
   offers PR event wakes, load its monitor tools (including deferred tools such
   as Claude Desktop's `ccd_pr`) and follow
   [host-managed monitoring](references/provider-commands.md#host-managed-monitoring).
2. Establish targets and a handled-ID snapshot. Every external comment, review,
   or thread absent from that snapshot is new, including pre-session feedback.
   After each poll record feedback IDs, CI state, and this controller's comments.
   For a `deliver-issue` PR, send the finding, current head and delivery record
   to delivery to resume `implement-with-subagents`. Use the reviewed repair
   for the next push. Return scope changes for replanning.
   For other PRs, retain the implementation owner and reuse the delivery
   record or PR snapshot. Verify scope, base/head, prior verdicts, findings
   and dispositions. Mark missing evidence unknown. Only when no workflow
   owner exists may the authorized controller take a repair. Verify the target
   checkout, head and absence of competing writers, then record that decision
   before edits or handoff. Never infer ownership from commit authorship.
   Hold writes on an unresolved claim or unavailable owner until prior work is
   reconciled and writers are quiescent. A read-only audit can inspect the
   frozen candidate meanwhile. Report uncertainty and preserve publication gates.
   Reconcile applicable current-head review initiation under
   [PR review timing](references/pr-review-timing.md) on acquisition and relevant
   wakes, even without repairs; one-off inspections stay read-only.
3. Read routine evidence in the controller. Delegate only a specific diagnostic
   question about a large failed CI log to a read-only helper. Use the
   [handoff reference](../subagent-delegation/references/subagent-selection.md).
   Supply the target, head, failed job, log and question. Request a diagnosis
   with log references and uncertainty. Keep monitoring and remote actions
   with the authorized controller.
4. Compare complete reviews, comments and checks against the snapshot using
   [provider commands](references/provider-commands.md). Under host monitoring,
   read once per wake. Act only on new evidence and skip status-only comments.
5. Triage new evidence before remote mutation. Fix clear requests and narrow
   formatting, lint, compile, or test failures; answer clear questions in-thread.
   Apply [Behavioral review and repair](../implement-with-subagents/references/behavioral-review.md) for
   related boundary cases, the two-round convergence audit, review coverage and
   browser failure evidence. Use the reporting context and repair owner resolved
   in step 2; the authorized controller retains remote mutations.
   Escalate architectural or contradictory feedback, unfamiliar failures,
   non-obvious fixes, and out-of-scope conflicts. Classify GitLab manual jobs
   using the provider's candidate checks in step 4.
6. Repair each target in its own head checkout, in this order:

   - Inspect the failed log and identify local equivalents from the check
     configuration. If evidence is missing, request the exact check name, log,
     PR diff, head and configuration. Identify unavailable or unknown checks.
   - Batch the fix with that target's clear review requests. Run affected
     CI-equivalent checks on the required host and reuse still-valid evidence.
     Broaden checks when impact is unknown.
   - Run required full checks on the integrated candidate. Required CI on
     the pushed head may supply the same suite when repository and provider
     rules allow it. That CI gates acceptance and merge.
   - Renew affected checks and independent review on each changed head under
     PR review timing. Push once all pre-push requirements pass. Use CI to
     confirm the repair. Reply to the finding and resolve only after the reply
     and any required push succeed.
7. Recheck CI after the verified repair push; return to step 6 on another
   code-related failure. Retry a suspected flaky GitLab job once without code
   changes; report a second failure. Poll pending checks every 2–5 minutes,
   active repair every 30–60 seconds, and after three or more unchanged cycles
   every 10+ minutes. Two unchanged cycles remain on the normal 2–5 minute
   cadence. Under host-managed monitoring, follow the host procedure after
   the push to continue watching and end the turn.
8. Merge only with explicit or standing authority, no conflicts, and passing
   checks, reviews and finding dispositions for the refreshed head. Follow
   the merge routing in step 4 and require that SHA; requalify on mismatch.
   For queue or auto-merge, verify final-head enforcement. For pending gates,
   follow PR review timing and check which events the active monitor wakes on.
   Disable controller-enabled auto-merge on escalation.

## Finish or escalate

Continue until the user stops monitoring, all targets merge or close, or
escalation is needed. Escalate immediately for an unresolved conflict, a
material human decision, contradictory reviews, or a failure still present
after three repair cycles.

Report each target's current CI and review state, actions taken, checks run
(say when none ran), unavailable evidence and the next required human decision.
Describe repairs in step 6 order. For host monitoring, name the events that
will not wake the session.
