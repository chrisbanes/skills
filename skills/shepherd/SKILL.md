---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests, including triaging review feedback, CI failures, and routine follow-up."
---

# Shepherd

## Core principle

Keep an authorized PR or MR moving with evidence, not noise: poll, act on every actionable item, batch each target's local fixes into one push, then resolve addressed threads. Never merge without explicit authority.

Do not start persistent polling for a one-off inspection, no open targets, or an action requiring human judgment; report the state and stop.

## Procedure

1. Detect the platform with `git remote get-url origin`. Use `gh` for a remote containing `github.com`; use `glab` for one containing `gitlab`. If detection is ambiguous or unavailable, stop and ask.
2. Establish the target PRs/MRs. Start with an explicit handled-ID snapshot if one exists; otherwise use an empty snapshot. Treat every external comment, review, and thread absent from it as unprocessed, including feedback that predates this session. Record the resulting IDs, CI state, and your own comments after each poll.
3. Before repeated polling, attempt to dispatch one lowest-cost available read-only **evidence-helper subagent**. Give it the targets and last-seen snapshot; require it to return each new feedback item's ID, body, and location, plus approval/request state, non-manual CI state, failed job names, and log references. Prohibit local or remote mutation. If no such subagent or cost control is available, poll directly. Keep triage, code changes, replies, pushes, thread resolution, retries, and merging with the authorized controller.
4. Poll the target(s), using that helper when dispatched:
   - GitHub: `gh pr list`, `gh pr view <number> --json comments,reviews,reviewDecision,statusCheckRollup`, `gh pr checks <number>`, and `gh run view <run-id> --log-failed`. When inline review-thread IDs are needed to reply or resolve, query the PR's `reviewThreads` through `gh api graphql`.
   - GitLab: `glab mr list --source-branch $(git branch --show-current) --output json`, `glab mr view <iid> --comments`, `glab ci list --mr <iid>`, and `glab ci trace <job-id>`.
   Compare comments, review state, and CI with the saved snapshot. Do not reprocess old feedback or post a polling update.
5. Triage all new feedback before changing remote state. Fix clear requested changes, formatting, lint, compile failures, and obvious test fixes. Answer clear questions in the relevant thread. Escalate architectural or contradictory feedback, unfamiliar failures, non-obvious test fixes, and conflicts outside the changed work. Treat GitLab manual jobs as non-blocking unless instructed otherwise.
6. Process each target independently: use that target's head checkout, batch and validate every actionable local fix, then push that target once. Reply to each addressed thread where supported (otherwise leave one concise PR/MR comment); resolve a thread only after its reply and the push both succeed. Do not combine fixes from different heads, push after every comment, resolve a local-only fix, or comment when nothing changed.
7. Recheck CI after a push. For a clear failure, inspect its log, reproduce or verify the narrow fix when practical, and return to step 6. Retry a suspected flaky job once, using `glab ci retry <job-id>` on GitLab; if it fails again, report it. If checks are pending, poll every 2–5 minutes; while actively fixing, poll every 30–60 seconds; back off to 10+ minutes after several unchanged cycles.
8. Merge only when requirements and CI are green, conflicts are absent, and the user granted explicit merge authority (or standing authority applies). Use `gh pr merge <number> --squash --delete-branch` or `glab mr merge <iid> --squash` as appropriate. Do not infer authority from an approval.

## Finish or escalate

Continue until the user stops monitoring, every target is merged or closed, or an escalation is needed. Report the target, current CI/review state, actions taken, and the next required human decision. Escalate immediately for ambiguous platform/target selection, an unresolved conflict, material human judgment, conflicting reviewer direction, or a failure that remains after three repair cycles.

## Scenario checks

- **Green:** With no handled snapshot, shepherd begins after a `REQUESTED_CHANGES` review, two inline comments, and a failed lint job already exist. The structured evidence response returns that feedback and failure; the controller fixes both comments locally, runs lint, makes one push, replies and resolves only after the push succeeds, then waits for CI.
- **Red:** The evidence helper sees `APPROVED` while CI is still running. Do not merge, push, resolve unrelated threads, or post a status-only comment; keep monitoring until the merge gate is actually met.
- **Counterexample:** A user asks for a one-off PR status or there are no open targets. Report the state; do not dispatch a helper or start the polling loop.
