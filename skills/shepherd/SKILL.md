---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests, including triaging review feedback, CI failures, and routine follow-up."
---

# Shepherd

## Core principle

Keep an authorized PR or MR moving with evidence, not noise: poll, act on new
actionable items, batch each target's local fixes into one push, then resolve
addressed threads. Use affected local checks during repairs and required full
checks on meaningful integrated candidates; use CI as confirmation. Never merge without explicit
authority.

Do not start persistent polling for a one-off inspection, no open targets, or an action requiring human judgment; report the state and stop.

## Procedure

1. Detect the platform with `git remote get-url origin`: use `gh` for GitHub and
   `glab` for GitLab, never `gh`. If it is ambiguous or unavailable, stop and ask. When the
   host provides a PR monitor that wakes this session on PR events, such as
   Claude desktop's `ccd_pr` tools, load those tools first if they are listed
   but deferred, then follow
   [host-managed monitoring](references/provider-commands.md#host-managed-monitoring)
   instead of polling. Project controllers and their ticket agents keep the
   Project waiting rules instead.
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
3. Read routine PR/MR evidence in the controller. Use a read-only helper only
   for one specific diagnostic question about a large failed CI log. Select and
   brief it using the shared
   [selection and handoff reference](references/subagent-selection.md).
   Give it the exact target, head, failed job and log, the question, and a bounded
   result format: diagnosis, supporting log references, and uncertainty. It
   never mutates or takes over polling. Keep triage, replies, pushes,
   resolution, retries, and merging with the authorized controller.
4. Poll with the platform CLI using [provider commands](references/provider-commands.md),
   then compare complete review, comment, and CI state with the snapshot. Inspect
   failed logs only when needed. Do not reprocess old feedback or post a status-only
   update. Under host-managed monitoring, read once per wake; never start a
   timer, loop, or repeated poll.
5. Triage new evidence before remote mutation. Fix clear requests and narrow
   formatting, lint, compile, or test failures; answer clear questions in-thread.
   Apply [Behavioral review and repair](references/behavioral-review.md) for
   related boundary cases, the two-round convergence audit, review coverage and
   browser failure evidence. Use the reporting context and repair owner resolved
   in step 2; the authorized controller retains remote mutations.
   Escalate architectural or contradictory feedback, unfamiliar failures,
   non-obvious fixes, and out-of-scope conflicts. Classify GitLab manual jobs
   using the provider's candidate checks in step 4.
6. Handle each target in its own head checkout and batch known actionable items.
   Inspect failing logs and identify applicable local equivalents from actual
   workflow/check configuration before repairing. If evidence is missing, obtain
   it before guessing a fix; report checks unavailable on this host honestly.
   Run focused checks during repair, reusing still-valid evidence, and required full checks on the meaningful
   integrated candidate before pushing, except where the PR's required CI runs
   the same full suite and no repository or provider rule requires a local run;
   then CI on the pushed head supplies that evidence before delivery acceptance
   or merge. Obtain or renew applicable independent review under PR review timing
   before push. Preserve stricter repository/provider rules; renew affected checks
   or broaden when impact is unknown.
   Do not use CI as an iterative test runner or require full checks per slice
   commit. Hold the push while checks required before push fail or lack evidence; a
   CI-supplied full suite gates acceptance or merge instead. Reassess evidence
   after each head change under PR review timing; renew affected independent
   review before pushing repairs.
   Reply after an addressed change or answer; resolve its thread only after the reply and required push succeed.
   Do not combine heads, push after every comment, resolve a local-only fix, or comment when nothing changed.
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

Continue until the user stops monitoring, every target is merged or closed, or
an escalation is needed. Report the target, current CI/review state, actions
taken, checks actually run (say none when none ran), checks unavailable or
unknown, and the next required human decision. Under host-managed monitoring,
also name the events that monitor does not wake on. When describing a repair
cycle, give this order: inspect the failed log (if missing, request the exact
check name, log, PR diff, head and check configuration, and say which local
equivalents are unidentified); batch the fix with that PR's clear review
requests; run affected CI-equivalent checks on the required host; reuse
still-valid evidence; complete integrated-candidate checks per step 6; push
once; use CI as confirmation. Do not claim unrun steps happened. Escalate immediately for ambiguous platform/target selection, an
unresolved conflict,
material human judgment, conflicting reviewer direction, or a failure that
remains after three repair cycles.
