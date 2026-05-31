---
name: shepherd
description: "Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests — including triaging review comments, detecting CI failures, fixing trivial CI issues, and keeping PRs/MRs moving without manual intervention."
---

# Shepherd

## Core principle

Poll open PRs (GitHub) and MRs (GitLab) in a loop, triage events by type, act on what you can fix, and report what you can't. Never sit idle when a PR has unaddressed feedback or a failing CI check.

## Platform detection

Use `git remote get-url origin` to determine the platform:

| Remote URL pattern | Platform | CLI tool | ID prefix |
|---|---|---|---|
| `github.com` | GitHub | `gh` | `#` |
| `gitlab.*` | GitLab | `glab` | `!` |

Use the detected CLI tool (`gh` or `glab`) for all commands below. The skill uses `PR` generically for both pull requests and merge requests.

## Command reference

| Operation | GitHub (`gh`) | GitLab (`glab`) |
|---|---|---|
| List open PRs | `gh pr list --state open --json number,title,headRepository,baseRefName,statusCheckRollup` | `glab mr list --source-branch $(git branch --show-current) --output json` |
| View PR details | `gh pr view <#> --comments --json comments` | `glab mr view <!> --comments` |
| Check CI status | `gh pr checks <#>` | `glab mr view <!>` (check `pipeline` or `head_pipeline` fields) |
| View CI logs | `gh run view <run-id> --log-failed` | `glab ci trace <job-id>` |
| List CI pipelines | — | `glab ci list --mr <!>` |
| Add comment | `gh pr comment <#> --body "..."` | `glab mr note <!> --message "..."` |
| Merge | `gh pr merge <#> --squash --delete-branch` | `glab mr merge <!> --squash` |
| Approve | `gh pr review <#> --approve` | `glab mr approve <!>` |

## When to use

- User says "shepherd my PRs", "babysit my PRs", "watch my PRs", "monitor open PRs", or "poll PRs" — applies to GitHub PRs and GitLab MRs interchangeably
- User has open PRs that need ongoing attention across minutes or hours
- You're asked to handle PR review feedback autonomously
- CI keeps failing on issues you can fix (lint, format, minor test breakage)

**Do NOT use when:**
- The failure requires domain knowledge you don't have (ambiguous test failure, architectural feedback)
- The user explicitly says to do something else first
- There are no open PRs to shepherd

## Core loop

```
Detect platform: git remote get-url origin
While the user wants monitoring:
  1. List open PRs (see command reference)
  2. For each PR:
     a. Check for new comments
     b. Triage comments (see Comment Triage below)
     c. Check CI (see CI Fix Workflow below)
     d. If CI failing, follow CI Fix Workflow
     e. If changes pushed and CI green, comment "ready for re-review" if requested
  3. Wait an appropriate interval before polling again
```

## Polling interval

- **30-60 seconds** when actively fixing issues
- **2-5 minutes** when all PRs are waiting on review / CI is running
- **10+ minutes** when PRs have no new activity for several cycles

Track which comments you've already seen to avoid re-processing. Compare against your last poll's comment set (timestamps/IDs).

## Comment triage

| Comment type | Signal | Action |
|---|---|---|
| Approval / LGTM | "LGTM", "ship it", `APPROVED` review / GitLab approval | Check CI is green, then offer to merge or merge if instructed |
| Change request | "please change", "request changes", `REQUEST_CHANGES` | Read the specific feedback, implement changes, push, comment "addressed" |
| Nit / suggestion | "nit", "optional", "consider" | Apply if trivial (rename, formatting). Skip if debatable — ask user |
| Question | "why", "what about", "did you consider" | Answer the question. If unsure, relay to user |
| CI reminder | "tests failing", "CI is red", "pipeline failed" | Follow CI Fix Workflow below |
| Merge conflict | "needs rebase", "conflicts" | Rebase on base branch, push. If conflicts are complex, report to user |

**Commenting rules:**
- Do NOT comment just to say "polling" or "checking in" — those are noise
- Do NOT comment if nothing has changed since your last comment
- Batch related responses into a single comment
- When pushing fixes, include `[autofix]` prefix so humans can spot automated pushes

## CI Fix Workflow

```
1. Check CI status (see command reference)
2. Identify failing check(s) or job(s)
3. If pipeline is still running, wait for completion
4. For each failure:
   a. Get logs (see command reference)
   b. Diagnose root cause:
      - Lint failure? Run the linter locally, fix formatting, push
      - Compilation error? Can you see the error clearly? Fix and push
      - Test failure? Read the test output. Only fix if the fix is obvious
      - Flaky test? Re-run once. If it fails again, report to user
   c. If fix is straightforward (≤ 3 lines, obvious intent):
      - Make the fix
      - Push with message "ci: fix [what was fixed]"
      - Re-check CI
   d. If fix is not obvious:
      - DO NOT guess
      - Report to user with the failure log snippet and your assessment
5. If no failures remain, mark CI as resolved
```

### GitLab CI specifics

GitLab pipelines are structured as stages → jobs. Use:

```
glab ci list --mr <!>           # list pipeline jobs
glab ci trace <job-id>          # view job logs
glab ci retry <job-id>          # retry a failed job
```

GitLab CI may have manual stages (environments, deployments). Only act on automatic stages; skip manual ones unless instructed.

## Merging

Only merge when:
- All requested reviewers have approved (or review requirement is met)
- All CI checks are green
- No merge conflicts
- User gave explicit merge permission OR you have standing merge authority

| Platform | Merge command |
|---|---|
| GitHub | `gh pr merge <#> --squash --delete-branch` |
| GitLab | `glab mr merge <!> --squash` |

For GitLab, if "Delete source branch" is not a project default, add `--remove-source-branch`.

## Resolving complexity

| Complex PRs (many files, large diff) | Simple PRs (small change, clear intent) |
|---|---|
| Look for split opportunities (can this be 2-3 smaller PRs?) | Merge quickly after approval + green CI |
| Pay extra attention to review feedback — harder to re-review | Fix CI failures aggressively |
| Log what you checked so user can scan | Default: merge yourself |

## Stop conditions

Stop polling and report to user when:
- User returns / says to stop
- All PRs merged or closed
- A CI failure repeats 3 cycles without resolution
- A comment requires human judgment you don't have
- You detect a merge conflict you can't resolve cleanly

## Common mistakes

| Mistake | Fix |
|---|---|
| Polling once and stopping | The core of this skill is the LOOP. Keep going unless a stop condition fires. |
| Commenting "I checked, everything looks good" every cycle | Only comment when you took action or when asked for status. |
| Merging after approval without checking CI | Approval ≠ ready to merge. Always check CI first. |
| Fixing a test you don't understand | "Obvious fix" means you can explain WHY. If you can't, don't fix. |
| Re-pushing without addressing all feedback | Triage ALL unaddressed comments before pushing. |
| Using the wrong CLI tool | Detect platform first (see Platform detection). |
| Not tracking which comments are new | Compare against your last poll's comment timestamps/IDs. Don't re-answer old comments. |
| Treating GitLab manual jobs as failures | Skip manual stages (deploy, review apps). Only act on automatic CI failures. |

## Red Flags — STOP and ask user

- CI failure log is >50 lines of unfamiliar code
- A reviewer asks for an architectural change
- You've pushed 3+ fix commits and CI still fails
- A comment contradicts another reviewer
- Merge conflicts involve files you didn't originally touch
- User said "stay on this" or "stop" — their word overrides this skill
- Platform detection fails or returns ambiguous results (multiple remotes, self-hosted both)
