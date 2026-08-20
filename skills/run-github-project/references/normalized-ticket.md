# Normalized Ticket Schema

Provide every field below to `scripts/rank_tickets.py` from fresh, completely
paginated GitHub and Project reads. Use this shape for execution contenders:

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
  "backlogTransition": null,
  "readyTransition": {
    "id": "PVTE_ready",
    "actor": "octocat",
    "createdAt": "2026-07-28T10:00:00Z",
    "status": "Ready to implement",
    "wasAutomated": false
  },
  "replanRequest": null,
  "implementationPlans": [
    {
      "commentId": "IC_plan",
      "permalink": "https://github.com/owner/repository/issues/42#issuecomment-1",
      "author": "octocat",
      "digest": "sha256:plan-payload",
      "createdAt": "2026-07-28T09:00:00Z",
      "publishedAt": "2026-07-28T09:00:00Z",
      "updatedAt": "2026-07-28T09:00:00Z",
      "plannedBranch": "main",
      "plannedSha": "0123456789abcdef",
      "markerVersion": 2,
      "revision": 1,
      "supersedes": null,
      "replanRequest": null,
      "isMinimized": false
    }
  ],
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

When Wayfinder is enabled, a configured Wayfinder child uses the Planning
shape above plus its direct parent and, for a task, its controller-derived mode:

```json
{
  "parentIssue": {
    "number": 7,
    "state": "OPEN",
    "labels": ["wayfinder:map"]
  },
  "labels": ["wayfinder:research"],
  "readyTransition": null,
  "implementationPlans": [],
  "wayfinderTaskMode": null,
  "wayfinderAfkEvidence": null
}
```

The parent must be the direct map parent, not an inferred ancestor. Use exactly
one configured type label. Research is AFK; prototype and grilling are HITL.
For a task, use `"afk"` only with non-empty fresh evidence that every action is
safely autonomous; use `"hitl"` or `null` for a human or ambiguous task.
Wayfinder children require the schema fields above, but not a Ready transition
or any implementation-plan entries.

For an interrupted terminal reconciliation, add the normalized authoritative
marker below. Recovery inventory may supply a closed child, a closed parent,
and a Project item in Done or archived; it must still use fresh values and the
exact recorded Project item node ID.

```json
{
  "wayfinderReconciliation": {
    "commentId": "IC_reconciliation",
    "permalink": "https://github.com/owner/repository/issues/52#issuecomment-2",
    "author": "octocat",
    "createdAt": "2026-07-28T09:00:00Z",
    "markerVersion": 1,
    "disposition": "resolved",
    "mapNumber": 7,
    "projectItemId": "PVTI_example",
    "outcomePermalink": "https://github.com/owner/repository/issues/52#issuecomment-1",
    "configurationDigest": "sha256:configuration",
    "planDigest": "sha256:semantic-reconciliation-plan"
  }
}
```

The comment body retains the full planned-mutation list; the normalized form
contains the identifiers and digests the ranker validates. The marker must be
runner-authored, match the child Project item and direct map parent, match the
`--configuration-digest` passed for this invocation, and remain assigned only
to that runner. Such a claim returns
`resume-wayfinder-reconciliation` before new Wayfinder work.
Use `resolved` only for a decision on the route and `out-of-scope` only for a
scope disposition. The recorded plan must place their linked gists in
`Decisions so far` and `Out of scope`, respectively.

Use the same canonical shape for Backlog triage contenders, with transition and
replan fields set to `null` and `implementationPlans` empty when absent. Backlog
`openPullRequests` entries need only `number`, `url`, and `closesIssue`; omit
execution-only author, draft, head, and base fields:

```json
{
  "number": 43,
  "title": "Unblocked issue awaiting triage",
  "url": "https://github.com/owner/repository/issues/43",
  "state": "OPEN",
  "projectItemId": "PVTI_backlog",
  "projectStatus": "Backlog",
  "projectPriority": "High",
  "projectPosition": 18,
  "labels": ["needs-triage"],
  "assignees": [],
  "blockedBy": [],
  "openDescendants": [],
  "backlogTransition": null,
  "planningTransition": null,
  "readyTransition": null,
  "replanRequest": null,
  "implementationPlans": [],
  "openPullRequests": []
}
```

Use that same Backlog shape for configured epics, human work, and
`ready-for-agent` items awaiting Planning authorization. Preserve every exact
label. The ranker derives the work shape and next action from configured label
names; never add a synthetic role to its input.

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
runner requeue by actor, the preceding Ready handoff, and `replanRequest`.

Use `backlogTransition` only for an item currently in Backlog. It must be the
latest transition into Backlog. An assigned Backlog item also requires a
runner-authored `replanRequest` with `disposition: "human-required"` so cleanup
can resume after interruption. Keep that assignment as the durable cleanup
lease until the controller verifies that every exact runner-owned artifact is
absent and unassigns last. An unassigned Backlog item without the configured
`needs-triage` label is human-owned and ineligible for runner execution; an
eligible labeled item belongs only to the triage inventory.

Normalize every runner-owned v1 or v2 plan marker, including minimized
comments, into `implementationPlans`. A v1 comment is a revision-one root. A v2
comment records its positive `revision`, predecessor permalink in
`supersedes`, triggering report permalink in `replanRequest` when applicable,
and payload publication time in `publishedAt`. Compute `digest` from the
semantic plan payload, excluding any superseded banner or `<details>` wrapper,
so presentation-only edits do not invalidate history.

