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
  "projectStatus": "Ready to implement",
  "projectPriority": "High",
  "projectPosition": 17,
  "labels": ["ready-for-agent"],
  "assignees": [{"login": "octocat"}],
  "blockedBy": [41, "other/repository#7"],
  "openDescendants": [43],
  "planningTransition": {
    "id": "PVTE_planning",
    "actor": "maintainer",
    "createdAt": "2026-07-28T08:00:00Z",
    "status": "Planning",
    "wasAutomated": false
  },
  "readyTransition": {
    "id": "PVTE_ready",
    "actor": "octocat",
    "createdAt": "2026-07-28T10:00:00Z",
    "status": "Ready to implement",
    "wasAutomated": false
  },
  "implementationPlan": {
    "commentId": "IC_plan",
    "permalink": "https://github.com/owner/repository/issues/42#issuecomment-1",
    "author": "octocat",
    "digest": "sha256:plan-body",
    "createdAt": "2026-07-28T09:00:00Z",
    "updatedAt": "2026-07-28T09:00:00Z",
    "plannedBranch": "main",
    "plannedSha": "0123456789abcdef"
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

Use GitHub logins, never display names, for assignees, PR authors, and
transition actors. Normalize `labels` to exact label names. Normalize
`blockedBy` and `openDescendants` entries to integer issue numbers for the
configured repository or `owner/repository#number` strings for cross-repository
issues; never pass GraphQL objects. Use a finite non-negative numeric Project
position. An empty PR array is valid.

For a first-time or human-reauthorized `Planning` item, `readyTransition` may be
`null`. A runner-authored Planning requeue must include its preceding verified
Ready transition. For any other accepted Status it must be the latest
transition into `Ready to implement`. `planningTransition` is always the latest
event entering Planning; the ranker distinguishes human authorization from a
runner requeue by actor and the preceding Ready handoff.
`implementationPlan` may be `null`; when present it must represent the only
comment containing `<!-- to-plan:implementation-plan:v1 -->` and `author` must
be the authenticated runner's GitHub login.

The ranker returns valid current-user claims and ordered unclaimed candidates:

```json
{
  "claimLimit": 3,
  "blockedClaims": [
    {"number": 39, "reasons": ["missing ready-for-agent label"]}
  ],
  "blockedPlanningClaims": [
    {"number": 40, "reasons": ["missing current implementation plan"]}
  ],
  "claims": [
    {"ticket": {"number": 41}, "action": "resume-implementation"},
    {"ticket": {"number": 42}, "action": "resume-planning-handoff"}
  ],
  "candidates": [
    {"ticket": {"number": 43}, "action": "resume-pr"},
    {"ticket": {"number": 44}, "action": "claim"},
    {"ticket": {"number": 45}, "action": "plan"}
  ],
  "excluded": []
}
```

Treat each `ticket` as the complete normalized object shown above. The
controller owns scheduling; the ranker only validates claims and orders
candidates. Each `blockedClaims` entry occupies a slot and preserves a claimed
implementation ticket that requires reconciliation. Planning claims and
`blockedPlanningClaims` preserve ownership but do not consume an implementation
slot.
