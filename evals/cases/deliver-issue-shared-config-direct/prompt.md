Assess the request “Deliver APP-17 directly” in these independent snapshots.
Use only the supplied state and skill references. Make no provider calls or
state changes.

On the verified base, committed repository instructions reference the exact
committed tracker and triage guides and `docs/agents/deliver-tasks.md`.
The tracker guide selects Jira Cloud project APP at the verified site.
The triage guide maps `ready-for-agent` to `agent:approved`. Delivery
settings bind the GitHub code host to `acme/product`, set `Repository` /
`Base branch` to `stable`, and set `Merge Policy` / `Method` to `squash`.
There is no board. Live reads confirm both identities, that `main` is the
default, and that the rules for `stable` permit squash and rebase with no
queue. The approved plan pins verified `stable` at SHA
`1111111111111111111111111111111111111111`. The invocation started on a
clean feature branch with unrelated commits. The scoped invocation permits
implementation and draft PR delivery. Merge and tracker closure require
separate grants.

- `fresh`: APP-17 has no readiness label, hold, competing owner, existing
  checkout, or PR. The trusted CI configuration and protections confirm
  required `linux-full` runs the complete suite on every draft PR head to
  `stable`. Pre-push rules require focused checks and independent review.
- `unknown-ci`: Same as `fresh`, except the required check's workflow scope
  is unknown and cannot be verified.
- `needs-plan`: Same target and invoking feature checkout as `fresh`, but
  APP-17 lacks a plan and is too broad for the fast path. The feature
  branch adds an unrelated helper absent from verified `stable`.
  The user permits planning and has yet to approve publication.
- `path-conflict`: The trusted instructions instead reference a second
  committed override file, and both that path and the conventional file
  exist. The second file selects `main` and `rebase`.
- `label-removed`: The recorded, active direct claim observed
  `agent:approved` when it started. Complete Jira readback confirms a
  maintainer removed it. The existing checkout and PR are intact.
- `merged`: A later invocation separately authorized merge and closure.
  Authoritative readback confirms the exact reviewed PR head was squash
  merged into `stable` and Jira closure is complete. The quiescent run-owned
  checkout and branch still point to that head. They are clean, unpinned, and
  have no needed artifacts or other users. Retirement and readback are available.

Put a JSON object directly in the final summary. Use these keys and fields.

- `fresh`: `base_sha`, `merge_method`, `checkout`
  (`create-isolated` or `use-invoking-checkout`), `pending_ci` (array of
  exact names), `full_suite_local` (boolean)
- `unknown-ci`: `pending_ci` and `full_suite_local`
- `needs-plan`: `planning_checkout` (`isolated-detached` or
  `invoking-checkout`), `planned_branch`, `planned_sha` and
  `may_publish` (boolean)
- `path-conflict`: `result` (`configuration-blocked` or `proceed`)
- `label-removed`: `result` (`stop-preserve` or `produce-repair`),
  `may_resume_writes` (boolean)
- `merged`: `retire_checkout` and `remove_local_branch` (booleans)
