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
claims still count toward this limit; planner/handoff claims and drain claims in
[Remote Waiting](drain-scheduler.md#remote-waiting) do not.

Read [GitHub normalization](github-binding.md#normalized-ticket-schema) for every
input field, plan/recovery shape and output collection before normalizing.
The ranker lives in `deliver-tasks/scripts/rank_tickets.py`; its input and output
contract is unchanged.
