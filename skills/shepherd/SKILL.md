---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests, including triaging review feedback, CI failures, and routine follow-up."
disable-model-invocation: true
---

# Shepherd

## Core principle

Keep an authorized PR or MR moving with evidence, not noise: poll, act on new
actionable items, batch each target's local fixes into one push, then resolve
addressed threads. After a code-related CI failure, use full local verification
as the repair loop and CI only as confirmation. Never merge without explicit
authority.

Do not start persistent polling for a one-off inspection, no open targets, or an action requiring human judgment; report the state and stop.

## Procedure

1. Detect the platform with `git remote get-url origin`: use `gh` for GitHub and
   `glab` for GitLab. If it is ambiguous or unavailable, stop and ask.
2. Establish targets and a handled-ID snapshot. Every external comment, review,
   or thread absent from that snapshot is new, including pre-session feedback.
   After each poll record feedback IDs, CI state, and this controller's comments.
3. Before repeated polling, use one lowest-cost read-only evidence helper when
   available. Give it targets and the snapshot; require new feedback IDs, body,
   location, review state, non-manual CI state, failed jobs, and log references.
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
6. Handle each target in its own head checkout and batch every known actionable
   item. Until a code-related CI failure, validate proportionately. After one,
   inspect its evidence, run every locally available CI-equivalent check, fix all
   failures, and rerun the full local suite before one repair push. Report exact
   checks unavailable locally instead of using CI as an iterative test runner.
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

Continue until the user stops monitoring, every target is merged or closed, or an escalation is needed. Report the target, current CI/review state, actions taken, and the next required human decision. Escalate immediately for ambiguous platform/target selection, an unresolved conflict, material human judgment, conflicting reviewer direction, or a failure that remains after three repair cycles.
