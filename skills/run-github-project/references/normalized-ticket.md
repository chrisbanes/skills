# Normalized Ticket Schema

## Ranker Invocation

Write the fresh normalized tickets as one JSON array, then run:

```text
python3 <skill-dir>/scripts/rank_tickets.py \
  --mode <next-or-drain> \
  [--wayfinder-ticket <explicit-user-selected-child-number>] \
  --current-user <github-login> \
  --repository <owner/repository> \
  --configuration-digest <committed-configuration-digest> \
  --base-branch <base-branch> \
  --issue-closure <closing-keyword-or-close-after-merge> \
  --backlog-status <backlog-name> \
  --planning-status <todo-name> \
  --ready-status <ready-to-implement-name> \
  --in-progress-status <in-progress-name> \
  --done-status <done-name> \
  --needs-triage-label <needs-triage-label> \
  --epic-label <epic-label> \
  --human-work-label <human-work-label> \
  --wayfinder-map-label <wayfinder:map-label> \
  --wayfinder-research-label <wayfinder:research-label> \
  --wayfinder-prototype-label <wayfinder:prototype-label> \
  --wayfinder-grilling-label <wayfinder:grilling-label> \
  --wayfinder-task-label <wayfinder:task-label> \
  --priority <highest-name> [--priority <next-name> ...] \
  --max-claims <mode-slot-limit> \
  < normalized-tickets.json
```

In `next`, add `--wayfinder-ticket` only for an explicitly selected eligible
child. Pass all five Wayfinder label options only for a complete enabled
configuration; otherwise omit all five.

Use configured Status and Priority display names, not option IDs; use IDs only
for Project mutations. Preserve GitHub logins, rank an unset Priority last, and
reject non-finite Project positions. Run `--help` if the installed script's
interface is uncertain rather than guessing an option. `--max-claims` accepts
any positive integer; pass the controller's effective implementation-slot
limit. Agent capacity is a separate dispatch constraint. Blocked implementation
claims still count toward this limit; planner/handoff claims do not.

