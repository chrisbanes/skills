# Issue tracker

Issues and specs live in GitHub Issues for `chrisbanes/skills`. Use the GitHub connector when it supports the operation. Run `gh` outside the sandbox for the remaining operations.

## Ticket operations

- **Fetch a ticket.** Read the issue body, labels, and comments. CLI: `gh issue view <number> -R chrisbanes/skills --json number,title,body,labels,comments`.
- **List tickets.** Filter by state and label as needed. CLI: `gh issue list -R chrisbanes/skills --state open`.
- **Publish to the issue tracker.** Create a GitHub issue in `chrisbanes/skills`. For the CLI, save the intended body to a temporary file and run `gh issue create -R chrisbanes/skills --title "<title>" --body-file <path>`.
- **Update a ticket.** Keep its current status in the issue body and preserve the original problem, acceptance criteria, and approval records. Use comments for decisions, findings, and discussion. For triage, use the [label mapping](triage-labels.md).
- **Create a sub-issue.** Link the child to its parent with GitHub's sub-issue relationship. If unavailable, list the child in the parent's task list and add `Part of #<parent>` to the child.
- **Record a blocker.** Use GitHub's native issue dependencies. If unavailable, add `Blocked by: #<number>` to the blocked issue. A ticket can start once all its blockers are closed.
- **Close a ticket.** Record the reason in a comment, then close the issue.

## Pull requests as a triage surface

**PRs as a request surface: no.** If this is set to `yes`, apply the issue triage workflow to external PRs using their descriptions, comments, and diffs.

## Wayfinding operations

- Create a GitHub issue with the `wayfinder:map` label for the map. Keep notes, decisions, and open questions in its body.
- Link tickets as sub-issues and label them `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task`.
- Pick the first open, unassigned child in map order whose blockers are closed. Assign it to the developer before starting.
- Record the resolution on the child, close it, and link the resulting context from the map.
