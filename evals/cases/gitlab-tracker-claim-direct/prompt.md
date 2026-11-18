Assess the independent snapshots in `gitlab-state.json`. Use the supplied
observations only. Do not contact either provider or change any files.
Put a JSON object directly in the final summary field. Use the scenario IDs
as keys, with exactly the fields listed below. Use lowercase hyphenated
decision strings, booleans for yes/no and numeric IDs for provider records.

- claim: action, claimLabel, assigneeIds, verifyExclusive
- shared-assignment: action, retainsSlot, write
- claim-label-removed: action, releaseSlotAfterQuiescence, write
- free-tier: blockerCapability, dependenciesComplete, mayDispatch
- failed-link-read: blockerCapability, dependenciesComplete, mayDispatch
