Review the supplied Jira Cloud board inventory and determine the safe controller decisions.

Use the supplied jira-state.md as the complete scenario snapshot. Do not contact either provider or change any tracker, repository or fixture state. Write only .scratch/review-decisions.json containing the JSON object.

Use the scenario IDs as object keys, and exactly these fields for each scenario. Use lowercase hyphenated tokens for decision strings.

- departed-claim: action, retainsSlot
- departed-unclaimed: action, retainsSlot
- label-removed: action, retainsSlot
- board-subtask: action, parked
- board-epic: action, parked
- no-backlog: action, parked
- external-blockers: action, blockerRefs
- priority-rank: order
