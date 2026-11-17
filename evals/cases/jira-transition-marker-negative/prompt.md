Review the supplied persisted claims and comments. Determine the next operation using the read-only snapshots.

Use the supplied jira-state.md as the complete scenario snapshot. Do not contact either provider or change any tracker, repository or fixture state. Put the JSON object directly in the final summary field. Keep the workspace read-only.

Use the scenario IDs as object keys, and exactly these fields for each scenario. Use lowercase hyphenated tokens for decision strings.

- zero-transitions: action, claim, transitionSend
- multiple-transitions: action, claim, transitionSend
- required-fields: action, claim, transitionSend
- assignment-only: claim, state
- moved-in-review: action, retainsSlot, write
- marker-round-trip: active, digest, digestSource
- marker-fallback: action
- marker-warning: active, action
