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
   `glab` for GitLab. If it is ambiguous or unavailable, stop and ask. When the
   host provides a PR monitor that wakes this session on PR events, such as
   Claude desktop's `ccd_pr` tools, load those tools first if they are listed
   but deferred, then follow
   [host-managed monitoring](references/provider-commands.md#host-managed-monitoring)
   instead of polling. Project controllers and their ticket agents keep the
   Project waiting rules instead, because a session binds only one PR.
2. Establish targets and a handled-ID snapshot. Every external comment, review,
   or thread absent from that snapshot is new, including pre-session feedback.
   After each poll record feedback IDs, CI state, and this controller's comments.
   Resolve reporting and repair ownership per target. Reuse a supplied delivery
   record and retained implementation owner. For a standalone PR without a
   delivery record, use its existing PR/reporting context and shepherd snapshot;
   hydrate source scope, base/head, prior verdicts, findings and dispositions
   from verified PR and repository evidence, marking missing evidence unknown.
   When no retained workflow owner exists, the authorized controller may own
   in-scope repairs after verifying the target checkout/head and absence of a
   competing writer; record that fallback before code writes or an implementation
   repair handoff. A read-only audit may inspect the verified frozen candidate
   while ownership or writer state is unresolved; report those gaps as material
   uncertainty, without granting write authority or clearing publication gates.
   Do not infer an owner handle from commit authorship. Preserve recorded owners;
   an unavailable owner, uncertain existing claim or unknown writer state holds
   code writes until reconciled, with writers quiescent before any explicit
   reassignment. This fallback supplies neither missing scope nor extra grants.
   Reconcile applicable current-head review initiation under
   [PR review timing](references/pr-review-timing.md) on acquisition and relevant
   wakes, even without repairs; one-off inspections stay read-only.
3. Before repeated polling, use one lowest-cost capable read-only evidence
   helper when available. Select and brief it using the shared
   [selection and handoff reference](references/subagent-selection.md)
   when available. Give it targets and the snapshot; require new feedback IDs,
   body, location, review state, non-manual CI state, failed jobs, and log references.
   It never mutates. Keep triage, repairs, replies, pushes, resolution, retries,
   and merging with the authorized controller. Skip it under host-managed
   monitoring.
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
   non-obvious fixes, and out-of-scope conflicts. GitLab manual jobs are
   non-blocking unless instructed otherwise.
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
   cadence. Under host-managed monitoring, end the turn after the push instead.
8. Refresh the exact head; merge only when all required checks, reviews and
   finding dispositions pass and apply to that head, conflicts are absent, and
   the user granted explicit or standing merge authority. Do not infer authority from
   approval. Under host-managed monitoring, green CI never wakes the session, so
   use PR review timing's verified enforcement rule for pending remote gates,
   and disable
   auto-merge this controller enabled when escalating.

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
