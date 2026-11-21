# GitHub Binding

## Core principle

Translate the controller's decisions into verified GitHub operations; this
binding supplies no selection, mutation or merge authority of its own. GitHub
Project and parent-issue scopes are supported. Resolve optional overrides and fresh
defaults below; preserve existing marker formats and the selected authority mode.
Board rules below apply to run-project. Direct deliver-issue invocations enter
[Direct issue scope](#direct-issue-scope) before any board-default or ranker operation.
The binding supplies operations, never an invocation grant.

## Operations

1. For setup or execution, validate identity, access and configuration under
   Binding validation and Setup; review uses only permitted or supplied evidence.
2. For authorized board reads, obtain complete scope/issue/PR state through Remote
   reconciliation, then normalize it under Normalized Ticket Schema for the board
   ranker. Direct issue delivery follows Direct issue scope without board normalization.
3. Execute only controller-authorized operations: assign the authenticated runner,
   write the scope's verified claim/completion marker, publish/refetch comments,
   perform permitted PR operations and merges, and reconcile closure/Done.
4. Use Project Watcher commands only under the controller scheduler. Its output
   is a wake hint, never authority or a replacement for a complete live read.
5. Pass the invoked lane's finish gate only after authoritative readback; preserve
   unknown outcomes and artifacts under Remote reconciliation.

## Planning marker operations

Use these operations for `to-plan` source reads and plan/handoff markers. They
supply tracker readiness, marker transport and presentation; the planner owns
publication authority, payload digest, revision chain and effective-contract
verification.

1. **Source reads:** Resolve the exact issue/repository, authenticated GitHub
   login and permissions. Read the complete issue body/comments, linked specs,
   parents, blockers and outcomes, linked/closing PRs and current open state.
   For a verified direct-issue controller handoff, apply
   [Direct issue planning readiness](#direct-issue-planning-readiness) instead of
   the role prerequisite below. For ordinary standalone or board planning,
   require the open issue to carry the human-applied
   resolved agent-work role, conventionally `ready-for-agent`, with no
   contradictory next-action roles;
   GitHub reports `parked: false`. Apply trusted role overrides without requiring
   the conventional literal label as well. Recheck before planning, material
   writes and recovery. Loss of that role stops the planner and writers, releases
   capacity, and preserves assignment, draft, worktree and every artifact until
   human restoration. Neither planner nor controller adds or restores the role.
   Before planning writes for an issue named by a trusted GitHub Project binding's
   retained migration table, verify its release under
   [retained claims](#retain-claims-across-legacy-migration).
   Prefer the connector; use the GitHub access fallback below when needed.
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

1. **Tracker source/readiness and markers:** Use Planning marker operations.
   Direct issue delivery verifies the live scoped invocation grant under
   Direct issue planning readiness. Board-owned work retains the resolved
   human-applied agent-work role and stop rules in Source reads. Both retain
   blocker and approval checks. Marker publication grants no label or closure
   authority; a missing role alone does not send direct delivery to triage.
2. **Code-host open/update:** Resolve the exact repository and base, authenticate
   permissions, and find the existing PR for the supplied branch before create.
   Prefer the connector, falling back to `gh pr`/GraphQL. Create one draft PR
   for the reviewed nonempty diff or update the verified existing PR; refetch
   repository, URL/node ID, base, head SHA, draft state and complete body. After
   an ambiguous write, reconcile Remote reconciliation before retrying. Never
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
   closing set. Local sources route to `implement`, outside this workflow.
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
   gates. Bind the merge operation itself to the reviewed head SHA (GitHub
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

## Binding validation

For `next` or `drain`, resolve the binding read-only using the procedure below.
An absent override file is valid; an existing file requires its exact trusted
instruction reference and both files committed on verified base. Never ignore an
untrusted, uncommitted or invalid file to fall back to defaults. Validate all
resolved values and pinned identities against complete live reads. Record the
[effective binding fingerprint](#effective-binding-fingerprint), default branch
and live merge-policy fingerprint. Missing, ambiguous, unknown or drifted state
returns `configuration-blocked`, naming the lookup, candidate identities and
required correction; preserve all work. Execution never enters setup repair.
Only an already trusted, committed display-name-only edit may use
[presentation-only renewal](#renew-presentation-only-configuration).

### Resolve defaults and overrides

1. Read closest trusted repository instructions and inspect
   `docs/agents/deliver-tasks.md`, or their explicitly referenced override path.
   If both exist and select different files, stop on conflicting configuration.
   Treat an existing legacy `docs/agents/run-github-project.md` as migration
   required, not as an absent file. Setup must inspect the
   [legacy migration](#approval-gated-legacy-migration) gate before resolving
   defaults; execution returns `configuration-blocked` and never migrates.
2. Select **Tracker** and **Code host** independently (default `github` for
   each; a `gitlab` code host uses the [GitLab binding](gitlab-binding.md);
   other providers need their own supported binding). Resolve repository host
   and `owner/repository` from the current checkout's git remote and verify its
   live identity. When the code host is not GitHub,
   resolve the tracker repository under [Delivery bindings](provider-bindings.md)
   step 1 (labels and short `#N` use it). Use explicit repository overrides first;
   without them, conflicting remotes or an unclear repository block.
3. Resolve **Scope** from the trusted override when present, otherwise from the
   invocation. A Project URL selects a board; route a named issue to
   [Direct issue scope](#direct-issue-scope) via `deliver-issue`. Use the
   verified tracker repository for a short `#N`.
   Validate explicit selectors and identity pins against exactly one canonical
   URL and stable node ID. Invalid, inaccessible or conflicting explicit scope
   blocks the run without discovery.
   - With no explicit scope for `run-project`, read all Projects linked to the
     verified GitHub tracker repository. Use the GitHub connector or the
     [repository's `projectsV2` GraphQL connection](https://docs.github.com/en/graphql/reference/repos#repository)
     via `gh api graphql` on that host. Paginate without a name filter and read
     `id`, `url`, `title`, `closed` and `template`, using supplied complete state
     when available. Follow [remote reconciliation](#remote-reconciliation) for
     all live reads.
   - Select the sole visible open, non-template Project from a complete read.
     With zero or multiple candidates, or incomplete or unavailable evidence,
     report `configuration-blocked` for Scope (in review, `review-blocked`),
     list the known candidate URLs and the reason, and ask for the Project URL
     or the access needed to validate it. Use repository links as the only
     discovery signal.
   - Report the inferred Project URL and repository. Continue with normal
     binding validation and repository filtering, and record the resolved
     Project ID in the effective binding. Discovery is read-only and grants no
     item authority. Keep the resolved Project for the run and check it against
     any retained binding before recovery.
4. Obtain the default branch from live code-host repository settings and use it as base
   unless overridden. Resolve a merge queue when required by live policy;
   otherwise use the sole permitted repository merge method. Multiple permitted
   methods without an explicit repository preference or override block; do not
   invent a preference. Verify any override against live permissions/rules.
   Default issue closure to `closing-keyword` for the default base, otherwise
   `close-after-merge`; default Done automation to `set-status` without archive.
   For Project scope read actual workflows and reject conflicting automation;
   parent scope uses closed issues as Done and no Project automation.
5. Overlay only supplied override fields on these defaults. For parent scope,
   resolve the existing `agent:in-progress` claim label by the same unique-name/ID
   rules as role labels, requiring a distinct ID from every role label. It is
   agent-owned bookkeeping, never a role grant.
   Skip Project Status/Priority/automation lookups entirely. For Project scope resolve the live
   `Status` field and `Todo`, `In Progress`, `Done` options by exact name on
   **every run**, including no-file recovery. Each lookup must have exactly one
   result. A missing or duplicate field/option blocks; show its name and all
   matching IDs. Explicit name overrides replace the conventional name. A pin
   selects its ID instead, but must still resolve to the intended object in the
   correct Project/field/repository with the stored name. A name change on the
   same ID is drift requiring reconciliation; an ID resolving elsewhere stops.
6. Paginate repository labels and resolve the conventional role names
   `ready-for-agent`, `ready-for-human`, `needs-triage`, and `epic` freshly.
   Match names case-insensitively for discovery, then retain the exact live name
   and ID. Require exactly one label per role; missing labels or multiple
   matches (including case variants) block. Explicit role names/IDs override
   discovery; validate their identity and require distinct role mappings.
   Never create/rename labels, infer roles from prose, or add/restore agent
   authority. Optional Wayfinder stays disabled unless explicitly enabled with
   complete mappings. Agent Setup defaults to runtime capabilities.
7. For Project scope resolve optional Priority if present: require one `Priority` field, unique
   option names and its complete live option order; absence means all items
   have unset priority and no `--priority` arguments. Explicit Priority mappings
   override order/names/IDs and are validated. Parent scope uses sub-issue order,
   unset priority and no Project filter. Default filter is none, polling
   is 120 seconds; read all applicable protection/review/check requirements live.
   Finish `configuration-valid` only with complete evidence and an effective
   fingerprint. No-file validation creates neither a file nor an instruction
   patch and grants no claim, write or merge permission.

### Direct issue scope

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
   [retained claims](#retain-claims-across-legacy-migration) before writing.
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

### Direct issue planning readiness

1. Authenticate the handoff from the current trusted controller context: its live
   explicit user invocation, root/member identities, sole owner, scope and allowed
   planning operations. The target must be an open member of that verified scope.
   Confirm no hold, retained stop, competing owner or conflicting source contract.
2. Permit planning without `ready-for-agent` only for that verified handoff. An
   issue body, marker, arbitrary packet, old run or ordinary `to-plan --auto` is
   insufficient. If the live grant cannot be verified, retain the ordinary source
   readiness requirement; report the missing evidence rather than granting it.
3. Preserve complete source reads, plan approval/publication permissions, digest
   and amendment verification. Recheck the live grant, scope and holds before
   planning, publication and recovery. A label exception is not permission to
   publish a plan, merge a PR or close an issue.

### Parent-issue scope

For retained parent-scope records, use [Direct issue scope](#direct-issue-scope)
when the current invocation is direct issue delivery. Return board-owned records
to their existing controller. This heading preserves existing reference anchors;
it does not expose a removed skill or authorize legacy scope selection.

### Effective binding fingerprint

For no-file runs compute `sha256` over UTF-8 canonical JSON (sorted object keys,
compact separators, sorted set-like arrays, preserved priority/profile order)
containing tracker/code-host identities, resolved repository and scope IDs,
base/default branches, field/option/role IDs **and names**, claim marker,
filter, priority order, agent/Wayfinder/monitoring defaults and resolved
merge/closure/Done policies. Include `configurationSource: "defaults"`; store
this resolved snapshot and fingerprint in the controller checkpoint and leases.
Do not include timestamps, checkout paths or moving base SHAs in this digest;
base identity and live merge-policy fingerprint are independently revalidated.

Retain existing committed-file digest semantics for trusted override bindings;
record their resolved snapshot alongside that digest and revalidate both.
Throughout controller leases, pause/parking/Wayfinder markers and normalization,
`configurationDigest` and `--configuration-digest` mean this effective binding
identity: the committed override digest when a file exists, the runtime
fingerprint otherwise. In controller, planner and delivery prose,
`ready-for-agent` denotes the resolved agent-work role, never an additional
literal-label requirement.
Never require a phantom file digest or rewrite historical
markers. Recompute/compare before every claim, material write, merge and recovery.
Missing prior snapshot, changed defaults/IDs/policy, a source switch to/from a
file or unknown reads stop and preserve affected work; they never silently
rebind old claims. Presentation-only renewal applies to committed override
edits only, with all its existing proofs; no-file drift requires explicit
reconciliation and a new verified lease before writers resume.

## Setup

Inspect for a legacy Status schema or configuration first under
[legacy migration](#approval-gated-legacy-migration); otherwise validate defaults
through the resolution procedure. Configuration is
optional and holds only requested overrides. For requested file creation or
repair use [project configuration](#github-project-configuration) and additive
setup below; preserve all unrelated values and explicit pins. Never create or
rename Project fields/options or infer role authority from placement. Legacy
item moves require the explicit migration approval below. Validate Agent Setup
profiles against current runtime capabilities;
keep the selected lead model unchanged. Allow `closing-keyword` only on the
default base. Finish with the applicable validation or proposed-edit result.

### Additive Setup for an Existing Repository

Start with the working-tree configuration, its committed version, and the
closest trusted instructions. Verify repository and Project identity against
complete live reads. Reconcile each value: retain existing values that still
match live state; add requested sections and missing required values; repair a
name only when its stored ID still identifies the same object. Change an
existing value only when the request or verified drift calls for it. Preserve
unrelated fields, IDs, filter, merge policy, comments, local edits, and trusted
instruction text. Never recreate the binding from the template or overwrite a
user choice merely to make it match a proposed default. An absent optional
section is normal, not drift.

If the trusted instructions already point to the exact configuration file,
leave them unchanged. If that reference is missing, propose the minimum patch
to those instructions and write it after confirmation, preserving their other
text and the existing configuration. Do not run the Status-schema migration
gate for an already adopted schema, move waiting Todo handoffs, reroute an existing ticket
owner, or touch Project, issue, or PR state.

When adding or updating Agent Setup, discover the current runtime's available
roles, models, reasoning levels, and access before proposing profiles. If the
request supplies no agent choices, propose the smallest setup:
one `default-owner` profile using `runtime-default` for model and reasoning,
named as both planner and ticket default, plus one `read-only-evidence` profile
when the runtime supports it. Prefer a read-only role capable of both evidence
analysis and independent review; otherwise include a separate review-capable
profile. Disclose a missing independent reviewer as a delivery capability
blocker. The [repair progress gate](ticket-lifecycle.md#repair-progress-gate)
needs that helper after a repeated non-CI failure. If the runtime has no
eligible read-only evidence role, disclose during setup that such a stall will
remain an exact ticket-local blocker; never invent a helper. Add other helper
profiles only when requested or needed for a specified capability. Remove obsolete
`Routing` and `TypeSafe judgment model` fields shown in the binding during an authorized setup edit
subject to the active-lease rules below; do not migrate live bindings during
execution. Resolve missing choices without duplicating a profile or replacing
a user pin.

Apply only the additions and evidence-backed changes, then validate the full
binding and any agent profiles against the runtime and complete live reads. If
it already matches the request, leave the files unchanged. If remote validation
is unavailable, keep the scoped local edit and report precisely which live
check remains unverified; do not report `configuration-valid`. Do not commit
implicitly. Finish `configuration-ready-to-commit` when validation passes and
the diff is ready; committing is the user's next action, not a condition of
that result. Report `configuration-valid` only after the committed
configuration and trusted reference on verified base pass fresh validation. Pause new claims while the edit is pending; existing claims may
continue on their unchanged binding.

Changing the effective binding fingerprint while a ticket still holds an old
lease invalidates it unless execution has verified the narrow
[presentation-only renewal](#renew-presentation-only-configuration).
Setup does not perform that renewal or assume it will succeed. While old-digest claims exist, prepare the
edit only in an already separate configuration checkout. Keep the controller
and ticket checkouts used to resume those claims clean and on the old committed
binding. If no separate checkout is available, present the proposed patch
without writing it; setup does not create worktrees. Existing owners may finish
their claims against the old digest, including feedback and repair. Defer
committing the new configuration to verified base and activating it until all
old-digest claims finish. The only exception for legacy migration is the
[retained-claim procedure](#retain-claims-across-legacy-migration). If validation passes, report
`configuration-ready-to-commit` with application or activation pending as
appropriate; do not change existing owners or leases. New routing and other
configuration changes apply only after activation.

When a user requests overrides and no configuration exists, present only the
requested overrides with the minimum exact-file trusted-instruction reference.
Write after confirmation, preserving unrelated text; do not commit implicitly.
Pause new claims until the pair is committed on verified base and freshly
validated. A user-authorized configuration commit may contain only that pair.
Absent a request for overrides, keep the no-file binding and create nothing.

Treat a legacy `Execution approver logins` entry as obsolete configuration.
Remove one shown in the binding during an otherwise authorized setup edit when no old-digest claim
depends on the binding; otherwise report the deferred cleanup. Never propose
conditional removal of fields the binding does not show. Its presence or
contents never gate Todo eligibility.

Setup uses the read-only pagination, retry, and incomplete-read rules from
[remote reconciliation](#remote-reconciliation). If a complete configuration
read cannot be established, discard partial state and return
`configuration-blocked`. Ordinary additive setup is read-only remotely; approved
legacy migration alone uses mutation reconciliation below.

## Approval-gated legacy migration

Core principle: approve an exact, reversible migration before changing any
board or repository state; preserve labels and concurrent work throughout.
This is the only exception to humans placing legacy items. Setup permission
alone authorizes discovery and a dry run, not migration or execution.

1. **Discover read-only.** Read the working and committed configuration and its
   closest trusted `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` references, plus complete paginated
   Project fields/options, items (including drafts and archived items), labels,
   assignments, workflows and active leases. Detect the old five-column schema
   (`Backlog`, `Todo`, `Ready to implement`, `In progress`, `Done`) by verified
   names/IDs, including explicit legacy name mappings, and the old
   `docs/agents/run-github-project.md` or explicitly referenced legacy file.
   Either signal enters this gate; config-only migration needs no item moves,
   board-only migration creates no optional file. An adopted three-column board
   with no legacy file stays on additive setup. If old options remain empty and
   no legacy file/patch remains, validate read-only with no migration writes or
   repeated approval; reconcile any prior journal before declaring completion.
   Missing, ambiguous, inaccessible
   or partial identities block migration; ask the human to resolve missing
   target options instead of creating/renaming them. Require quiesced writers,
   zero In Progress items and no old-binding leases unless each such item or
   lease qualifies under [retained claims](#retain-claims-across-legacy-migration).
   Report every ineligible item or lease as a dry-run blocker.
2. **Present the complete dry run.** Enumerate every item in Backlog or Ready to
   implement, including identity/reference, old option ID/name, target Todo
   ID/name, exact current label IDs/names and unchanged labels. Include zero
   counts when empty. Separately list every Backlog item already carrying the
   agent-work role that will become immediately eligible, after parked,
   contradictory-role, open-state and blocker checks; also list labelled items
   that remain blocked and why. A Ready item still needs a verified plan leaf
   before implementation. Show exact before/after file paths and full patch:
   rename the legacy file to `docs/agents/deliver-tasks.md` (or an explicitly
   approved override path), change its heading to `Deliver tasks`, add Tracker
   and Code host Provider `github`, and Scope Type `project`/URL from the
   verified Project. Retain Project/repository identity pins, Todo/In progress/
   Done mappings, roles, filters, priority, agent settings, merge/closure policy,
   comments and unrelated content. Remove only legacy Backlog/Ready name/ID
   fields and explicitly shown obsolete fields under additive setup. Add any
   missing required role mappings only from verified live identities. Update
   each trusted exact-file reference in `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` in the same patch.
   An existing destination, conflicting references or local edits require a
   reconciled patch preserving both, never overwrite. Show the journal location,
   rollback plan and activation/commit boundary. Include the retained claims
   and their treatment under the new binding. Leave every Status option intact.
   Finish `migration-awaiting-approval` with no board or repository writes,
   including no journal file, until explicit approval of this exact plan. A
   decline finishes `migration-declined` with no changes; silence is not approval.
3. **Journal before applying.** Refresh the whole plan and preconditions after
   approval; changes to membership, labels, files, claims or writer state require a revised
   dry run and renewed approval. Persist a durable local migration record at
   the approved location before the first write and verify it can be read back.
   Include migration/operation IDs, approval evidence, repository/Project/field/
   option identities, source commit and binding digest, plan digest, each item's
   old/target Status, labels (label changes: empty), assignment and archive state.
   Store original bytes/digests and existence of every touched config/instruction
   path, proposed bytes/digests, file rename mapping and ordered operations.
   Never put secrets in the record. Record intent before each write, and append
   attempted/verified/unknown/conflicted results and authoritative readbacks
   durably after it. If journaling fails, stop before the next write.
4. **Apply and reconcile one operation at a time.** Recheck each original-state
   precondition and the writer fence immediately before its write. Change only Status for a listed
   item, using the verified Project/item/field/option IDs; refetch and verify
   Status, labels, membership, assignment and archive state after every write.
   Preserve labels verbatim; migration never adds/restores `ready-for-agent`.
   For failed, timed-out or unknown writes, read complete authoritative state
   before retry: target state means record success without replay; original
   state permits a retry only with fresh preconditions and unchanged approval;
   any other state or incomplete read stops as `migration-blocked`, preserving
   the journal and completed operations. Never infer failure from an error or
   success from the command exit alone. Apply the approved config/reference
   patch with original-bytes preconditions, verify exact bytes/existence after
   each write, and journal partial rename/reference outcomes the same way.
5. **Rollback safely when requested.** Use the journal in reverse operation
   order, reconciling every unknown attempt first, including a write whose
   success was not journaled. Restore each item's original Status only if it
   still has the migration's verified target Status and unchanged membership,
   labels, assignments and archive state; otherwise preserve current state and
   report a rollback conflict for human reconciliation. Restore original config/
   instruction bytes and legacy path, removing a migration-created destination
   only when its current bytes still equal the recorded migration output. For
   partial file writes use each operation's recorded before/after state. Preserve
   concurrent edits; offer a reviewed inverse patch instead of wholesale restore
   on mismatch. Journal rollback intent and verify every inverse write; apply
   the same unknown-outcome reconciliation before retry. Already restored state
   is a no-op. A missing old option blocks its inverse; never recreate or delete
   options. Report remaining conflicts and retained recovery evidence.
6. **Finish from readback.** Re-enumerate affected items and all touched paths;
   verify intended statuses, unchanged labels and the complete config/reference
   pair. Report each verified, pending, unknown or conflicted operation, journal
   location and recovery action. Return `migration-blocked` for incomplete or
   divergent outcomes; do not start execution or commit implicitly. Successful
   file edits finish `configuration-ready-to-commit`; activation/new claims wait
   until the pair is committed on verified base and freshly validated. A
   board-only migration finishes `configuration-valid` only after fresh binding
   validation. Human option deletion is a separate action once old options are
   empty; setup never deletes options, even after approval or rollback.

### Retain claims across legacy migration

Use this exception only when migrating a trusted legacy file to a committed
replacement on the same Project and repository. Board-only migrations still
require zero In Progress items and no old leases.

1. **Verify each claim at cutover.** Carry a verified authority pause or a
   quiesced Todo handoff with a verified active plan leaf and exclusive
   assignment. Verify the old binding and claim identity, original marker
   author and digest, current membership/lane and owner, and checkpoint or
   owner evidence that all writers and in-flight mutations are settled. An
   In Progress item qualifies only with a verified authority pause. An active
   writer, unmatched In Progress item, CI-parked lease or unverified claim
   blocks application. Preserve uncertain artifact or budget evidence as
   unknown and require it to be resolved before resume.
2. **Specify the preservation in the approved patch.** Add a
   `## Retained migration claims` table to the replacement binding. List each
   issue URL and node ID, Project item ID, assignee, pre/post Status option IDs,
   kind (`authority-pause` or `todo-handoff`), and original committed binding
   identity and digest. Pin the immutable pause or active plan permalink
   and [payload digest](../../to-plan/references/github-mode.md#payload-digest).
   Journal the same entries and the preserved source,
   branches, heads, PRs, checkpoints, qualification evidence and consumed or
   remaining budgets. Use null for verified absence and mark unknowns explicitly.
   Keep local paths and private evidence out of the committed table. Move a
   retained Backlog/Ready item only via its listed Status operation. Preserve
   the labels, owner, dependency edges, historical markers and artifacts.
   Keep excluded labelled items out of the dry run's newly eligible list.
3. **Fence dispatch through activation.** Keep old and new controllers and
   ticket writers quiesced from the first mutation through readback and
   activation. Activate only once the complete journal reconciles, the trusted
   replacement containing the approved table is committed on verified base,
   and fresh reads confirm the migration and its retained items. Before
   ranking and on refresh, match table entries by stable IDs and check the
   current owner, marker and Status. Keep unresolved entries in the frontier
   outside ranking and capacity, with their dependency edges, even when a
   checkpoint is unavailable. Mismatched entries block their own writes and
   stay excluded. An incomplete or ambiguous table blocks dispatch until all
   its protected identities are known. An old binding cannot issue a new
   grant after activation.
4. **Resume under the current binding.** Observe the original pause's resume
   condition or obtain an explicit scoped continuation for a Todo handoff.
   Apply label-stop and revalidate ownership, source/plan, worktree, PR/head,
   base, budget, and applicable checks, reviews and grants. Publish and refetch
   one runner-authored `<!-- run-github-project:migration-resume:v1 -->`
   record linking the committed table entry and original marker permalink and
   digest, old/new binding digests, verified resume evidence, and the new
   lease identity. Apply the normal authority-resume protocol for paused
   work. Reconstruct the transition from both records on later runs. Require
   owner acknowledgement before writes and keep the same owner, artifacts and
   counters. A missing or ambiguous record preserves the hold. Neither
   migration nor the table supplies execution authority or qualification.
5. **Rollback before release.** Apply the ordinary journal rollback only
   after fencing writers and checking that no retained claim changed or
   acquired a lease under the new binding. If a claim resumed or activation
   admitted other work, preserve it and reconcile the affected binding and
   ownership before any inverse operation.

## GitHub Project Configuration

Use `docs/agents/deliver-tasks.md` for optional overrides in the repository
that owns the queue. Include only sections/fields being overridden; the following
is a field catalogue, not a required complete file. Resolve omitted fields from
fresh defaults. Replace included placeholders with live verified data. The
closest trusted `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` must reference that exact file.
For parent scope, use Scope type `parent-issue` and the canonical parent issue
URL; omit Project, Status, Priority and Done automation sections. Optional
`Claim` overrides are `Label` and `Label ID`, defaulting to the existing
`agent:in-progress` label. Verify its distinct identity as above; these overrides
never rename/create labels or change next-action roles.

For an existing binding, run `setup` from its current values instead of copying
this template over it. Follow the
[additive setup procedure](#additive-setup-for-an-existing-repository).

```markdown
# Deliver tasks

## Tracker

- Provider: `github`
- Repository: `<owner>/<repository; required when Code host is not github>`

## Code host

- Provider: `github`

## Scope

- Type: `<project or parent-issue>`
- URL: `<Project or parent issue URL>`

## Repository

- Host: `github.com`
- Repository: `<owner>/<repository>`
- Default branch: `<branch>`
- Base branch: `<branch>`

## Project

- Owner: `<organization-or-user>`
- Number: `<number>`
- URL: `<url>`
- Node ID: `<PVT_...>`
- Filter: `<optional trusted Project filter, or none>`

## Status

- Field name: `<Status>`
- Field ID: `<PVTSSF_...>`
- Todo name: `<Todo>`
- Todo option ID: `<option-id>`
- In progress name: `<In Progress>`
- In progress option ID: `<option-id>`
- Done name: `<Done>`
- Done option ID: `<option-id>`

## Triage

- Needs-triage label: `<repository label mapped to needs-triage>`
- Needs-triage label ID: `<LA_...>`

## Work Roles

- Agent-work label: `<repository label mapped to ready-for-agent>`
- Agent-work label ID: `<LA_...>`
- Epic label: `<repository label mapped to epic>`
- Epic label ID: `<LA_...>`
- Human-work label: `<repository label mapped to ready-for-human>`
- Human-work label ID: `<LA_...>`

## Agent Setup (optional)

- Default planner profile: `<profile name>`
- Default ticket profile: `<profile name>`

| Profile | Capability | Best suited to | Runtime role | Execution model | Reasoning |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `default-owner` | `<bounded task description>` | `<role>` | `<model or runtime-default>` | `<level or runtime-default>` |
| `<evidence-name>` | `read-only-evidence` | `Repeated non-CI failure investigation` | `<read-only role, if available>` | `<model or runtime-default>` | `<level or runtime-default>` |

## Wayfinder (optional)

- Enabled: `<true or false>`
- Map label: `<wayfinder:map>`
- Map label ID: `<LA_...>`
- Research label: `<wayfinder:research>`
- Research label ID: `<LA_...>`
- Prototype label: `<wayfinder:prototype>`
- Prototype label ID: `<LA_...>`
- Grilling label: `<wayfinder:grilling>`
- Grilling label ID: `<LA_...>`
- Task label: `<wayfinder:task>`
- Task label ID: `<LA_...>`

## Monitoring (optional)

- Poll interval seconds: `<120>`

## Priority

- Field name: `<Priority>`
- Field ID: `<PVTSSF_...>`
- Options in descending order:
  1. `<Critical>`: `<option-id>`
  2. `<High>`: `<option-id>`
  3. `<Medium>`: `<option-id>`
  4. `<Low>`: `<option-id>`

## Merge Policy

- Method: `<merge, squash, rebase, or merge queue>`
- Issue closure: `<closing-keyword or close-after-merge>`
- Required reviews: `<repository rule>`
- Required checks: `<repository rule>`
- Done automation: `<none, set-status, or set-status-and-archive>`
- Automation description: `<workflow and trigger, or none>`
```

The binding specifies how merging works. Establish invocation-scoped permission
under [run authority](authority-and-pauses.md).

Keep human-readable names beside IDs so startup validation can distinguish a
rename from an ID that now identifies a different object. Preserve repository-
specific comments and additions when repairing stale mappings.

`Todo` is the default display name for the lane that queues planning. Pass its
configured name through `--planning-status`; planning action names and
`blockedPlanningClaims` still describe that work. Current human-applied role-label membership is
authority; column membership only routes work. Never read transition history to prove authorization or a handoff.
Preserve an existing binding's verified lane name, including `Planning`, until
a human renames the live option and an authorized setup reconciles the same
option ID. Once that presentation-only edit is trusted and committed, execution
may [renew affected leases](#renew-presentation-only-configuration) after proving
equivalence; an unreconciled live rename still stops execution. A display-name
rename alone does not require moving items or running the Status-schema migration.

Treat the epic label as a work-shape declaration and the human-work label as a
next-action role. Require both mappings even when the current Project has no
matching issue. Never infer either role from issue titles or bodies. Humans
create and rename role labels; never do so from this workflow.

Omit the Wayfinder section, or set `Enabled` to `false`, to preserve the
ordinary workflow unchanged. When enabled, require every displayed Wayfinder
name and ID pair, validate each pair live at startup, and reject an ID that
resolves to another label. A renamed matching ID is repairable drift. The map
label identifies the parent map; the other four labels are mutually exclusive
child types. Never create, rename, or infer any of them.

Humans own the Project schema and agent role authority. Require the resolved
`Todo`, `In Progress`, and `Done` Status options (or explicit configured names)
with verified IDs. Unlabelled Todo is
the backlog; placement never grants authority. Keep `ready-for-agent` throughout
active work. The controller never adds or restores it, including setup, triage,
recovery and retries. Only [approved setup migration](#approval-gated-legacy-migration)
may move legacy items; humans alone delete empty old options. Never create or
rename Status options. Do not retain an Agent Brief compatibility path. Revalidate
usable marker plans by their identity, integrity, and configured base; do not
require Status event history. An existing `Execution approver logins` entry is
obsolete and must not affect eligibility.

Omit Agent Setup to use runtime-default agents under the existing capability
rules. When present, require unique profile names, a default-owner profile for
both planner and ticket defaults, and a runtime role with the required access
for every profile. Include a `read-only-evidence` row when the runtime supports
it because the repair progress gate needs that helper. Ensure a configured
read-only profile also supports independent judgment-based review; the same
profile may cover evidence and review if its runtime role supports both. Add
`read-only-discovery` or `exceptional-investigator` rows only when wanted. When
no read-only evidence role is available, disclose that repeated non-CI stalls
remain ticket-local blockers. The named defaults are preferences; table order
is the deterministic fallback order for other eligible profiles. Give each
profile a short task description. Explicit execution models and reasoning levels
must be supported by that runtime; `runtime-default` defers the choice to it.
Profiles describe allowed agents, not new authority. Keep the user-selected lead
model and explicit agent-model pins unchanged. Select agents deterministically
under [agent routing](agent-routing.md); no routing service is used.
Legacy `Routing` and `TypeSafe judgment model` fields are obsolete: ignore them
at dispatch and remove them during an authorized setup edit, preserving active
binding leases under the setup procedure.

### Monitoring (optional)

Omit Monitoring to check every 120 seconds. When present, `Poll interval
seconds` sets the `drain`
[Project Watcher](drain-scheduler.md#project-watcher) interval and must be a
positive number. It grants no authority. A mid-drain edit is ordinary
configuration drift under the existing rules; presentation-only renewal does
not cover it.

## Renew Presentation-Only Configuration

Execution may use this narrow exception when the trusted binding has already
changed on the verified committed base. It never edits a binding, trusted
instructions or the board. Use the same procedure at startup, before writes
and for active, planning, paused, parked and Wayfinder recovery leases.

1. Stop affected writers and new claims. Reconcile in-flight mutations and
   resource ownership; do not renew while a writer can still use the old lease.
   Retain every owner, assignment, draft, worktree, PR and historical record.
2. Load the old and new committed binding and trusted-reference identities,
   their digests, prior verified mappings and complete current live mappings.
   Require stable repository, Project, field, option and label identities.
   Permit only human-readable display-name changes attached to those same IDs.
   Prove unchanged lane meaning, selection/filter, priority order, role meaning,
   agent policy, base branch, authority, merge/closure/automation policy and
   [live merge-policy fingerprint](#live-merge-policy-fingerprint). Compare the
   entire binding, not just the renamed field; a same-ID rename alone is not
   proof of unchanged meaning. Missing old evidence, an uncommitted replacement,
   unknown equivalence, a changed ID or any semantic change stops the run.
3. Freshly revalidate membership, current role-label authority, exclusivity,
   source/plan and any amendment, retained artifacts/heads and grants for each
   affected lease. Screen base drift under the existing plan rules. A
   presentation change does not revive label-stopped work, pass qualification, alter
   a bounded grant, reset a repair budget or supply new invocation authority.
4. In the controller lane, publish one runner-authored issue record per affected
   ticket with `<!-- run-github-project:configuration-renewal:v1 -->`. Record
   old/new commits and configuration digests, stable IDs and old/new names,
   complete comparison and policy evidence, lease/artifact identities and
   predecessor renewal permalink/digest (or original lease for the root).
   Bind every retained historical marker by comment ID, permalink and
   [payload digest](../../to-plan/references/github-mode.md#payload-digest). Never edit that marker's original configuration digest.
   Reconcile an ambiguous create before retrying; refetch and verify exact
   author, body, payload digest and a single unforked, gap-free renewal lineage.
5. Renew the controller's effective leases only after every affected record is
   verified and each owner acknowledges the new lease before writing. Keep the
   old and new evidence plus the verified renewal links in the checkpoint;
   never silently replace history. Partial publication or acknowledgment keeps
   affected writes stopped until reconciled. Do not republish verified records.
6. On resume, reconstruct from original leases/markers and the complete verified
   renewal lineage. Refetch current identities and authority, and require the
   latest renewal's new digest to match the current committed binding. Retain
   the original marker payload and digest even after repeated renames. A cache
   or a renewal comment alone cannot prove equivalence or authorize execution.

For Wayfinder, normalize only this verified result through the optional
[configuration renewal binding](#wayfinder-configuration-renewal).
The ranker validates its marker/current-digest binding, not live semantics.
Without verified renewal, every existing exact-digest mismatch remains a stop.
An unchanged merge-policy fingerprint is mandatory; policy drift never uses
this route. Keep invalid or incomplete renewal as an integrity blocker, not a
parking or retry signal.

## Live Merge-Policy Fingerprint

At precondition validation, compute `sha256` over canonical JSON with sorted
object keys and sorted set-like arrays containing:

- the configured base branch and repository merge method or merge-queue mode;
- the live repository settings that permit that method;
- every active ruleset and branch-protection rule applying to the base, reduced
  to merge-queue requirements, required-review fields, and required-check names
  plus strictness; and
- the configured Done automation and the live Project workflow identities and
  enabled states that implement it.

Treat a failed or partial source read as unknown global state, not as a stable
fingerprint. Recompute the fingerprint before every merge, after a relevant
ruleset, branch-protection, repository-setting, merge-queue, or Project-workflow
event, and before resuming a parked implementation claim. A changed fingerprint
is global merge-policy drift: stop and preserve all work until the trusted
configuration and live policy are reconciled. Do not recompute it solely
because an unchanged parked claim appears in an otherwise fresh queue snapshot.

## Remote Reconciliation

Use this procedure for every GitHub read. In ordinary `setup`, apply steps 1,
2, and the `setup` branch of step 5. Approved legacy migration uses the complete
procedure plus its journal and original-state preconditions; exhausted access
returns `migration-blocked`. In `next` and `drain`,
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

## Unintended Closure

After a merge or discovery of an unexpected closure, compare actual issue
closures with the intended set recorded under the
[ticket lifecycle guard](ticket-lifecycle.md#pre-push-shepherd-and-merge).
For a controller-run PR proven to have closed an unintended issue with pending
work, reopen it, restore its last verified pre-closure Project Status, and leave
one explanatory comment linking the PR and remaining work. Perform and read back
each correction through the controller lane using the procedure above. Preserve
concurrent human changes; if cause, prior Status or write authority is uncertain,
report the exact repair needed and pause affected reconciliation rather than
guessing. Label-stopped recovery remains read-only under the controller's
[stop gate](authority-and-pauses.md#stop-on-label-removal); never restore its agent label. Do not report the issue Done or clean its retained work until
recovery is verified.

## Normalized Ticket Schema

Use the controller's [ranker invocation](normalized-ticket.md#ranker-invocation).

Normalize the fully resolved GitHub binding before ranking. For parent scope,
apply Parent-issue scope above; the Project-specific mapping below applies only
to board scope. `scopeParent` is an optional boolean identifying the selected
root's epic work shape; ordinary items omit it. It never supplies role authority.

Use the resolved exact live names (including overrides), IDs and effective binding
fingerprint from validation; absence of an override file is not missing state:

1. Map the Project item node ID to `itemId`, the issue URL to `itemRef`, and
   unresolved native blocker identities to `blockerRefs`. Preserve local issue
   numbers and cross-repository `owner/repository#N` references as opaque
   blocker values; include blockers outside the selected scope.
2. Supply `parked: false` for every GitHub item. GitHub has no parked column;
   unlabelled Todo is outside automatic work. Other bindings must supply their
   own parked gate, independently of role authority.
3. Pass `--agent-work-label` with the exact resolved agent-work role name;
   `ready-for-agent` below denotes that role, including its human-only grant.
   Pass `--claim-marker '{"status":"<configured In progress name>","requiresAssignment":true}'`.
   Use the exact configured column display name and authenticated runner login.
   Require only the resolved Todo, In Progress and Done options; derive
   implementation readiness from Todo, `ready-for-agent`, and a verified usable active plan leaf. Pass no
   Ready option or CLI input.
4. For `wayfinderReconciliation`, map the durable GitHub marker's
   `projectItemId` to normalized `itemId`; compare the same node ID without
   rewriting existing marker comments or their digests.

Provide every field below to `scripts/rank_tickets.py` from fresh, completely
paginated GitHub and Project reads. Before dispatch ranking, the controller
recovers [authority pauses](authority-and-pauses.md#recover-and-resume) and
retains active verified pauses in its separate frontier, outside the ranker's
active claims/candidates, as for parked CI claims. Apply the controller's
[readiness preflight](execution-controller.md#unattended-readiness) before
dispatch; the ranker does not inspect external access, host capabilities,
qualification receipts or execution grants. Keep those observations in existing
controller records, not invented CLI fields. Preserve unknown or unavailable
prerequisites as dispatch blockers even when the ranker returns a candidate.
Keep every paused issue in
the complete dependency graph used to hydrate blockers and descendants; never
erase a blocker to make a dependent runnable. Do not invent an authority flag
or pause field for this ranker CLI. Use this shape for execution contenders:

```json
{
  "number": 42,
  "title": "Short title",
  "itemRef": "https://github.com/owner/repository/issues/42",
  "state": "OPEN",
  "itemId": "PVTI_example",
  "parked": false,
  "projectStatus": "Todo",
  "projectPriority": "High",
  "projectPosition": 17,
  "labels": ["ready-for-agent"],
  "assignees": [{"login": "octocat"}],
  "blockerRefs": [41, "other/repository#7"],
  "openDescendants": [43],
  "replanRequest": null,
  "implementationPlans": [
    {
      "commentId": "IC_plan",
      "permalink": "https://github.com/owner/repository/issues/42#issuecomment-1",
      "author": "octocat",
      "digest": "<plan payload digest>",
      "createdAt": "2026-07-28T09:00:00Z",
      "publishedAt": "2026-07-28T09:00:00Z",
      "updatedAt": "2026-07-28T09:00:00Z",
      "plannedBranch": "main",
      "plannedSha": "0123456789abcdef",
      "markerVersion": 2,
      "revision": 1,
      "supersedes": null,
      "replanRequest": null,
      "isMinimized": false
    }
  ],
  "openPullRequests": [
    {
      "number": 91,
      "url": "https://github.com/owner/repository/pull/91",
      "author": "octocat",
      "closesIssue": true,
      "linksIssue": true,
      "headRepository": "owner/repository",
      "headRefName": "cb/issue-42",
      "headSha": "0123456789abcdef",
      "baseRepository": "owner/repository",
      "baseRefName": "main",
      "isDraft": false
    }
  ]
}
```

When Wayfinder is enabled, a configured Wayfinder child uses the Todo
shape above plus its direct parent and, for a task, its controller-derived mode:

```json
{
  "parentIssue": {
    "number": 7,
    "state": "OPEN",
    "projectStatus": "Todo",
    "labels": ["wayfinder:map"]
  },
  "labels": ["ready-for-agent", "wayfinder:research"],
  "implementationPlans": [],
  "wayfinderTaskMode": null,
  "wayfinderAfkEvidence": null
}
```

The parent must be the direct map parent, not an inferred ancestor. Hydrate its
current Project Status too; require a configured Todo-or-later column for the
parent before automatic map work or recovery. Missing or unknown parent Status
blocks the child. Require a human-applied agent role and a non-parked parent
before mutating it; a child never authorizes its map.
Use exactly
one configured type label. Research is AFK; prototype and grilling are HITL.
For a task, use `"afk"` only with non-empty fresh evidence that every action is
safely autonomous; use `"hitl"` or `null` for a human or ambiguous task.
Wayfinder children require the schema fields above, but no implementation-plan
entries or transition-history fields.

For an interrupted terminal reconciliation, add the normalized authoritative
marker below. Recovery inventory may supply a closed child, a closed parent,
and a Project item in Done or archived; it must still use fresh values and the
exact recorded Project item node ID.

```json
{
  "wayfinderReconciliation": {
    "commentId": "IC_reconciliation",
    "permalink": "https://github.com/owner/repository/issues/52#issuecomment-2",
    "author": "octocat",
    "createdAt": "2026-07-28T09:00:00Z",
    "markerVersion": 1,
    "disposition": "resolved",
    "mapNumber": 7,
    "itemId": "PVTI_example",
    "outcomePermalink": "https://github.com/owner/repository/issues/52#issuecomment-1",
    "configurationDigest": "sha256:configuration",
    "planDigest": "sha256:semantic-reconciliation-plan"
  }
}
```

The comment body retains the full planned-mutation list; the normalized form
contains the identifiers and digests the ranker validates. The marker must be
runner-authored, match the child Project item and direct map parent, match the
`--configuration-digest` passed for this invocation (or carry the exact verified
renewal below), and remain assigned only to that runner. Such a claim returns
`resume-wayfinder-reconciliation` before new Wayfinder work.
Use `resolved` only for a decision on the route and `out-of-scope` only for a
scope disposition. The recorded plan must place their linked gists in
`Decisions so far` and `Out of scope`, respectively.

### Wayfinder Configuration Renewal

Only after the controller verifies
[presentation-only renewal](#renew-presentation-only-configuration),
include these optional fields inside `wayfinderReconciliation`:

```json
{
  "payloadDigest": "<marker payload digest>",
  "configurationRenewal": {
    "commentId": "IC_renewal",
    "permalink": "https://github.com/owner/repository/issues/52#issuecomment-3",
    "author": "octocat",
    "markerCommentId": "IC_reconciliation",
    "markerPermalink": "https://github.com/owner/repository/issues/52#issuecomment-2",
    "markerPayloadDigest": "<marker payload digest>",
    "originalConfigurationDigest": "sha256:configuration",
    "configurationDigest": "sha256:renewed-configuration"
  }
}
```

Keep the marker's original `configurationDigest` unchanged. Compute
`payloadDigest` from its freshly read marker body under the
[payload digest](../../to-plan/references/github-mode.md#payload-digest) rule; retain every identity, configuration value and
planned mutation. The normalized renewal binds that payload, comment ID and permalink
to its original digest and the current CLI configuration digest. Require all
fields nonempty and its author to be the authenticated runner. A supplied
malformed, foreign, stale or mismatched renewal blocks recovery even when the
marker already has the current digest; omit renewal entirely when unnecessary.
Without renewal the original exact-digest rule is unchanged.

The controller must verify the durable record and full unforked renewal lineage,
committed semantic equivalence and live authority before normalization. For
repeated renames, supply the latest verified original-marker-to-current binding
only after verifying every intervening renewal and predecessor. The ranker
checks normalized identity consistency; it does not authenticate comments,
compare configuration semantics or grant access.

## Partial PR Recovery

For an intentionally non-closing implementation PR, include its non-closing
issue URL, approved plan permalink/digest and remaining work in the original PR
creation body. This makes intent recoverable even if the run stops before
publishing an authority pause. On recovery, verify that body against the current
claim and approved plan, authenticated PR author, exact head, repository/base
and complete competing-PR inventory. Then normalize `linksIssue: true`,
`closesIssue: false` and `verifiedPartial: true`; record the evidence with the
existing ownership record. `verifiedPartial` is an optional controller-derived
boolean, false when omitted; a bare issue mention or unverified body supplies
no proof. The ranker permits this exception only for a retained current-user
claim, never unclaimed adoption. Unknown or stale proof preserves a blocked
claim. Matching a partial PR authorizes neither live qualification nor merge;
repeat unattended readiness and the closing-reference guard at their gates.

## Other Ticket Shapes And Plan State

Use the same canonical shape for Todo triage contenders, with `replanRequest`
set to `null` and `implementationPlans` empty when absent. Their
`openPullRequests` entries need only `number`, `url`, and `closesIssue`; omit
execution-only author, draft, head, and base fields:

```json
{
  "number": 43,
  "title": "Unblocked issue awaiting triage",
  "itemRef": "https://github.com/owner/repository/issues/43",
  "state": "OPEN",
  "itemId": "PVTI_triage",
  "parked": false,
  "projectStatus": "Todo",
  "projectPriority": "High",
  "projectPosition": 18,
  "labels": ["needs-triage"],
  "assignees": [],
  "blockerRefs": [],
  "openDescendants": [],
  "replanRequest": null,
  "implementationPlans": [],
  "openPullRequests": []
}
```

Use that same Todo shape for configured epics, human work, and
`ready-for-agent` items already queued for planning. Preserve every exact
label. The ranker derives the work shape and next action from configured label
names; never add a synthetic role to its input.

Use GitHub logins, never display names, for assignees and PR authors when
GitHub is the tracker. For a GitLab tracker, authenticate the selected GitHub
code-host account and compare its immutable GitHub account ID with the PR
author's ID. Map an exact match to the verified GitLab tracker runner identity
used for assignees and `--current-user`. Keep other authors as distinct
GitHub-host-qualified identities. Missing or unverified author identity never
matches the runner. Preserve the original provider ID and login in the
delivery record. Normalize `labels` to exact label names. Normalize
`blockerRefs` and `openDescendants` entries to integer issue numbers for the
configured repository or `owner/repository#number` strings for cross-repository
issues; never pass GraphQL objects. Use a finite non-negative numeric Project
position. An empty PR array is valid.

Set `linksIssue` only from a freshly verified exact issue link in the PR; absent
or ambiguous evidence is false. Closing PRs already prove that link and may omit
the field. Under `close-after-merge`, a non-closing PR requires `linksIssue: true`
to resume; a branch name or historical report alone is insufficient. Keep all
other open implementation PRs in the array as competitors. The ranker defaults
to `closing-keyword` for compatibility; pass the binding's policy explicitly.

A human-applied role label plus `parked: false` supplies eligibility; current Project Status routes the lane. Do not hydrate status
history. `planningTransition`, `readyTransition`, and `backlogTransition` are
obsolete inputs: omit them; legacy values are ignored even when malformed,
foreign, automated, or missing. Check usable active-plan integrity and the
configured base rather than comparing publication times with column events.

Unlabelled Todo enters no automatic lane. Owned work missing `ready-for-agent`
is returned in `stoppedItems` before plan, PR or recovery hydration, with the
unchanged ticket, `stop-preserve` action and reason. Stop its writers, release
verified capacity and preserve assignment, Status, worktree, branch, PR and all
artifacts without cleanup or comment writes. Later runs remain stopped until a
human restores the label; the controller never adds or restores it. Keep all
dependency edges in the complete graph and report stopped work in the human frontier.

Hydrate every comment containing `<!-- to-plan:implementation-plan:v1 -->` or
`<!-- to-plan:implementation-plan:v2 -->`, including minimized comments, and
normalize it into `implementationPlans`. Require runner authorship. A v1
comment is a revision-one root. A v2
comment records its positive `revision`, predecessor permalink in
`supersedes`, triggering report permalink in `replanRequest` when applicable,
and payload publication time in `publishedAt`. Compute `digest` under the
[payload digest](../../to-plan/references/github-mode.md#payload-digest) rule, which
excludes the marker, revision metadata and any superseded wrapper, so
presentation-only edits do not invalidate history. Normalize a verified legacy
`previousPlanDigest` in a replan report to that rule's digest under the same
rule's legacy path, so an older report still matches its plan.

Require one root, contiguous revisions, one child per revision, and one
unminimized leaf. The ranker returns that leaf as the synthesized
`implementationPlan` in each selected ticket. Reject forks, gaps, duplicate
revisions, missing predecessors, foreign marker authors, and a minimized active
leaf. A verified runner-authored `autonomous-replan` report naming a plan's exact
permalink and payload digest invalidates that predecessor in every execution
column until a later revision links the report. Todo may plan its replacement;
In-progress work remains blocked; Todo cannot implement the invalidated leaf.
For compatibility, the ranker also accepts the former singular
`implementationPlan` input as one v1 root.

An integration amendment is not a synthetic implementation-plan revision or
ranker input field. Keep the original marked plan in `implementationPlans`;
the controller separately enforces the
[effective-contract gate](todo-lane.md#consume-a-verified-integration-amendment)
before dispatch, on recovery, observed authority changes and before external
material writes. The verified handoff covers in-scope local edits and tests.
Persist its verified lineage,
base/candidate identities and delivery evidence alongside the authority lease.
Unverified or unsupported amendments cannot make an otherwise blocked plan
usable, and a ranker selection cannot validate an amendment.

For an automatic requeue, normalize the verified report comment as:

```json
{
  "commentId": "IC_replan",
  "permalink": "https://github.com/owner/repository/issues/42#issuecomment-2",
  "author": "octocat",
  "createdAt": "2026-07-28T11:00:00Z",
  "disposition": "autonomous-replan",
  "previousPlanPermalink": "https://github.com/owner/repository/issues/42#issuecomment-1",
  "previousPlanDigest": "<plan payload digest>",
  "baseSha": "0123456789abcdef",
  "implementationHeadSha": "fedcba9876543210",
  "pullRequestUrl": null
}
```

A pending `human-required` decision stays in its original eligible column
under a verified authority pause, outside dispatch ranking. Explicit
abandonment cleanup must finish while the agent label remains, then transfer
to the human-work role in Todo. Label removal at any earlier point stops cleanup. Retained head and PR fields may be null but must identify
exact durable state when present. The replan report identifies its predecessor
plan and retained artifacts; no column-event ordering is required.

For Todo triage contenders, require the configured `needs-triage` label, no
assignee, and no open implementation pull request. Return an otherwise valid
item with open native blockers or descendants as `parkedBlocked`; return an
unblocked item as `triageCandidates`. Neither consumes an implementation slot.

For other role-labelled Todo work, apply
[Epics And Human Frontier](human-frontier.md). A bare epic is shape without a role and grants no automatic closure; keep `readyEpics` empty. Return unblocked human work as `humanActions`, and unblocked
`ready-for-agent` work in `candidates` with action `claim` when its active
plan is usable, or `plan` when planning is needed. Retain agent planning/handoff
assignment leases separately; among other roles, permit an existing assignee
only on human work. Role-tag dependency-blocked Todo results in
`parkedBlocked`. Reject contradictory roles, including agent plus epic. A role never overrides the binding's parked gate.

The ranker returns valid current-user claims and ordered unclaimed candidates:

```json
{
  "claimLimit": 3,
  "blockedClaims": [
    {"number": 39, "reasons": ["missing ready-for-agent label"]}
  ],
  "blockedPlanningClaims": [
    {"number": 40, "reasons": ["missing current implementation plan"]}
  ],
  "claims": [
    {"ticket": {"number": 41}, "action": "resume-implementation"},
    {"ticket": {"number": 42}, "action": "resume-planning-handoff"}
  ],
  "candidates": [
    {"ticket": {"number": 44}, "action": "resume-pr"},
    {"ticket": {"number": 45}, "action": "claim"},
    {"ticket": {"number": 46}, "action": "plan"},
    {"ticket": {"number": 49}, "action": "plan"}
  ],
  "wayfinderHumanFrontier": [
    {"ticket": {"number": 52}, "action": "resolve-wayfinder-hitl", "type": "grilling"}
  ],
  "wayfinderClaimedHitl": [
    {"ticket": {"number": 53}, "action": "resume-wayfinder-hitl", "type": "prototype"}
  ],
  "triageCandidates": [
    {"ticket": {"number": 47}, "action": "triage"}
  ],
  "readyEpics": [],
  "stoppedItems": [
    {"ticket": {"number": 48}, "action": "stop-preserve", "reasons": ["missing ready-for-agent label; human restoration required"]}
  ],
  "humanActions": [
    {"ticket": {"number": 50}, "action": "perform-human-work"}
  ],
  "parkedBlocked": [
    {
      "ticket": {"number": 51},
      "role": "human-epic",
      "reasons": ["blocked by ['owner/repository#41']"]
    }
  ],
  "excluded": []
}
```

Treat each `ticket` as the complete normalized object shown above. The
controller owns scheduling; the ranker only validates claims and orders
candidates. Each `blockedClaims` entry occupies a slot and preserves a claimed
implementation ticket that requires reconciliation. Todo claims and
`blockedPlanningClaims` preserve ownership but do not consume an implementation
slot; both still prevent the Todo triage tail from starting. Ready epics and
human actions consume neither slots nor agent capacity. Triage candidates are
ordered separately and run only through [Todo Triage Lane](triage-lane.md).
Process ready epics and human actions through
[Epics And Human Frontier](human-frontier.md); Todo `parkedBlocked` items consume
neither a slot nor an agent. `stoppedItems` also consumes neither once writers are quiesced; it never emits cleanup or label restoration.

When enabled in `next`, the ranker emits any eligible Wayfinder candidate as
`wayfind` and an assigned one as `resume-wayfind`. In `drain`, it emits only AFK
work in those collections and returns configured prototype, grilling, HITL,
and ambiguous task children in `wayfinderHumanFrontier` only while unassigned,
ordered by Priority, position, and issue number. It returns assigned eligible
HITL children separately in `wayfinderClaimedHitl`. A terminal recovery is
always an assigned `resume-wayfinder-reconciliation` claim in a configured
Todo-or-later column, including Done for interrupted terminal reconciliation.
New Wayfinder work requires Todo. None consumes an implementation slot. Route every form through
[Wayfinder Todo Lane](wayfinder-lane.md).

When `--wayfinder-ticket` is present in `next`, the output includes
`selectedWayfinderTicket` and returns only that child as new work. The ranker
rejects an absent or ineligible child, use in `drain`, and any selection that
would bypass another current-user claim.

Every human-facing consumer must render the complete ticket as
`[title](url)`. The abbreviated number-only objects above illustrate collection
shape, not permitted narration.

Before invoking the ranker, apply the drain scheduler's
[Terminal Required-CI Parking](drain-scheduler.md#terminal-required-ci-parking)
contract. Keep a parked implementation claim with an unchanged verified
observation fingerprint outside the normalized array and `max-claims` count. A
changed observation fingerprint triggers deep hydration but does not by itself
resume the claim or reset its repair budget. This inventory is distinct from
`blockedClaims` and Todo `parkedBlocked`; it blocks triage and successful
drain completion without occupying an implementation slot.

## GitHub access

Prefer the GitHub connector for issues, PRs, reviews, comments, threads, and CI;
use `gh project`/GraphQL only when Project operations require it. Before retry,
mutation, or success claim, apply [remote reconciliation](#remote-reconciliation).

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

## Project Watcher command

Run `python3 <run-project-skill-dir>/scripts/watch_project.py`; it stays
with the GitHub binding and runs only `gh api graphql` queries. Follow the
controller's [Project Watcher procedure](drain-scheduler.md#project-watcher)
for scheduling, baselines, relay capacity, deadlines and report handling.

```text
snapshot --project-id <Node ID> --repository <owner/name> --status-field <Status field name> [--pr <N>]... [--issue <N>]... > <baseline file>
```

Invoke that subcommand through the script above. For `wait`, use the same
scope/repository and watch set plus `--baseline <file>` and
`--deadline <ISO-8601>`; use configured `--interval <seconds>` when present.
For parent scope replace `--project-id` and `--status-field` with
`--parent-id <resolved issue node ID>`. The read-only query paginates every
sub-issue, dependency, label and assignee connection, reads through closed
intermediate parents, and follows transitive blockers outside the scope. It
fingerprints ordered sub-issue IDs, dependency IDs and states, labels,
assignment, identity and latest marker-comment change. Equal dependency counts
cannot hide replaced edges. Incomplete reads or identity ambiguity return an
error, never an unchanged/empty graph. `--board-from` preserves the same prior
scope graph for parent scope too.

For a targeted replacement, add `--board-from <prior baseline>` to
`snapshot` and pass repeatable `--refresh-pr <N>` for exactly the PRs covered
by the following authoritative read. Keep the complete watch set in `--pr`.
The snapshot queries those refresh PRs and newly watched PRs. It preserves
other prior PR fingerprints, including removed identities, as well as item
and issue fingerprints. `--refresh-pr` requires `snapshot --board-from` and
each refresh PR must be in `--pr`.

The PR fingerprint includes the aggregate check status and each check run and
status context on the observed head. The watcher reads every context page and
returns an error if the PR/head identity changes or a page is incomplete.
Treat check changes as a signal for an authoritative reread, where the
controller determines requiredness and readiness.

The default interval remains 120 seconds. This command never performs writes.

## Publish an authority pause

1. In the controller lane, publish one runner-authored issue comment containing
   `<!-- run-github-project:authority-pause:v1 -->`, the repository, issue and
   Project item IDs, effective binding fingerprint, base identity, exact
   blocked operation, missing authority or decision, and an observable resume
   condition. Include current Status and assignment, source and plan
   permalink/digest, PR URL, branch, head, and the
   [checkout ID](ticket-lifecycle.md#worktrees) when present. Explain which
   completed work is preserved. Use nulls for absent artifacts. Keep secrets,
   local paths, and unsanitized logs out of the comment.
2. Refetch the comment and live ticket/artifact state. Verify the authenticated
   runner author, identifiers, [payload digest](../../to-plan/references/github-mode.md#payload-digest), and existing authority lease
   when claimed. Reconcile ambiguous publication before retrying. Update the
   ticket only when that record is verified; report a failed write precisely
   and continue other safe work rather than claiming the update succeeded.

## Wayfinder reconciliation record

Post and refetch the resolution answer or scope-disposition comment. Before any
terminal mutation, compute one exact reconciliation plan covering the correct
map section, fog changes, child creates/updates/closes, parent-child and
dependency edges, Project additions, child terminal state, and possible map
completion. Post and refetch a durable runner-authored marker comment with this
machine-readable payload:

```json
{
  "markerVersion": 1,
  "disposition": "resolved",
  "mapNumber": 7,
  "projectItemId": "PVTI_child",
  "outcomePermalink": "https://github.com/owner/repository/issues/52#issuecomment-1",
  "configurationDigest": "sha256:configuration",
  "planDigest": "sha256:semantic-reconciliation-plan",
  "plannedMutations": [
    {"kind": "update-map", "issueNumber": 7, "digest": "sha256:map-body"}
  ]
}
```

Wrap it with the marker
`<!-- run-github-project:wayfinder-reconciliation:v1 -->`. Record every
mutation with a unique operation key and the exact intended state. For an
existing object, also record its stable node ID or issue number. For a new
issue, include the operation key in its marker-owned body so recovery can find
the result before retrying creation. Exclude presentation-only text from
`planDigest`. Assignment is the durable lease. Do not close the child, edit the
map, or perform another terminal mutation until the marker is authoritative.

## Execution prerequisites

Before ticket acceptance, confirm GitHub identity, applicable read/write access,
default/base branch, clean state and automation compatibility. Require Project
access only for Project scope; parent scope needs issue access.

## Claim implementation work

For Todo work with `ready-for-agent` and a verified usable active plan leaf,
wait for an implementation slot while preserving any planning assignment in
Todo. Once a slot is free, assign only the authenticated user, refetch
exclusivity, recover only own lost claim race, transition to In progress through
the scope's claim marker (Status for Project, label for parent scope),
refetch membership/status/assignment/open state/readiness/current plan/no blockers/no
competing PR, then record item, identity, configuration, and every plan
lease as authority. Keep `ready-for-agent` on the item throughout active work.
Ambiguity after In progress is a preserved blocked slot; verified label removal
instead invokes the stop gate and releases capacity once writers are quiesced.

## Claim Todo work

1. Enter the controller lane and refetch current `Todo` membership,
   `ready-for-agent`, non-parked state and exclusive next-action role. If the
   label is absent, stop and preserve under the label-stop gate. Assign exclusively to the
   authenticated user, refetch and verify the assignment, and release the lane. Reconcile an
   ambiguous Status or assignment mutation before retrying. Preserve the
   assignment through planning and implementation.

## Publish a fast-path plan

1. In the controller lane, publish one runner-authored
   `<!-- to-plan:implementation-plan:v2 -->` comment with revision one,
   `Supersedes: none`, `Replan report: none`, a `## Fast path` heading, the
   planned branch and base SHA, the classification evidence, the issue
   contract digest and the brief plan. Verify it under [Plan a Todo item](todo-lane.md#plan-a-todo-item) step 7,
   reconciling an ambiguous create by exact revision and digest.

## Publish a CI parking record

1. Publish one runner-authored issue comment containing
   `<!-- run-github-project:parked-implementation:v1 -->`, the issue and Project
   item IDs, PR URL, branch, head SHA and
   [checkout ID](ticket-lifecycle.md#worktrees), verified base SHA, effective
   binding fingerprint, and
   [live merge-policy fingerprint](#live-merge-policy-fingerprint),
   required-check names and conclusions, sanitized failure fingerprint, and the
   check-run IDs, heads, and fingerprints for all three rounds. Include the
   preserved assignment and `In progress` Status. Never include local paths,
   secrets, or unsanitized logs.

## Authority resume format

Publish the runner-authored issue comment with
`<!-- run-github-project:authority-resume:v1 -->`. Use the controller's
pause permalink/digest, instruction or decision evidence and current lease/artifact
identities. Preserve the controller's completed-external-merge branch, verification
and unknown-outcome rules.

## Replan request format

Publish the exact replan evidence packet in a new issue comment with
`<!-- run-github-project:replan-request:v1 -->`, then refetch and verify it.
Publication failure leaves the ticket In progress and its slot occupied.

## Resume parking format

Publish a runner-authored issue comment with
`<!-- run-github-project:resume-parked-implementation:v1 -->`, referring to the
parking permalink/digest and the controller's verified recovery evidence.
Keep its current-head, checks, base, configuration and merge-policy evidence;
an ambiguous write leaves the claim parked under the scheduler procedure.
