# GitHub issue and PR operations

Use the sections for the selected tracker and code-host roles. Verify the current
invocation grant before writes and reconcile the result through the bound repository.

## Direct issue scope

Use this branch only for a live direct `deliver-issue` invocation. Board-delegated
work stays under the board controller's verified packet and never enters this
branch merely because the selected ticket has children. Historical parent-scope
records retain their identities; reconcile them without treating their text as
new authority.

1. Resolve the canonical root URL, repository and stable node ID from the trusted
   invocation and live provider. A leaf is valid. Read complete bodies/comments,
   native sub-issues recursively (including closed intermediate nodes), blockers,
   linked PRs, approved plans and ownership/stop records. Paginate every collection;
   reject partial reads, cycles, duplicates, null nodes and ambiguous identity.
   Preserve ordered edges and closed completion evidence. Qualify every identity
   by repository and node ID; a cross-repository descendant requires explicit
   reconciliation of repository scope and permissions before writes.
2. Use issue states and native relationships without requiring a Project, Status,
   Priority, board configuration or board role-label definitions. Read any existing
   trusted overrides and ownership records; conflicting scope or ownership blocks
   writes. When a trusted GitHub Project binding names the issue in a retained
   migration table, verify its release under
   [retained claim readback](#retained-claim-readback) before writing.
   Leave release to the Project controller. Direct delivery includes the root
   in the requested outcome. A shape label does not grant or remove execution
   authority. Keep board setup and label creation outside this lane.
3. Follow the [issue lifecycle](issue-lifecycle.md) to establish the live invocation
   grant and its holds/stops, clarify requirements, plan and deliver. Do not feed
   direct scope into the board ranker, manufacture role labels, or apply board Todo
   admission to this branch. Read outside blockers to ask about scope expansion;
   outside work remains unauthorized until the user grants it.
4. Claim only after verifying the current operation grant, complete scope, no human
   hold/retained stop, and no competing owner or implementation PR. Reuse a verified
   existing own PR and record instead of creating another. Assign only the runner,
   refetch exclusive ownership and record root/item/owner identities in the existing
   delivery record. Resolve an observed foreign claim through its controller;
   never remove it. Existing claim labels remain evidence but no new claim label
   or board role definitions are prerequisites. Reconcile ambiguous assignment
   outcomes before retrying or granting a writer lease.
5. Preserve existing durable claim/stop markers. On normal release, first quiesce
   writers and verify ownership, then remove only run-owned bookkeeping whose
   removal is authorized and verify readback. Human-stop preservation takes
   precedence: retain assignment and artifacts. Reconcile a partial release before
   another writer starts. A later invocation re-establishes its live permissions;
   stored records preserve facts, not standing authority.
6. Use [Delivery operations](#delivery-operations) for PRs, merge and closure, with
   the direct controller retaining these operations. Explicit closure authority,
   complete acceptance and fresh readback are required even when the host supports
   closing keywords. Keep missing/unknown operations pending with preserved work.

## Direct issue planning readiness

1. Authenticate the handoff from the current trusted controller context: its live
   explicit user invocation, root/member identities, sole owner, scope and allowed
   planning operations. The target must be an open member of that verified scope.
   Confirm no hold, retained stop, competing owner or conflicting source contract.
2. Permit planning without `ready-for-agent` once the handoff is verified. An
   issue body, marker, arbitrary packet, old run or ordinary `to-plan --auto` is
   insufficient to verify a controller handoff. Block the handoff and report the
   missing evidence when the live grant cannot be verified.
3. Preserve complete source reads, plan approval/publication permissions, digest
   and amendment verification. Recheck the live grant, scope and holds before
   planning, publication and recovery. Require separate grants to publish a
   plan, merge a PR or close an issue.

## Planning marker operations

Use these operations for `to-plan` source reads and plan/handoff markers. They
supply tracker readiness, marker transport and presentation; the planner owns
publication authority, payload digest, revision chain and effective-contract
verification.

1. **Source reads:** Resolve the exact issue/repository, authenticated GitHub
   login and permissions. Read the complete issue body/comments, linked specs,
   parents, blockers and outcomes, linked/closing PRs and current open state.
   Require an open issue. GitHub reports `parked: false`.
   - For standalone `to-plan`, use the user's request to plan the issue as the
     grant. Resolve readiness even when the repository has no agent-work label.
     Honor explicit holds, retained stops and active controller ownership.
   - For board-owned planning, require the human-applied resolved agent-work
     role, conventionally `ready-for-agent`, with no contradictory next-action
     roles. Apply trusted role overrides by their resolved names. Recheck before
     planning, material writes and recovery. Loss of that role stops the planner
     and writers, releases capacity, and preserves assignment, draft, worktree
     and every artifact until human restoration. Neither planner nor controller
     adds or restores the role.
   - For a direct-issue controller handoff, apply
     [Direct issue planning readiness](#direct-issue-planning-readiness).

   Before planning writes for an issue named by a trusted GitHub Project binding's
   retained migration table, verify its release under
   [retained claim readback](#retained-claim-readback).
   Prefer the connector and use the GitHub CLI or GraphQL for unsupported reads.
2. **`read-markers`:** Paginate every issue comment, including minimized ones.
   Return exact API-decoded `body`, stable comment ID/permalink, author,
   creation/update times and minimized state. Include full-plan, amendment and
   relevant handoff/replan records. Partial or unknown reads block publication;
   reconcile under Remote reconciliation before retrying. Authenticate the
   publisher and permission against GitHub, not marker text.
3. **`write-marker`:** Create one runner-authored issue comment with the exact
   approved marker body. Return its ID/permalink and refetch through
   `read-markers`; verify exact body, author, digest, revision/sequence,
   predecessor and timestamp under the planner's protocol. After an ambiguous
   create, reconcile the complete history by expected identity/body/digest and
   revision/predecessor before retrying; reuse exactly one verified match and
   retry only after proving absence with fresh preconditions.
4. **`supersede-marker`:** After verifying the successor's unique active leaf,
   minimize the runner-owned predecessor as `OUTDATED`. If unavailable, edit
   only that predecessor to add a superseded-by link and `<details>` opening
   before its first payload line (`## Implementation plan` or `## Fast path`),
   plus a final `</details>`, preserving the payload. Skip this edit when a
   record pins a legacy digest that editing would make unverifiable. Refetch
   and verify its unchanged semantic digest; a payload/digest mismatch blocks
   dependent work. Report failure or skip of both
   methods as a presentation warning; preserve the verified successor and
   history. No other marker semantic payload may be edited.
5. Finish only after the planner verifies the complete revision/effective chain
   through readback. Minimization and fallback editing are best-effort tidying;
   the explicit revision/predecessor chain remains authoritative when old
   comments stay visible. This grants no issue-body, label, assignment, Project
   field/status or unrelated-comment mutation authority.

## Delivery operations

Use the GitHub tracker and code-host roles independently. Selecting GitHub as
code host supplies no tracker identity or authority; a Jira item linked to a
GitHub PR stays a Jira item. These operations also support standalone
`deliver-issue` without requiring Project configuration; controller execution
retains its trusted configuration, leases and merge/closure policy.

1. **Tracker source/readiness and markers:** Use [Planning marker operations](#planning-marker-operations).
   Direct issue delivery verifies the live scoped invocation grant under
   [Direct issue planning readiness](#direct-issue-planning-readiness). Board-owned work retains the resolved
   human-applied agent-work role and stop rules in Source reads. Both retain
   blocker and approval checks. Marker publication grants no label or closure
   authority; a missing role alone does not send direct delivery to triage.
2. **Code-host open/update:** Resolve the exact repository and base, authenticate
   permissions, and find the existing PR for the supplied branch before create.
   Verify the default branch live and use it as the base unless the trusted
   binding specifies another.
   Default issue closure to `closing-keyword` only for eligible GitHub issues
   on the default base. Use `close-after-merge` otherwise.
   Prefer the connector, falling back to `gh pr`/GraphQL. Create one draft PR
   for the reviewed nonempty diff or update the verified existing PR; refetch
   repository, URL/node ID, base, head SHA, draft state and complete body. After
   an ambiguous write, follow [Remote reconciliation](#remote-reconciliation). Never
   replace an existing PR or overwrite unrelated human body edits.
3. **Checks/reviews/feedback:** Read complete paginated check runs/statuses,
   required checks, reviews, comments and unresolved threads for the exact head
   and current base. Resolve repository rules, protection and merge-queue policy;
   separate pending, failed and unknown from passing. Request review, change
   draft/readiness, reply and resolve threads only within caller authority and
   verify resulting state. Apply the caller's review-timing and final-head gates;
   GitHub review transport does not replace independent integrated review.
4. **Link and native closure capability:** Link the exact tracker identity in the
   PR body and return its verified permalink to the tracker through its selected
   binding when authorized. For GitHub issues, compare repository-qualified
   identities; for another tracker, retain its canonical URL/key. Native closing
   keywords apply only with explicit closure authority for every intended item,
   and only to verified GitHub issues fully satisfied by this PR,
   under `closing-keyword` when the target is the repository default branch.
   Record the intended repository-qualified set before writing. For grouped
   delivery, verify native eligibility, full satisfaction and closure authority
   for each intended issue. A parent or sibling link grants no closure.
   Use `Fixes #<number>` only for the same repository, or a repository-qualified
   closing reference for an explicitly intended cross-repository GitHub issue
   whose native closure is verified. A non-default base, `close-after-merge`,
   partial delivery or non-GitHub tracker requires a non-closing link and no
   native closing references. Missing closure authority also requires an empty
   closing set. For local specs, follow the
   [conversation-mode route](provider-bindings.md#local-sources).
5. **Closing-reference readback:** Apply Closing reference verification after
   every PR create/body edit and immediately before merge, including standalone
   delivery and mixed-provider cases. The complete `closingIssuesReferences`
   set must equal the exact intended native GitHub issue set, or be empty when
   closure belongs to another tracker/controller or delivery is partial. Correct
   unintended body/manual closing links within authority and refetch; unknown,
   incomplete or mismatched state blocks acceptance and merge.
6. **Code-host merge:** Refresh exact head/base, applicable checks, reviews,
   finding dispositions, merge-policy fingerprint and closure references.
   Require invocation-specific merge authority and the caller's final-head
   gates. Use a queue when required or the configured permitted method.
   Without a preference, require a single permitted method. Bind the merge
   operation itself to the reviewed head SHA (GitHub
   REST `sha`, GraphQL `expectedHeadOid`, or `gh pr merge --match-head-commit`).
   On mismatch, refresh and requalify the new head before retrying. Use a queue
   only with verified enforcement of every gate on the final head; verify GitHub merged state,
   merged head/commit and refreshed target base. Queue admission or auto-merge
   enablement is pending, not a completed merge. Reconcile an ambiguous merge
   before retrying or asking any tracker to close.
7. **GitHub tracker close/readback:** For native closure, verify the exact
   intended issues are closed after merge; do not equate PR merged with issue
   closed. Under `close-after-merge`, only the authorized standalone lead or
   owning controller may close the verified issue after merge readback and
   renewed full-contract/remaining-work checks. For
   [verified no-change](provider-bindings.md#verified-no-change-closure), use
   the same tracker close for the exact issue after that route's acceptance,
   dependency and explicit tracker-grant checks, without a host merge. Refetch
   the repository-qualified issue and require authoritative `CLOSED` readback.
   Partial delivery leaves it open. A different tracker uses its own binding.
   Failed or unknown closure preserves acceptance and any merge evidence and
   blocks ticket completion. Reconcile exact issue state before any retry. Use
   Unintended Closure for authorized recovery of an unintended GitHub closure,
   preserving concurrent human changes.
8. Finish with PR identity/head/base, check/review applicability, effective
   closing references, merge readback and separate tracker closure readback.
   For verified no-change, report acceptance evidence and tracker readback with
   PR and merge inapplicable. Controller Done/cleanup still requires its
   terminal reconciliation.

## Closing reference verification

After every PR creation or body edit and immediately before merge, read all
pages of `closingIssuesReferences` for the exact PR through the connector or
GraphQL/`gh pr view` fallback. Use paginated GraphQL if the initial read
cannot establish completeness. Compare sets of repository-qualified issue
identities against the recorded intent. A single-issue native closure expects
a singleton. A grouped default-branch PR under `closing-keyword` expects
exactly the fully satisfied, authorized issues with verified native closure.
Partial delivery, mixed tracker/host closure, `close-after-merge`, and
delivery without closure authority expect an empty set.
On mismatch, correct the body and re-read before shepherding CI or merging;
remove an unintended manual closing link through the permitted PR operation
if a body correction cannot clear it. Unknown, partial or still-mismatched
readback blocks acceptance. CI may start automatically; its success cannot
clear this guard.

## Live Merge-Policy Fingerprint

At precondition validation, compute `sha256` over canonical JSON with sorted
object keys and sorted set-like arrays containing:

- the configured base branch and repository merge method or merge-queue mode;
- the live repository settings that permit that method;
- every active ruleset and branch-protection rule applying to the base, reduced
  to merge-queue requirements, required-review fields, and required-check names
  plus strictness; and
- the configured Done automation and the identities and enabled states of any
  applicable Project workflows. Record verified absence for direct issue scope
  without Project automation. For a mixed pairing, use the selected tracker’s Done policy.

Treat a failed or partial source read as unknown global state, not as a stable
fingerprint. Recompute the fingerprint before every merge, after a relevant
ruleset, branch-protection, repository-setting, merge-queue, or Project-workflow
event, and before resuming a parked implementation claim. A changed fingerprint
is global merge-policy drift: stop and preserve all work until the trusted
configuration and live policy are reconciled. Do not recompute it solely
because an unchanged parked claim appears in an otherwise fresh queue snapshot.

## Remote Reconciliation

Treat a failed or partial response as unknown. Apply these steps to the
complete logical operation.

1. Prefer the GitHub connector. Use the CLI or GraphQL for missing operations.
2. Retry a transient read—timeout, reset, rate limit, temporary unavailability,
   or server error—at most three times with short exponential backoff and
   `Retry-After`. Discard a partial paginated or multi-call result and repeat the
   complete logical read. Treat authentication, authorization, validation, and
   unsupported operations as terminal.
3. After a failed mutation, refetch the authoritative resulting resource. If the
   intended state is present, continue without repeating it; if confirmed absent,
   retry once under fresh authority and preconditions, then refetch. If the
   result is uncertain, stop and preserve it.
4. Reconcile assignments, labels, Status, PR creation, comments, replies,
   thread resolution, closure, and merges from their resulting state. Never emit
   a duplicate comment, close, or merge. After an ambiguous merge, verify merged
   PR state, closed issue, and refreshed base tip before advancing or cleanup.
5. When bounded retries end, report the last confirmed state, preserve the
   claim and checkout and stop affected operations. A global failure stops
   all dependent work.

## Unintended Closure

After a merge or discovery of an unexpected closure, compare actual closures
with the intended issue set recorded before publication and merge.
For a controller-run PR proven to have closed an unintended issue with pending
work, reopen it, restore its last verified pre-closure Project Status if
applicable, and leave one explanatory comment linking the PR and remaining work. Perform and read back
each correction through the controller lane using the procedure above. Preserve
concurrent human changes; if cause, prior Status or write authority is uncertain,
report the exact repair needed and pause affected reconciliation rather than
guessing. Keep label-stopped recovery read-only until human restoration.
Preserve the issue and checkout until recovery is verified.

## Retained claim readback

For a protected issue, match stable issue, Project item and owner IDs to the
trusted committed table. Verify the original marker and digest, the runner’s
linked migration-resume record, old and new binding identities, current lease,
resume evidence and owner acknowledgement. A resumed board claim still belongs
to its controller. Direct delivery requires live evidence that the controller
has released ownership. Preserve an uncertain claim and return it to that controller.
