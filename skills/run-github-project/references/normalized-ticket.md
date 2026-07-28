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
  "blockedBy": [],
  "openDescendants": [],
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
actors. Use a finite non-negative numeric Project position. An empty PR array
is valid.
