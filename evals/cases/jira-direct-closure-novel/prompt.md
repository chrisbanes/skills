Assess the supplied direct Jira issue delivery scenarios and their tracker and code-host effects.

Use the supplied jira-state.md as the complete scenario snapshot. Do not contact either provider or change any tracker, repository or fixture state. Write only .scratch/review-decisions.json containing the JSON object.

Use the scenario IDs as object keys, and exactly these fields for each scenario. Use lowercase hyphenated tokens for decision strings.

- direct-tree: eligibleScope, rootAction, subTaskDelivery
- partial-graph: action, write
- unknown-visibility: action, write
- issue-type-override: doneId, write
- unmapped-type: action, write
- parent-validator: merge, closure, retry
- confirmed-close: closure
- external-close: closure, write
- plain-key: action
- closing-keyword: action, write
- smart-commit: action, write
