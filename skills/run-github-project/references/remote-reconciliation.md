# Remote Reconciliation

Use this procedure for every GitHub read. In `setup`, apply steps 1, 2, and the
`setup` branch of step 5; setup permits no mutation. In `next` and `drain`,
apply the complete procedure to reads and mutations. A missing or failed
response is unknown, never evidence that a Project item, blocker, review,
check, comment, PR, merge, or closure is absent.

1. Prefer the GitHub connector. Use `gh project` or ProjectV2 GraphQL only for
   Project operations the connector cannot perform.
2. Retry a transient read—timeout, reset, rate limit, temporary unavailability,
   or server error—at most three times with short exponential backoff and
   `Retry-After`. Discard a partial paginated or multi-call result and repeat the
   complete logical read. Treat authentication, authorization, validation, and
   unsupported operations as terminal.
3. After a failed mutation, refetch the authoritative resulting resource. If the
   intended state is present, continue without repeating it; if confirmed absent,
   retry the same mutation once and refetch; otherwise stop and preserve state.
4. Reconcile assignments, labels, Status, PR creation, comments, replies,
   thread resolution, closure, and merges from their resulting state. Never emit
   a duplicate comment, close, or merge. After an ambiguous merge, verify merged
   PR state, closed issue, and refreshed base tip before advancing or cleanup.
5. When bounded access retries end in `setup`, report
   `configuration-blocked`. Otherwise block the affected slot unless the
   failure is global. Preserve its claim and worktree and report the last
   confirmed state. Access, configuration, and ambiguous-mutation failures are
   never parking signals; apply the scheduler's failure-isolation rules.