Provide every field below to `scripts/rank_tickets.py` from fresh, completely
paginated GitHub and Project reads. Before dispatch ranking, the controller
recovers [authority pauses](authority-and-pauses.md#recover-and-resume) and
retains active verified pauses in its separate frontier, outside the ranker's
active claims/candidates, as for parked CI claims. Apply the controller's
[readiness preflight](execution-controller.md#unattended-readiness) before
dispatch; the ranker does not inspect external access, host capabilities,
qualification receipts or execution grants. Keep those observations in existing
controller records, not invented CLI fields. Preserve unknown or unavailable
prerequisites as dispatch blockers even when the ranker returns a candidate.
Keep every paused issue in
the complete dependency graph used to hydrate blockers and descendants; never
erase a blocker to make a dependent runnable. Do not invent an authority flag
or pause field for this ranker CLI. Use this shape for execution contenders:

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
      "linksIssue": true,
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

When Wayfinder is enabled, a configured Wayfinder child uses the Todo
shape above plus its direct parent and, for a task, its controller-derived mode:

```json
{
  "parentIssue": {
    "number": 7,
    "state": "OPEN",
    "projectStatus": "Todo",
    "labels": ["wayfinder:map"]
  },
  "labels": ["wayfinder:research"],
  "implementationPlans": [],
  "wayfinderTaskMode": null,
  "wayfinderAfkEvidence": null
}
```

The parent must be the direct map parent, not an inferred ancestor. Hydrate its
current Project Status too; require a configured Todo-or-later column for the
parent before automatic map work or recovery. Missing, unknown, and Backlog
parent Status block the child; a child's column never authorizes its map.
Use exactly
one configured type label. Research is AFK; prototype and grilling are HITL.
For a task, use `"afk"` only with non-empty fresh evidence that every action is
safely autonomous; use `"hitl"` or `null` for a human or ambiguous task.
Wayfinder children require the schema fields above, but no implementation-plan
entries or transition-history fields.

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
`--configuration-digest` passed for this invocation (or carry the exact verified
renewal below), and remain assigned only to that runner. Such a claim returns
`resume-wayfinder-reconciliation` before new Wayfinder work.
Use `resolved` only for a decision on the route and `out-of-scope` only for a
scope disposition. The recorded plan must place their linked gists in
`Decisions so far` and `Out of scope`, respectively.

### Wayfinder Configuration Renewal

Only after the controller verifies
[presentation-only renewal](project-config.md#renew-presentation-only-configuration),
include these optional fields inside `wayfinderReconciliation`:

```json
{
  "payloadDigest": "sha256:original-marker-payload",
  "configurationRenewal": {
    "commentId": "IC_renewal",
    "permalink": "https://github.com/owner/repository/issues/52#issuecomment-3",
    "author": "octocat",
    "markerCommentId": "IC_reconciliation",
    "markerPermalink": "https://github.com/owner/repository/issues/52#issuecomment-2",
    "markerPayloadDigest": "sha256:original-marker-payload",
    "originalConfigurationDigest": "sha256:configuration",
    "configurationDigest": "sha256:renewed-configuration"
  }
}
```

Keep the marker's original `configurationDigest` unchanged. Compute
`payloadDigest` from its freshly read semantic payload, excluding only a
presentation wrapper; retain every identity, configuration value and planned
mutation. The normalized renewal binds that payload, comment ID and permalink
to its original digest and the current CLI configuration digest. Require all
fields nonempty and its author to be the authenticated runner. A supplied
malformed, foreign, stale or mismatched renewal blocks recovery even when the
marker already has the current digest; omit renewal entirely when unnecessary.
Without renewal the original exact-digest rule is unchanged.

The controller must verify the durable record and full unforked renewal lineage,
committed semantic equivalence and live authority before normalization. For
repeated renames, supply the latest verified original-marker-to-current binding
only after verifying every intervening renewal and predecessor. The ranker
checks normalized identity consistency; it does not authenticate comments,
compare configuration semantics or grant access.

## Other Ticket Shapes And Plan State

Use the same canonical shape for Todo triage contenders, with `replanRequest`
set to `null` and `implementationPlans` empty when absent. Their
`openPullRequests` entries need only `number`, `url`, and `closesIssue`; omit
execution-only author, draft, head, and base fields:

```json
{
  "number": 43,
  "title": "Unblocked issue awaiting triage",
  "url": "https://github.com/owner/repository/issues/43",
  "state": "OPEN",
  "projectItemId": "PVTI_triage",
  "projectStatus": "Todo",
  "projectPriority": "High",
  "projectPosition": 18,
  "labels": ["needs-triage"],
  "assignees": [],
  "blockedBy": [],
  "openDescendants": [],
  "replanRequest": null,
  "implementationPlans": [],
  "openPullRequests": []
}
```

Use that same Todo shape for configured epics, human work, and
`ready-for-agent` items already queued for planning. Preserve every exact
label. The ranker derives the work shape and next action from configured label
names; never add a synthetic role to its input.

Use GitHub logins, never display names, for assignees and PR authors. Normalize `labels` to exact label names. Normalize
`blockedBy` and `openDescendants` entries to integer issue numbers for the
configured repository or `owner/repository#number` strings for cross-repository
issues; never pass GraphQL objects. Use a finite non-negative numeric Project
position. An empty PR array is valid.

Set `linksIssue` only from a freshly verified exact issue link in the PR; absent
or ambiguous evidence is false. Closing PRs already prove that link and may omit
the field. Under `close-after-merge`, a non-closing PR requires `linksIssue: true`
to resume; a branch name or historical report alone is insufficient. Keep all
other open implementation PRs in the array as competitors. The ranker defaults
to `closing-keyword` for compatibility; pass the binding's policy explicitly.

Current Project Status supplies ticket authorization. Do not hydrate status
history. `planningTransition`, `readyTransition`, and `backlogTransition` are
obsolete inputs: omit them; legacy values are ignored even when malformed,
foreign, automated, or missing. Check usable active-plan integrity and the
configured base rather than comparing publication times with column events.

Backlog items are always excluded from dispatch, including assigned items with
old cleanup reports, PRs, or Wayfinder reconciliation markers. Never place
Backlog work in claims, planning candidates, triage candidates, ready epics,
human actions, or automatic cleanup. Keep its dependency edges in the complete
live graph and report interrupted artifacts for human handling.

Hydrate every comment containing `<!-- to-plan:implementation-plan:v1 -->` or
`<!-- to-plan:implementation-plan:v2 -->`, including minimized comments, and
normalize it into `implementationPlans`. Require runner authorship. A v1
comment is a revision-one root. A v2
comment records its positive `revision`, predecessor permalink in
`supersedes`, triggering report permalink in `replanRequest` when applicable,
and payload publication time in `publishedAt`. Compute `digest` from the
semantic plan payload, excluding any superseded banner or `<details>` wrapper,
so presentation-only edits do not invalidate history.

Require one root, contiguous revisions, one child per revision, and one
unminimized leaf. The ranker returns that leaf as the synthesized
`implementationPlan` in each selected ticket. Reject forks, gaps, duplicate
revisions, missing predecessors, foreign marker authors, and a minimized active
leaf. A verified runner-authored `autonomous-replan` report naming a plan's exact
permalink and payload digest invalidates that predecessor in every execution
column until a later revision links the report. Todo may plan its replacement;
Ready and In-progress work remain blocked. For compatibility, the ranker also accepts the former singular
`implementationPlan` input as one v1 root.

An integration amendment is not a synthetic implementation-plan revision or
ranker input field. Keep the original marked plan in `implementationPlans`;
the controller separately enforces the
[effective-contract gate](todo-lane.md#consume-a-verified-integration-amendment)
before dispatch, on recovery and before writes. Persist its verified lineage,
base/candidate identities and delivery evidence alongside the authority lease.
Unverified or unsupported amendments cannot make an otherwise blocked plan
usable, and a ranker selection cannot validate an amendment.

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

A pending `human-required` decision stays in its original eligible column
under a verified authority pause, outside dispatch ranking. Explicit
abandonment cleanup must finish before a final transfer to Backlog; never
recover cleanup there. Retained head and PR fields may be null but must identify
exact durable state when present. The replan report identifies its predecessor
plan and retained artifacts; no column-event ordering is required.

For Todo triage contenders, require the configured `needs-triage` label, no
assignee, and no open implementation pull request. Return an otherwise valid
item with open native blockers or descendants as `parkedBlocked`; return an
unblocked item as `triageCandidates`. Neither consumes an implementation slot.

For other role-labelled Todo work, apply
[Epics And Human Frontier](human-frontier.md). Return a bare unblocked epic as
`readyEpics`, unblocked human work as `humanActions`, and unblocked
`ready-for-agent` work in `candidates` with action `plan`. Permit an existing
assignee only on human work. Role-tag dependency-blocked Todo results in
`parkedBlocked`. Never infer a human promotion from labels on a Backlog item.

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
    {"ticket": {"number": 44}, "action": "resume-pr"},
    {"ticket": {"number": 45}, "action": "claim"},
    {"ticket": {"number": 46}, "action": "plan"},
    {"ticket": {"number": 49}, "action": "plan"}
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
implementation ticket that requires reconciliation. Todo claims and
`blockedPlanningClaims` preserve ownership but do not consume an implementation
slot; both still prevent the Todo triage tail from starting. Ready epics and
human actions consume neither slots nor agent capacity. Triage candidates are
ordered separately and run only through [Todo Triage Lane](triage-lane.md).
Process ready epics and human actions through
[Epics And Human Frontier](human-frontier.md); Todo `parkedBlocked` items consume
neither a slot nor an agent. No Backlog cleanup action is emitted.

When enabled in `next`, the ranker emits any eligible Wayfinder candidate as
`wayfind` and an assigned one as `resume-wayfind`. In `drain`, it emits only AFK
work in those collections and returns configured prototype, grilling, HITL,
and ambiguous task children in `wayfinderHumanFrontier` only while unassigned,
ordered by Priority, position, and issue number. It returns assigned eligible
HITL children separately in `wayfinderClaimedHitl`. A terminal recovery is
always an assigned `resume-wayfinder-reconciliation` claim in a configured
Todo-or-later column, including Done for interrupted terminal reconciliation.
New Wayfinder work requires Todo. None consumes an implementation slot. Route every form through
[Wayfinder Todo Lane](wayfinder-lane.md).

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
`blockedClaims` and Todo `parkedBlocked`; it blocks triage and successful
drain completion without occupying an implementation slot.
