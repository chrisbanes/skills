# Normalized Ticket Schema

## Ranker Invocation

Write the fresh normalized tickets as one JSON array, then run:

```text
python3 <skill-dir>/scripts/rank_tickets.py \
  --mode <next-or-drain> \
  [--wayfinder-ticket <explicit-user-selected-child-number>] \
  --current-user <runner-identity> \
  --repository <owner/repository> \
  --configuration-digest <committed-configuration-digest> \
  --base-branch <base-branch> \
  --issue-closure <closing-keyword-or-close-after-merge> \
  --backlog-status <backlog-name> \
  --planning-status <todo-name> \
  --ready-status <ready-to-implement-name> \
  --in-progress-status <in-progress-name> \
  --claim-marker '<binding-claim-marker-json>' \
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
claims still count toward this limit; planner/handoff claims and drain claims in
[Remote Waiting](drain-scheduler.md#remote-waiting) do not.

Read [GitHub normalization](github-binding.md#normalized-ticket-schema) for every
input field, plan/recovery shape and output collection before normalizing.
The ranker lives in `deliver-tasks/scripts/rank_tickets.py`. Preserve its output
collections and five-column decisions while supplying the neutral fields below.

## Binding-supplied inputs

1. Supply `itemId` as the stable identity within the resolved scope, `itemRef`
   as the tracker item reference, and `blockerRefs` as the complete unresolved
   blocker references. Treat these values as opaque: a reference can be a URL,
   tracker key, integer or qualified identity; `itemId` and `itemRef` are strings.
   Retain `number` as the integer local selection and tie-break key. The current
   `projectStatus`, `projectPriority` and `projectPosition` fields still carry the
   binding's status, priority and ordering values.
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
   An active marker takes precedence over a Todo/Ready planning handoff, still
   requires the verified implementation plan, and occupies implementation
   capacity even when blocked. `--in-progress-status` remains the configured
   column for five-column validation and Wayfinder recovery; it does not infer
   active implementation claims.
5. Verify the binding's normalization covers every required field before
   ranking. Read the resulting claims, blocked claims and candidate collections
   before dispatch; a candidate alone never grants mutation authority.
