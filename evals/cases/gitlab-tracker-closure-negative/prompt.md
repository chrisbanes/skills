Assess the independent snapshots in `gitlab-state.json`. Use the supplied
observations only. Do not contact either provider or change any files.
Put a JSON object directly in the final summary field. Use the scenario IDs
as keys, with exactly the fields listed below. Use lowercase hyphenated
decision strings, booleans for yes/no and numeric IDs for provider records.

For `closingSet`, use an array of issue identities as strings in
`hostname/project-id/issue-iid` form. Report the required effective set,
and whether the current snapshot permits merge. For `trackerAfterMerge`,
report the policy’s follow-up if a merge is later verified.

- same-project: policy, closingSet, mayMerge, trackerAfterMerge
- same-iid-other-project: policy, closingSet, mayMerge, trackerAfterMerge
- non-default-base: policy, closingSet, mayMerge, trackerAfterMerge
- github-host: policy, closingSet, mayMerge, trackerAfterMerge
- filtered-exact: policy, closingSet, mayMerge, trackerAfterMerge
- filtered-empty: policy, closingSet, mayMerge, trackerAfterMerge
