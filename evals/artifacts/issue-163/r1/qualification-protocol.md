# GitLab tracker qualification proposal

Revision 1 of [issue #163](https://github.com/chrisbanes/skills/issues/163)
and its [active plan](https://github.com/chrisbanes/skills/issues/163#issuecomment-6982694062).
This is a checked protocol proposal. The preceding
[code-host evidence](../../2026-11-17-gitlab-code-host-live.md) applies to
code-host operations only. This revision has **zero authorized or attempted
fixture writes**. Native GitLab closure is covered by synthetic offline
decisions. Live execution, tracker cleanup and qualification are pending.

## Read-only fixture record

The controller verified GitLab.com project `banes3/Banes-project`, ID
`88319115`, private, with issues enabled, default branch `main`, Free
namespace plan and configured account with group Owner access. The fully
paged label inventory lacked `ready-for-agent` and `agent:in-progress`.
This preflight blocks the full journey. Free lacks directional blocking
links. Alternative role labels require trusted configuration and
verification. A failed link read would be unknown even on a supported tier.
No tier, setting, label, resource or branch was changed.

## Obtain one bounded grant

1. Refresh exact host, account, path and numeric ID, default branch and
   its SHA, namespace tier, issue visibility, directional blocking-link
   capability, configured role/selection names and IDs, and effective
   operation and cleanup permissions. Require a verified complete blocker
   and descendant view for the three run issues. Verify Owner cleanup scope
   for issue and MR deletion, and effective branch-create/delete authority
   for both disposable branches. Verify protection patterns, push/merge
   policy and automation. Stop before writing if any required fact is unknown.
2. Agree a unique run ID and record a sanitized preflight manifest with exact
   fixture, actors, label/selection names, immutable base SHA, one file
   path, branch names and starting absence of run resources. Require both
   branches to be new, unprotected, disposable and different from the
   default. Check that the pinned base and generated commit introduce no
   additional closing directives. Neither actor receives authority over
   existing issues, labels, refs, merge requests or project settings.
3. Obtain one explicit maintainer grant for this exact manifest and
   [write ledger](qualification-writes.json). The fixture operator applies the
   preapproved existing human role labels only while creating test issues and
   removes the claim on the stop-case issue. The controller runs the authorized
   claim, plan, merge and close steps. Explicitly approve deletion of run-owned
   issues and MR and their associated records. A Free negative-only check
   would need a separate, narrower grant and could only verify the capability
   boundary. No grant is present for either check.
4. The ledger creates one ready, non-closing fixture MR to exercise the
   tracker-controlled close. This is preparation for that check. Ordinary
   delivery still opens a draft. If the maintainer requires a draft-to-ready
   journey in this check, pause for an amended write ledger and grant before
   any send. No native-close test into `main` is proposed. The extra tracker
   backlink note also has no slot in this ledger. Verify the canonical
   source URL in the MR and the exact issue readback for this check.

## Run and verify

1. Treat the JSON ledger as the complete allowlist. Prefix requests with
   `projects/88319115/` on `gitlab.com`. Bind every issue and MR IID and
   URL-encoded branch reference to a same-run creation receipt confirmed by
   exact readback. Substitute frozen, exact request bodies from the manifest
   and verified prior steps. The only exceptions to a creation receipt are
   the create calls themselves, which require verified absence and unique run
   names. Never infer ownership from a name or IID alone. Revalidate live
   identity, grant and operation preconditions immediately before each send.
   Reject cross-project IDs, arbitrary payload fields, protected branch
   targets, auto-merge, merge trains and pre-existing resources.
2. Advance the forward rows in order. Debit the exact row against the
   15-forward limit before handing a request to transport. Keep the six
   cleanup rows reserved. Each row is single-use even after a timeout.
   Reconcile uncertain effects with at most three complete retry reads
   beyond the initial read, using receipt identity, author/account,
   exact result and timestamps. A unique, proven matching effect can be
   recorded. Unknown effects halt forward progress, and a proven absent
   effect ends that journey without a resend. Every actual send counts,
   including a rejected response, an ambiguous response and every cleanup
   write. There is no automatic write retry or second attempt at a row.
3. Verify the open blocker gates delivery after linking, then verify its
   attributable closure releases that gate. Verify the stop-case claim and
   exclusive assignment, remove its claim label as the fixture operator and
   verify stop-preserve with the assignment, human role and retained state
   intact. Do not send any further delivery writes for the stop issue.
   Verify the target claim and exact runner-authored plan note and digest.
4. Read back the created base and source, verified commit and exact MR
   head and base. Verify the canonical non-closing source link and empty
   effective closing set before merge, with the ordinary exact-head and
   policy checks. Use a one-time expected-head merge into the created base.
   Read back the merge and commit reachability. Verify the target remains
   open after merge, then perform the controller-authorized close and verify
   the exact issue and new attributable close event. Preserve the distinct
   merge and closure receipts.

## Cleanup and finish

Enter cleanup after success or a halted forward path. Spend at most one
attempt on each of the six cleanup rows. Clean up only known, verified
run-owned resources with fresh current identity, authorization and
preconditions. An already absent source branch requires readback only.
If an effect is unknown, preserve the affected resources and skip dependent
deletes. Continue independent authorized cleanup. A failed or ambiguous
deletion consumes its row. Read back its exact result and report any residue
with its known IDs, without retrying the write. Verify removal of the
relationship and note through target/blocker cleanup and authoritative
resource absence. Verify absence using exact reads and paged inventories
under unchanged fixture access. A bare 404 or a partial inventory is
insufficient. Compare the default branch SHA and settings with preflight.
Report any unexpected drift without attempting to restore shared state.

The absolute cap is **21 attempted writes**. The forward ledger leaves six
cleanup attempts even at full forward expenditure. Persist only sanitized
run ID, project/account IDs, tier, role names, resource IDs, preconditions,
attempt counts and exact outcomes, including failures and unknowns.
Never record credentials. Return independent closure, cleanup and
remaining-gate evidence to the controller for any authorized publication.
