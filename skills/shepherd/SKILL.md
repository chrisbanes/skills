---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests, including triaging review feedback, CI failures, and routine follow-up."
disable-model-invocation: true
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
   `glab` for GitLab. If it is ambiguous or unavailable, stop and ask.
2. Establish targets and a handled-ID snapshot. Every external comment, review,
   or thread absent from that snapshot is new, including pre-session feedback.
   After each poll record feedback IDs, CI state, and this controller's comments.
3. Before repeated polling, use one lowest-cost capable read-only evidence
   helper when available. Select and brief it using the shared
   [selection and handoff reference](references/subagent-selection.md)
   when available. Give it targets and the snapshot; require new feedback IDs,
   body, location, review state, non-manual CI state, failed jobs, and log references.
   It never mutates. Keep triage, repairs, replies, pushes, resolution, retries,
   and merging with the authorized controller.
4. Poll with the platform CLI using [provider commands](references/provider-commands.md),
   then compare complete review, comment, and CI state with the snapshot. Inspect
   failed logs only when needed. Do not reprocess old feedback or post a status-only
   update.
5. Triage new evidence before remote mutation. Fix clear requests and narrow
   formatting, lint, compile, or test failures; answer clear questions in-thread.
   Escalate architectural or contradictory feedback, unfamiliar failures,
   non-obvious fixes, and out-of-scope conflicts. GitLab manual jobs are
   non-blocking unless instructed otherwise.
6. Handle each target in its own head checkout and batch known actionable items.
   Inspect failing logs and identify applicable local equivalents from actual
   workflow/check configuration before repairing. If evidence is missing, obtain
   it before guessing a fix; report checks unavailable on this host honestly.
   Run focused checks during repair and required full checks on the meaningful
   integrated candidate before pushing. Reuse valid evidence; repeat only checks
   invalidated by changes, unknown impact, or explicit repository/provider rules.
   Do not use CI as an iterative test runner or require full checks per slice
   commit. Hold the push while applicable required checks fail or lack evidence.
   Reply after an addressed change or answer; resolve its thread only after the reply and required push succeed.
   Do not combine heads, push after every comment, resolve a local-only fix, or comment when nothing changed.
7. Recheck CI after the verified repair push; return to step 6 on another
   code-related failure. Retry a suspected flaky GitLab job once without code
   changes; report a second failure. Poll pending checks every 2–5 minutes,
   active repair every 30–60 seconds, and after three or more unchanged cycles
   every 10+ minutes. Two unchanged cycles remain on the normal 2–5 minute
   cadence.
8. Merge only when requirements and CI are green, conflicts are absent, and the
   user granted explicit or standing merge authority. Do not infer authority from
   approval.

## Finish or escalate

Continue until the user stops monitoring, every target is merged or closed, or
an escalation is needed. Report the target, current CI/review state, actions
taken, checks actually run (say none when none ran), checks unavailable or
unknown, and the next required human decision. When failure evidence is missing,
request the exact check name and log, PR diff and head commit, and workflow/check
configuration before proposing a targeted repair. Give the verification order:
run affected CI-equivalent checks on the required host, fix their failures,
complete required integrated-candidate checks, and push once evidence covers the
candidate. Use CI
as confirmation. Do not claim any of those steps happened when only describing
the plan. Escalate immediately for ambiguous platform/target selection, an
unresolved conflict,
material human judgment, conflicting reviewer direction, or a failure that
remains after three repair cycles.