Require one root, contiguous revisions, one child per revision, and one
unminimized leaf. The ranker returns that leaf as the synthesized
`implementationPlan` in each selected ticket. Reject forks, gaps, duplicate
revisions, missing predecessors, foreign marker authors, and a minimized active
leaf. For compatibility, the ranker also accepts the former singular
`implementationPlan` input as one v1 root.

For an automatic requeue, normalize the verified report comment as:

```json
{
  "commentId": "IC_replan",
  "permalink": "https://github.com/owner/repository/issues/42#issuecomment-2",
  "author": "octocat",
  "createdAt": "2026-07-28T11:00:00Z",
  "disposition": "autonomous-replan",
  "previousPlanPermalink": "https://github.com/owner/repository/issues/42#issuecomment-1",
  "previousPlanDigest": "sha256:plan-payload",
  "baseSha": "0123456789abcdef",
  "implementationHeadSha": "fedcba9876543210",
  "pullRequestUrl": null
}
```

Use `human-required` instead of `autonomous-replan` for the Backlog path.
Retained head and PR fields may be null but must identify exact durable state
when present. The report must precede the resulting Status transition and
identify the plan that authorized the prior Ready handoff.

For Backlog triage contenders, the ranker ignores historical Planning, Ready,
and plan fields. Require the configured `needs-triage` label, no assignee, and
no open implementation pull request. Return an otherwise valid item with open
native blockers or descendants as `parkedBlocked`; return an unblocked item as
`triageCandidates`. Never feed either collection into an implementation slot.

For other unassigned Backlog work, apply
[Epics And Human Frontier](human-frontier.md). Return a bare unblocked epic as
`readyEpics`, and return unblocked human work or agent work awaiting Planning
as `humanActions`. Permit an existing assignee only on human work. Role-tag
every dependency-blocked Backlog result in `parkedBlocked`.

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
    {"ticket": {"number": 42}, "action": "resume-planning-handoff"},
    {"ticket": {"number": 43}, "action": "resume-backlog-cleanup"}
  ],
  "candidates": [
    {"ticket": {"number": 44}, "action": "resume-pr"},
    {"ticket": {"number": 45}, "action": "claim"},
    {"ticket": {"number": 46}, "action": "plan"}
  ],
  "wayfinderHumanFrontier": [
    {"ticket": {"number": 52}, "action": "resolve-wayfinder-hitl", "type": "grilling"}
  ],
  "wayfinderClaimedHitl": [
    {"ticket": {"number": 53}, "action": "resume-wayfinder-hitl", "type": "prototype"}
  ],
  "triageCandidates": [
    {"ticket": {"number": 47}, "action": "triage"}
  ],
  "readyEpics": [
    {"ticket": {"number": 48}, "action": "close-epic"}
  ],
  "humanActions": [
    {"ticket": {"number": 49}, "action": "move-to-planning"},
    {"ticket": {"number": 50}, "action": "perform-human-work"}
  ],
  "parkedBlocked": [
    {
      "ticket": {"number": 51},
      "role": "human-epic",
      "reasons": ["blocked by ['owner/repository#41']"]
    }
  ],
  "excluded": []
}
```

Treat each `ticket` as the complete normalized object shown above. The
controller owns scheduling; the ranker only validates claims and orders
candidates. Each `blockedClaims` entry occupies a slot and preserves a claimed
implementation ticket that requires reconciliation. Planning claims and
`blockedPlanningClaims` preserve ownership but do not consume an implementation
slot; both still prevent the Backlog triage tail from starting. Ready epics and
human actions consume neither slots nor agent capacity. Triage
`resume-backlog-cleanup` also consumes no implementation slot, must finish
before new claims, and prevents the triage tail from starting. Its cleanup is
idempotent: already-absent owned artifacts satisfy their individual finish
checks, but the assignment remains until the complete cleanup state is
verified. Triage candidates are ordered separately and run only through
[Backlog Triage Lane](triage-lane.md). Process ready epics and human actions
through [Epics And Human Frontier](human-frontier.md); Backlog `parkedBlocked`
items consume neither a slot nor an agent.

When enabled in `next`, the ranker emits any eligible Wayfinder candidate as
`wayfind` and an assigned one as `resume-wayfind`. In `drain`, it emits only AFK
work in those collections and returns configured prototype, grilling, HITL,
and ambiguous task children in `wayfinderHumanFrontier` only while unassigned,
ordered by Priority, position, and issue number. It returns assigned eligible
HITL children separately in `wayfinderClaimedHitl`. A terminal recovery is
always an assigned `resume-wayfinder-reconciliation` claim. All are Planning
work and consume no implementation slot. Route every form through
[Wayfinder Planning Lane](wayfinder-lane.md).

When `--wayfinder-ticket` is present in `next`, the output includes
`selectedWayfinderTicket` and returns only that child as new work. The ranker
rejects an absent or ineligible child, use in `drain`, and any selection that
would bypass another current-user claim.

Every human-facing consumer must render the complete ticket as
`[title](url)`. The abbreviated number-only objects above illustrate collection
shape, not permitted narration.

Before invoking the ranker, apply the drain scheduler's
[Terminal Required-CI Parking](drain-scheduler.md#terminal-required-ci-parking)
contract. Keep a parked implementation claim with an unchanged verified
observation fingerprint outside the normalized array and `max-claims` count. A
changed observation fingerprint triggers deep hydration but does not by itself
resume the claim or reset its repair budget. This inventory is distinct from
`blockedClaims` and Backlog `parkedBlocked`; it blocks triage and successful
drain completion without occupying an implementation slot.
