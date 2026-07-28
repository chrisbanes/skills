# Normalized Ticket Schema

Provide every field below to `scripts/rank_tickets.py` from fresh, completely
paginated GitHub and Project reads:

```json
{
  "number": 42,
  "title": "Short title",
  "url": "https://github.com/owner/repository/issues/42",
  "state": "OPEN",
  "projectItemId": "PVTI_example",
  "projectStatus": "Ready",
  "projectPriority": "High",
  "projectPosition": 17,
  "assignees": [{"login": "octocat"}],
  "blockedBy": [41, "other/repository#7"],
  "openDescendants": [43],
  "readyTransition": {
    "id": "PVTE_example",
    "actor": "maintainer",
    "createdAt": "2026-07-28T10:00:00Z",
    "status": "Ready",
    "wasAutomated": false
  },
  "agentBrief": {
    "commentId": "IC_example",
    "digest": "sha256:...",
    "createdAt": "2026-07-28T09:00:00Z",
    "updatedAt": "2026-07-28T09:00:00Z"
  },
  "openPullRequests": [
    {
      "number": 91,
      "url": "https://github.com/owner/repository/pull/91",
      "author": "octocat",
      "closesIssue": true,
      "headRepository": "owner/repository",
      "headRefName": "cb/issue-42",
      "headSha": "0123456789abcdef",
      "baseRepository": "owner/repository",
      "baseRefName": "main",
      "isDraft": false
    }
  ]
}
```

Use GitHub logins, never display names, for assignees, PR authors, and Ready
actors. Normalize `blockedBy` and `openDescendants` entries to integer issue
numbers for the configured repository or `owner/repository#number` strings for
cross-repository issues; never pass GraphQL objects. Use a finite non-negative
numeric Project position. An empty PR array is valid.

The ranker returns valid current-user claims and ordered unclaimed candidates:

```json
{
  "claimLimit": 3,
  "blockedClaims": [
    {"number": 39, "reasons": ["assigned to current user while project status is still ready"]}
  ],
  "claims": [{"ticket": {"number": 40}, "action": "resume-pr"}],
  "candidates": [
    {"ticket": {"number": 41}, "action": "resume-pr"},
    {"ticket": {"number": 42}, "action": "claim"}
  ],
  "eligible": [40, 41, 42],
  "excluded": []
}
```

Treat each `ticket` as the complete normalized object shown above. The
controller owns scheduling; the ranker only validates claims and orders
candidates. Each `blockedClaims` entry occupies a slot and preserves a claimed
ticket that requires reconciliation.
