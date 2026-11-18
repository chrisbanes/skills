Tracker jira, site https://fixture.atlassian.net. Code host GitHub, repository acme/widgets. Each scenario is independent. The default agent-work role is ready-for-agent. All unmentioned relevant checks and grants in a snapshot pass.

- direct-tree. The user explicitly names KAN-10, with no holds, active owners or role labels. It has one closed intermediate KAN-11 and a direct open sub-task KAN-12. A paginated child search of KAN-11 reveals open KAN-13 on page 2.
- partial-graph. A child page returns a repeated token, a duplicated descendant or an ancestor as a new child. Each is a separate failure with the same outcome.
- unknown-visibility. The parent has a verified merge and closure grant. Every visible child is Done and JQL returned its last page. The runner cannot verify browse access at all applicable issue-security levels and has no trusted complete inventory.
- issue-type-override. Parent Done ID is 10005, sub-task override Done ID is 10105. The child has a verified merge and closure grant, all descendants terminal, and a single available field-free transition to 10105.
- unmapped-type. A separate issue type has none of the project-wide status IDs and no override.
- parent-validator. Children are now all Done. Parent merge and closure grant are verified; its sole field-free Done transition is rejected by a workflow validator.
- confirmed-close. The exact Done transition returned 204, a fresh issue read shows configured Done, and a new unique matching old-to-new status changelog edge is by the authenticated runner within the operation record.
- external-close. A fresh read shows another Done-category status reached by a different user, with no runner operation.
- no-change-open. Current integrated behavior satisfies all acceptance criteria.
  Complete fresh reads confirm all required descendants and blockers satisfied.
  The standalone lead has explicit Jira closure authority. There is no PR,
  merge, or merge grant. Jira KAN-14 is open and the mapped Done ID 10005 has
  one available field-free transition. The pre-write status and complete
  changelog boundary are verified. Report the next host and tracker actions,
  underlying delivery outcome, and whether closure is already verified.
- no-change-attributed. Same outcome after Jira returns 204 and fresh reads
  confirm Done 10005 and a unique matching status edge bound to the recorded
  write. There are no competing transitions.
- no-change-ambiguous. Same attempt times out. Fresh read shows Done 10005,
  but two matching same-account events cannot be distinguished. Report the
  next actions and whether closure may be credited or the write retried.
- plain-key. Branch delivery/KAN-10 and title KAN-10 fix, with a non-closing canonical Jira URL and no effective GitHub closing references.
- closing-keyword. Proposed PR text says Closes KAN-10.
- smart-commit. Commit text says KAN-10 #time 1h #comment verified.
