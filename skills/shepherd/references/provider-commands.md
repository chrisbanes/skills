# Provider Commands

Use these read commands when the platform-specific API is otherwise unclear.

| Platform | Target and feedback | Checks and logs |
| --- | --- | --- |
| GitHub | `gh pr list`; `gh pr view <number> --json comments,reviews,reviewDecision,statusCheckRollup`; query `reviewThreads` with `gh api graphql` during every poll to discover inline feedback and resolution state | `gh pr checks <number>`; `gh run view <run-id> --log-failed` |
| GitLab | `glab mr list --source-branch $(git branch --show-current) --output json`; `glab mr view <iid> --comments` | `glab ci list --mr <iid>`; `glab ci trace <job-id>` |

Use `glab ci retry <job-id>` only for the one permitted suspected-flake retry.
