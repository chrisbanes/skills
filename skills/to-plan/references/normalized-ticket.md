# Normalized Ticket Schema

## Ranker Invocation

Write the fresh normalized tickets as one JSON array, then run:

```text
python3 <skill-dir>/scripts/rank_tickets.py \
  --mode <next-or-drain> \
  [--wayfinder-ticket <explicit-user-selected-child-number>] \
  --current-user <runner-identity> \
  --repository <owner/repository> \
  --configuration-digest <effective-binding-fingerprint> \
  --base-branch <base-branch> \
  --issue-closure <closing-keyword-or-close-after-merge> \
  --planning-status <todo-name> \
  --in-progress-status <in-progress-name> \
  [--candidate-order <action-priority-or-scope-position>] \
  --claim-marker '<binding-claim-marker-json>' \
  --done-status <done-name> \
  --agent-work-label <agent-work-label> \
  --needs-triage-label <needs-triage-label> \
  --epic-label <epic-label> \
  --human-work-label <human-work-label> \
  --wayfinder-map-label <wayfinder:map-label> \
  --wayfinder-research-label <wayfinder:research-label> \
  --wayfinder-prototype-label <wayfinder:prototype-label> \
  --wayfinder-grilling-label <wayfinder:grilling-label> \
  --wayfinder-task-label <wayfinder:task-label> \
  [--priority <highest-name>] [--priority <next-name> ...] \
  --max-claims <mode-slot-limit> \
  < normalized-tickets.json
```

In `next`, add `--wayfinder-ticket` only for an explicitly selected eligible
child. Pass all five Wayfinder label options only for a complete enabled
configuration; otherwise omit all five.

Use resolved Status and Priority display names, not option IDs; use IDs only
for provider mutations. Preserve binding-resolved assignee identities, rank an
unset Priority last, and reject non-finite positions. Run `--help` if the installed script's
interface is uncertain rather than guessing an option. `--max-claims` accepts
any positive integer; pass the controller's effective implementation-slot
limit. Agent capacity is a separate dispatch constraint. Blocked implementation
claims still count toward this limit; planner/handoff claims and drain claims in
[Remote Waiting](drain-scheduler.md#remote-waiting) do not.

Read the common field, plan/recovery and output shapes in
[GitHub normalization](github-binding.md#normalized-ticket-schema).
For Jira apply the [Jira field mapping](jira-binding.md#normalize-and-reconcile)
and use its account identities and ordered positions.
The ranker lives in `run-project/scripts/rank_tickets.py`. Preserve its output
collections while supplying the neutral fields below. Todo plus `ready-for-agent`
and a verified usable active plan leaf produces an implementation candidate;
without a plan it produces a planning candidate. Invalid chains block both;
stale plans require planning or base-drift screening before implementation.

## Binding-supplied inputs

1. Supply `itemId` as the stable identity within the resolved scope, `itemRef`
   as the tracker item reference, and `blockerRefs` as the complete unresolved
   blocker references. Treat these values as opaque: a reference can be a URL,
   tracker key, integer or qualified identity; `itemId` and `itemRef` are strings.
   Retain `number` as the integer local selection and tie-break key. The current
   `projectStatus`, `projectPriority` and `projectPosition` fields still carry the
   binding's status, priority and ordering values. For GitHub parent scope use
   the parent-scope normalization in the binding, including optional boolean
   `scopeParent` for the root's epic work shape, unset priority and depth-first
   sub-issue order. Pass `--candidate-order scope-position` for that scope; it
   orders new candidates by position across plan states. Project scopes retain
   the default `action-priority` ordering. Active claim precedence is unchanged.
   Closed issues remain graph evidence outside active inputs.
2. Supply an explicit boolean `parked` on every item. Parked items enter no
   candidate lane, regardless of labels; keep them in the dependency graph.
   A parked active implementation claim is blocked and retains its slot.
   This tracker gate is separate from the controller's CI parking records and
   the ranker's existing `parkedBlocked` collection of blocked Todo roles.
3. Pass `--claim-marker` as a JSON object with exactly one non-empty `status`
   or `label`, and a boolean `requiresAssignment`. For example:
   `{"status":"In progress","requiresAssignment":true}`,
   `{"label":"agent:in-progress","requiresAssignment":true}`, or
   `{"status":"Working","requiresAssignment":false}`.
   Match the named status or label against fresh item state. When assignment
   is required, only the authenticated runner's assignment makes an active
   claim; foreign or non-exclusive assignment blocks execution. When it is
   not required, the matched status or label itself represents an active claim.
   Missing or malformed marker configuration blocks ranking.
4. Retain planning/handoff assignment leases independently of active claims.
   An active marker takes precedence over a Todo planning handoff, still
   requires the verified implementation plan, and occupies implementation
   capacity even when blocked. `--in-progress-status` remains the configured
   column for Status validation and Wayfinder recovery; it does not infer
   active implementation claims.
5. Read `stoppedItems` before blocked claims or dispatch. Each entry carries the unchanged ticket, action `stop-preserve` and reasons. These are owned items missing `ready-for-agent`; stop writers and release capacity while retaining assignment and all artifacts. No plan or PR hydration is required to establish that authority is absent. Later runs remain stopped until a human restores the label.
6. Verify the binding's normalization covers every required field before
   ranking. Read the resulting claims, blocked claims and candidate collections
   before dispatch; a candidate alone never grants mutation authority.

## Binding identity and defaults

Validate the selected binding before normalization
([GitHub](github-binding.md#resolve-defaults-and-overrides) or
[Jira](jira-binding.md#binding-validation)). Use its effective binding fingerprint
for `--configuration-digest` and every lease/marker `configurationDigest`.
No-file runs supply the verified runtime fingerprint; trusted override runs
retain their committed digest and resolved snapshot. Exact historical comparisons
and verified committed-file renewal remain unchanged. Missing files alone do
not invalidate no-file leases; a changed fingerprint or source does.

Pass every resolved role name explicitly, including `--agent-work-label`.
`ready-for-agent` in controller prose names that semantic role; overrides change
its label, never its human-only authority or stop-on-removal rule. Keep raw live
labels unchanged in normalized input. Without Priority, supply null
`projectPriority` on every ticket and omit `--priority`; ordering falls back to
position and number. A present but unresolved Priority is a blocker, not absence.
