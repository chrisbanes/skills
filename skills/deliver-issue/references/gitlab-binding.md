# GitLab Binding

## Core principle

Translate the controller's decisions into verified GitLab operations. Select
the tracker and code host independently under [Delivery bindings](provider-bindings.md).
Each role uses its own verified project and account. Binding selection grants
no authority to claim, write, merge or close.

## Configuration

Use the existing sections of the controller’s trusted `docs/agents/deliver-tasks.md`. Add these fields to the existing sections for
a GitLab code host, keeping every other field (including the `Merge Policy`
Done automation fields a GitHub Project board needs):

```markdown
## Tracker

- Provider: `github`
- Repository: `<owner>/<repository>`

## Code host

- Provider: `gitlab`

## Repository

- Host: `<gitlab.com or self-managed host>`
- Repository: `<full project path, group/subgroup/project>`
- Project ID: `<numeric project ID>`
- Credential: `<glab:<host> or env:<VARIABLE>>`
- Default branch: `<branch>`
- Base branch: `<branch>`

## Merge Policy

- Method: `<merge, rebase_merge or ff>`
- Squash: `<true, false, or omitted for the project default>`
- Issue closure: `close-after-merge`
- Pipelines must succeed: `<true, false or unavailable>`
- Discussions must be resolved: `<true, false or unavailable>`
- Merge trains: `<enabled, disabled or unavailable>`
- Required approvals: `<rule summary, none or unavailable>`
```

- Resolve a GitHub tracker repository from the
  [shared tracker guide or delivery binding](provider-bindings.md#shared-repository-configuration).
  The GitLab checkout origin cannot identify it.
- `Project ID` is operator-supplied; setup may propose it from a read. Keep
  names beside IDs: the same Project ID under a new path is repairable drift
  (`configuration-blocked` for the whole run until setup reconciles the path);
  a path or ID that now resolves to a different project is `stop-preserve`:
  stop all work and preserve it.
- `Credential` names the source, never the value. `glab:<host>` uses the GitLab
  CLI login for that host. `env:<VARIABLE>` reads that variable at call time.
- `Squash` must be permitted by the project's `squash_option` (`always`
  requires `true`, `never` requires `false`). Omitted, use `true` for
  `default_on` and `false` for `default_off`.
- Select `closing-keyword` only for the eligible pair and base in
  [Link and close](#link-and-close). Use `close-after-merge` for mixed roles,
  different projects or non-default bases.

For a GitLab tracker, set the existing `Tracker` section independently:

```markdown
## Tracker

- Provider: `gitlab`
- Host: `<gitlab.com or self-managed host>`
- Repository: `<full project path, group/subgroup/project>`
- Project ID: `<numeric project ID>`
- Credential: `<glab:<host> or env:<VARIABLE>>`

## Scope

- Type: `<label or milestone>`
- Name: `<exact label name or milestone title>`
- ID: `<label or milestone ID>`

## Claim

- Label: `<agent:in-progress or trusted override>`
- Label ID: `<resolved label ID>`
```

For board runs require one configured selection. For direct and standalone
planning resolve a canonical issue URL or qualified reference against the
trusted tracker identity. Resolve a bare IID only against the bound tracker
project. Keep scope, claim and role names beside IDs. Apply the project drift
rules above to the tracker independently of the checkout. For controller runs,
resolve the `Triage` and `Work Roles` names under
[shared repository configuration](provider-bindings.md#shared-repository-configuration).
Fall back to the conventional names for undeclared roles. Record the effective
tracker identity, selection, resolved labels and account ID in the binding
fingerprint used by leases. Standalone `to-plan` uses the exact issue and any
mapped holds. It requires no board selection, claim label or agent-work label.
A rename requires configuration reconciliation. An identity substitution stops
the run. Omit GitHub Project fields and workflow settings for this tracker.

## Transport and credentials

1. Send every write and every decision-gating read through
   `glab api --hostname <Host> <endpoint>` (the REST API under
   `projects/<Project ID>/…`). Higher-level `glab` commands may display logs
   and summaries, never decide a gate. Paginate with `--paginate`.
2. Before any provider read, refuse to start the run when `GITLAB_TOKEN`,
   `GITLAB_ACCESS_TOKEN` or `OAUTH_TOKEN` is set in the environment, unless that variable is exactly
   the configured `env:<VARIABLE>` source; `glab` would otherwise use it
   instead of the configured source. For `env:<VARIABLE>`, pass its value to
   the `glab` child process only, as `GITLAB_TOKEN`.
3. Never print, log, store or include a credential value in records, PR/MR
   bodies, checkpoints or evidence. Report only the source name.
4. Verify `GET user` succeeds with the selected source before any write, and
   record the account ID and username.
5. A missing `glab` executable blocks the selected GitLab role's remote lanes.
   Keep independent work through the other binding and local validation.
   Resolve each role's identity with its own credential and reject credentials
   on foreign hosts. Keep both role preflights separate in a mixed pairing.
6. Treat any non-2xx response, timeout, malformed JSON or incomplete pagination
   as unknown state, never as absence. Retry reads and reconcile writes under
   [Reconciliation](#reconciliation).

## Tracker operations

### Scope and readiness

1. Verify the configured project by numeric ID and encoded path with
   `GET projects/:id` and `GET projects/<encoded path>`. Match the ID, path
   and host, require issues enabled, and establish the authenticated account,
   effective membership, visibility and operation-specific permissions.
   For controller runs validate all configured label IDs and names from fully
   paginated `GET projects/:id/labels?include_ancestor_groups=true`. Require the
   claim label to exist and differ from every selection and work-role label.
   Refuse ambiguous names, which issue updates address by name. For a milestone,
   resolve the selected title and ID through the project or inherited group
   milestone inventory (`GET projects/:id/milestones?include_ancestors=true`).
2. For board scope page
   `GET projects/:id/issues?scope=all&state=all&issue_type=issue`.
   Match exact label name or `milestone.id` locally against the verified
   selection. Include visible closed issues as graph evidence. Read an exact
   issue via `GET projects/:id/issues/:issue_iid` and match host, project ID,
   IID, immutable issue ID, type and canonical `web_url`; an IID alone is
   project-local. Read its full description, notes, linked specifications,
   parent context, blockers and their outcomes, and linked delivery records.
   A paginated inventory covers only items visible to the runner. An unknown
   selection or relevant visibility gap blocks the affected action.
3. For dependencies, establish the tier and link capability from trusted
   subscription/instance evidence. Directional blocking links require
   Premium or Ultimate. When supported, paginate
   `GET projects/:id/issues/:issue_iid/links`; use only the inward
   `is_blocked_by` relation. GitLab can omit links to issues the reader
   cannot see. Require current, independent evidence covering every possible
   related project and confidential issue for this exact source, such as an
   authoritative relationship inventory reconciled with the live read or a
   verified visibility boundary that includes every permitted link target.
   Source-project membership, a fully paged 200, and an empty list do not
   establish that coverage. Keep outside-selection blockers, and clear them
   only after a fresh exact-identity read verifies `closed`. A `relates_to`
   link supplies context. On a verified unsupported tier, mark blocking
   links unavailable and dependency completeness unknown. A denied, malformed,
   failed or partial read, or unproven relationship visibility, leaves
   completeness unknown. Record the distinct reason and block
   dependency-gated planning, claims, delivery and closure. Keep known unresolved references; never
   substitute an empty complete graph or invent edges. Check documented
   textual blockers as additional constraints.
4. Apply the holds, ownership, graph and plan checks. For standalone `to-plan`,
   accept the selected open issue under the user's planning request without
   requiring an agent-work label. Board planning requires the open issue's own
   human-applied agent-work role and no contradictory role. The direct-issue
   controller may accept the named open root and verified scope without an
   initial agent-work label if its invocation grants that branch. Preserve
   explicit stops in every mode and observed role removals for controller-owned
   work. A handoff inherits exactly one claim and its grant. Neither planner
   nor controller adds or restores the agent-work role.
5. For controller ranking, normalize to the shared ticket interface. Use the
   bound host and immutable issue ID for `itemId`, canonical issue URL for
   `itemRef`, IID for `number`, and authenticated host-qualified numeric identities for
   assignees and the runner. Use `parked: false`, null priority and stable
   IID order for positions. Closed maps to Done; open without a claim label
   maps to Todo, including an assignment-only planning lease. An open issue
   with the claim label requires exclusive runner assignment for In Progress.
   Preserve raw labels and pass
   `--claim-marker '{"label":"<resolved name>","requiresAssignment":true}'`.
   A foreign or non-exclusive assignment blocks the claim. Keep unknown-graph
   items out of runnable ranker input, accounting for their retained claims
   against capacity and preserving them in controller reconciliation. Only
   pass complete blocker and descendant data as such.

### Claim, stop and release

1. Before any material write or recovery, refresh the bound configuration,
   exact issue, graph, scope membership, state, labels, account/assignees and
   applicable grant. For an owned claim that disappears from selection, read
   the exact issue separately. Loss of the claim label on an owned open
   implementation issue or loss of its required agent-work role is
   `stop-preserve`: stop writers before releasing capacity, preserve the
   assignment, plan and all artifacts, and keep a durable stop receipt.
   Never recreate the claim or restore the role to continue. A verified
   scope departure with both labels intact, changed assignment or unknown
   read blocks and preserves the claim and slot. Check stops before hydrating
   plans or interpreting assignment as a new lease.
2. Within the controller's serialized claim lane, require open state,
   complete graph, applicable role/plan gates, an absent claim label and
   either no assignee or exactly the runner under its verified lease.
   Use one `PUT projects/:id/issues/:issue_iid` with `add_labels` set to
   the verified claim name and `assignee_ids: [<runner ID>]`. A planning
   reservation uses only the assignment under its separate grant. Refetch
   the exact issue and verify the intended label and exclusive assignment
   before dispatch. GitLab does not offer a conditional assignment update
   here. Refuse a stale or conflicting snapshot; if a concurrent change or
   partial effect is observed, preserve it and reconcile before dispatch.
3. For an explicitly authorized release of a verified, still-owned lease,
   remove only its claim label with `remove_labels` and clear only the
   verified exclusive assignment owned by the lease using `assignee_ids: []`.
   Never run release as a response to a human stop. Verify the resulting state;
   retained planning assignments need their own disposition. Reconcile
   ambiguous effects through a fresh issue read before any retry.

### Planning marker operations

1. For `read-markers`, paginate `GET projects/:id/issues/:issue_iid/notes`.
   Return exact decoded marker bodies, immutable note IDs, permalinks
   (`<issue web_url>#note_<id>`), author IDs and timestamps. Exclude system
   notes from marker candidates; retain other notes as source evidence.
   Authenticate marker authors and verify the shared revision/predecessor
   and digest protocol, including handoffs and amendments. Pagination
   order, timestamps and presentation cannot choose the active leaf.
2. For `write-marker`, POST one `body` to the issue notes endpoint under the
   specific grant. GitLab executes and removes quick actions and normalizes
   CR and trailing whitespace on save. Require LF text, refuse quick-action
   command lines, and append exactly one LF followed by
   `<!-- gitlab-binding:end-marker -->`. Reject a payload containing that
   reserved footer. Strip that exact suffix on readback before hashing or
   comparing; this protects trailing payload whitespace. Read unframed
   historical markers as stored and require their recorded digest to verify.
   Refetch through `read-markers` and verify exact decoded body, author,
   permalink, digest and unique revision/sequence and predecessor. For
   ambiguous creation, reconcile by those facts and reuse only a unique
   authorized result. A competing leaf or changed payload blocks handoff.
3. For `supersede-marker`, verify the successor and unchanged predecessor
   digest through the complete chain, then leave the predecessor visible.
   This binding has no supported presentation-only mutation. Return a
   presentation warning if supersession requested one; the new verified
   leaf owns authority without editing historical notes.

### Link and close

1. Read related and closing GitLab MRs through the issue's paginated
   `related_merge_requests` and `closed_by` endpoints. For delivery,
   verify the exact source URL and recorded change request through the
   selected host. With tracker note authority, create one issue note with
   the canonical PR/MR URL as a plain delivery link and refetch it by note
   ID, author and exact link. Reuse the verified runner-owned match on
   resume. An unknown link outcome blocks any operation that requires it.
2. Use native closure only when both roles resolve to the same GitLab host
   and project ID as the exact eligible issue, the MR targets the verified
   default branch, the tracker project's `autoclose_referenced_issues` is
   verified true, and all shared closure gates hold. Verify the merge account
   can close that issue. Use an exact issue reference such as `Closes #<iid>`
   in that project's MR. On GitHub or another host, a different GitLab
   project, a non-default base, partial delivery or absent authority, use a
   non-closing source link and `close-after-merge`. Never translate a
   GitLab IID to a code-host issue number. Verify the host's complete
   closing set using the shared procedure.
3. Read back native closure from the exact issue and its paginated
   `resource_state_events`, comparing the intended closure set and
   reconciling attribution against the verified merge. For a tracker close,
   require the owning controller or authorized standalone lead to verify the
   fresh tracker grant, open issue and full acceptance, with complete blocker
   and descendant evidence and no remaining work. Apply the verified merge,
   head and base gates for `close-after-merge`, or the shared
   [verified no-change closure](provider-bindings.md#verified-no-change-closure)
   gates for already-satisfied work. Capture the pre-write
   state event boundary, then send only `state_event: close` in
   `PUT projects/:id/issues/:issue_iid`. Require fresh `closed` readback and
   one matching new close event attributable to this write. External or
   ambiguous closure stays pending reconciliation. For a proven unintended
   closure, only the authorized owner may reopen using `state_event: reopen`
   against verified unchanged state, then verify the issue and event. If
   attribution, grant or preconditions are unknown, preserve and report it.

### Tracker availability and finish gate

- Verified lack of directional blocking links blocks all dependency-gated
  lanes. Continue independent read-only discovery and local checks.
- This REST binding does not establish a complete work-item hierarchy. Block
  operations requiring descendant completeness unless a trusted, current
  complete inventory verifies the graph for the exact item. Never infer
  an empty hierarchy from a paginated issue or relation list.
- Native closure is unavailable outside the verified pair and default base.
  Use controller closure only within its separate grant and readback gates.
- Unattended tracker wake, GitHub Project migration, Project-field Wayfinder
  writes and applied triage without a verified GitLab operation contract are unavailable. Finish eligible work and return the
  pending refresh or unsupported lane; never run the GitHub watcher.

Finish with exact identities, last verified state, effects, preserved claims
and the next reconciliation condition. Report verified merge separately from
verified tracker Done.

## Code-host operations

Each operation names its REST call. `:id` is the configured Project ID; `:iid`
is the merge request IID.

1. **Identity and checkout:** `GET projects/:id` and
   `GET projects/<url-encoded path>` must return the same project, with
   `path_with_namespace` equal to `Repository` and the live `default_branch`.
   The checkout's `origin` (https or ssh form) must name `Host` and
   `Repository`. Match any configured `Default branch` to the live value.
   Use the trusted `Base branch` when supplied and the live `default_branch`
   otherwise. Verify the selected branch and its exact tip SHA through
   `GET projects/:id/repository/branches/<url-encoded branch>` before planning or choosing
   a checkout. Any mismatch blocks under the drift rules above.
2. **Find or open a merge request:** Merge requests come only from task
   branches in the configured project, never forks. Before create, list
   `GET projects/:id/merge_requests?source_branch=<branch>&target_branch=<base>&state=all`
   and reuse the verified existing request. Otherwise
   `POST projects/:id/merge_requests` with `source_branch`, `target_branch`,
   `title` prefixed `Draft: `, and `description`. Never send
   `merge_when_pipeline_succeeds` or `auto_merge`.
3. **Update:** `PUT projects/:id/merge_requests/:iid` with only the changed
   `title` or `description`. Preserve unrelated human edits by refetching
   first.
4. **Exact head and base:** `GET projects/:id/merge_requests/:iid`; record
   `iid`, `web_url`, `sha` (head), `diff_refs.base_sha`, `target_branch`,
   `source_branch`, `draft`, `state`, `has_conflicts`, `detailed_merge_status`, `head_pipeline`,
   `source_project_id` and `target_project_id`. Both project IDs must equal
   the configured Project ID. The returned IID and target branch must match
   the request, and the reviewed head must equal `sha`.
5. **Checks:** Read every page of
   `GET projects/:id/merge_requests/:iid/pipelines`. Reject foreign refs and
   conflicting project IDs. Use only the verified MR-scoped list for
   membership, never a project-wide SHA search. Consider both pipelines with
   the exact head `sha` and either the MR's source branch or
   `refs/merge-requests/<iid>/head`, and pipelines with
   `refs/merge-requests/<iid>/merge`. Select the newest of these before
   checking its status or resolving its identity. Require its ID.
   For a merged-results pipeline, require the ID, ref and temporary merge SHA
   to match `head_pipeline` from operation 4 at the reviewed head. If that
   evidence is missing or disagrees, refresh the MR and reverify its identity
   and head under operation 4. If the reads still disagree or are incomplete,
   keep checks pending. Never fall back to an older pipeline. If the head
   changes, requalify it.
   Read every page of `GET projects/:id/pipelines/:pipeline_id/jobs` for the
   selected ID. If the responses include project or pipeline IDs, they must
   match the request scope.

   Pass only with a successful pipeline and no blocking jobs. For an unrun
   manual job, use the effective API value: `allow_failure: true` leaves an
   otherwise passing pipeline eligible unless the repository requires the job,
   and `allow_failure: false` keeps delivery pending. A blocked or manual
   pipeline remains pending regardless of the project's merge policy. Report
   failed, running, canceled or unknown checks as such. Missing or incomplete
   evidence, including unknown manual-job policy or no pipeline for the
   reviewed head, leaves checks pending or unknown.
6. **Reviews and feedback:** Review state is discussions plus approvals. Read
   `GET projects/:id/merge_requests/:iid/discussions` (every page) and record
   each resolvable discussion's ID, notes, author and `resolved` state. Read
   `GET projects/:id/merge_requests/:iid/approvals` for `approved_by`,
   `approvals_required` and `approvals_left` where the tier exposes them;
   missing fields are `unavailable`. GitLab review transport does not replace
   independent integrated review.
7. **Reply and resolve:** Reply with
   `POST projects/:id/merge_requests/:iid/discussions/:discussion_id/notes`
   (`body`). Resolve with
   `PUT projects/:id/merge_requests/:iid/discussions/:discussion_id`
   (`resolved=true`) only after the reply and any required push succeed, then
   refetch the discussion. Never resolve a local-only fix.
8. **Draft and readiness:** A new request is a draft through its `Draft: `
   title prefix. Mark ready with `PUT projects/:id/merge_requests/:iid`
   removing that prefix, then read back `draft: false`. Return to draft by
   restoring the prefix. Change readiness only within caller authority under
   [PR review timing](../../shepherd/references/pr-review-timing.md).
9. **Source link and closing references:** Put the exact tracker URL in the
   description as non-closing text unless [Link and close](#link-and-close)
   and the shared closure gates select native closure. After every create or
   description edit and immediately before merge, page
   `GET projects/:id/merge_requests/:iid/closes_issues`. Resolve each entry
   to its exact host/project/issue identity. A successful read can omit
   unreadable issues, including manually linked closures that persist after
   access is lost. Independently establish the complete effective set for
   this exact MR, head and base. Use an independently reconciled inventory
   or authoritative evidence that the read covers every target and record type.
   Include effective closing directives in the description, commits and merge
   text, and all manual closing links, including cross-project and confidential
   targets. An
   apparent exact match, an empty result, and a non-default base do not
   prove completeness. Compare the complete set to the intended native
   set or the required empty set for controller closure. Unproven
   completeness or unintended references block acceptance and merge.
   Recheck corrected readback and its coverage before proceeding.
10. **Merge:** Refresh operations 4–6 and 9 and the
    [live merge-policy fingerprint](#live-merge-policy-fingerprint). Require
    invocation-specific merge authority, the caller's final-head gates,
    `detailed_merge_status` equal to `mergeable`, `draft: false`,
    `has_conflicts: false` and `sha` equal to the expected head. Re-read
    transient statuses (`checking`, `unchecked`, `preparing`) with bounded
    polling; a fresh draft can report `checking` rather than `draft_status`.
    Any other status refuses with zero writes and reports GitLab's status.
    Require a verified train policy before sending exactly one merge write
    with `sha=<expected head>` and `squash` from the policy. Use
    `PUT projects/:id/merge_requests/:iid/merge` only when trains are
    explicitly disabled. When enabled or required, use operation 11.
    If the policy is unknown or contradictory, report it and send no merge
    write. Never set auto-merge. On a direct merge SHA mismatch, refetch the
    MR and qualify the new head under all applicable gates before considering
    another merge.
11. **Merge trains:** When the fingerprint shows merge trains enabled, a direct
    merge would bypass the train or be rejected, so merge by adding the request
    with `POST projects/:id/merge_trains/merge_requests/:iid`, omitting
    `auto_merge` so it joins immediately; that is the only train interaction.
    A 202 (scheduled for later) is unexpected: stop and reconcile.
    The delivery stays `pending` while
    `GET projects/:id/merge_trains/merge_requests/:iid` or the request's state
    shows it on the train. It is merged only after readback; a request that
    leaves the train unmerged is `blocked` with GitLab's reason.
12. **Merge readback:** `GET projects/:id/merge_requests/:iid` must show
    `state: merged`, the expected head, and a `merge_commit_sha` or
    `squash_commit_sha` reachable from the refreshed base
    (`GET projects/:id/repository/branches/<base>`). A fast-forward merge
    (`ff` without squash) has neither; require the expected head itself to be
    reachable from the base instead. Then return merge
    evidence to the tracker binding for terminal readback or authorized
    `close-after-merge`. GitLab may delete the source branch on merge; treat a missing
    source branch after verified merge as cleaned up.
13. **Linked merge requests for the board ranker:** Discover open requests in
    the project whose description contains the exact canonical tracker URL, or
    whose source branch is the recorded task branch. Normalize each into the
    ranker's existing `openPullRequests` entry: `number` = `iid`, `url` =
    `web_url`, `author` = the ranker's current-user identity when the MR
    author's account ID equals the verified runner account from `GET user`,
    otherwise `gitlab:<username>` so it never matches a tracker login,
    `headRepository` and
    `baseRepository` = project path, `headRefName`, `headSha`, `baseRefName`,
    `isDraft`, and `closesIssue` from the verified effective set for the
    exact tracker item. Set `linksIssue` from the exact canonical URL or a
    verified delivery record binding this task branch to the exact item.

## Unavailable operations

| Operation | Lanes blocked |
| --- | --- |
| Merge requests from forks | Delivery from a fork; use project task branches |
| Auto-merge | None; merge only through operations 10–11 |
| Approval reads on tiers without them | None by itself; record `unavailable` |

Return an unavailable operation precisely. Never fall back to `gh` or another
host for a GitLab target.

## Setup

`setup` makes no GitLab writes. For a GitLab tracker, run the read-only
identity, account, scope and role validation, resolve capabilities and read the
tracker Done inputs below. Propose missing values through additive setup;
report missing labels or unavailable capabilities without creating labels.
For a GitLab code host, apply the credential checks above, then read `GET projects/:id` (or the path when the ID
is not yet known), the default and base branches
(`GET projects/:id/repository/branches/<branch>`), merge settings,
`GET projects/:id/protected_branches`, `GET version` and, unless it reports
Community Edition, `GET projects/:id/approval_rules` and
`GET projects/:id/approvals`. Propose `Repository`, `Project ID`,
`Credential`, branches and `Merge Policy` values from those reads under the
board controller’s additive setup procedure.
If bounded access retries end during setup, report `configuration-blocked`.
Finish with the applicable validation or proposed-edit result.

## Live Merge-Policy Fingerprint

Use the verified base from code-host operation 1. Use the configured
`Method` when it matches the project's live `merge_method`, or the live
method when omitted. Resolve `Squash` under [Configuration](#configuration)
and closure under [Link and close](#link-and-close). Record the resolved
policy and applicable gates for the controller.

Compute and recompute it as the
[GitHub fingerprint](github-delivery.md#live-merge-policy-fingerprint) does,
with `sha256` over canonical JSON containing:

- the base branch, the configured `Method` and `Squash`;
- from `GET projects/:id`: `merge_method`, `squash_option`,
  `only_allow_merge_if_pipeline_succeeds`, `allow_merge_on_skipped_pipeline`,
  `only_allow_merge_if_all_discussions_are_resolved`, `merge_trains_enabled`
  and `merge_pipelines_enabled`;
- the protected-branch rules matching the base, reduced to push and merge
  access levels, `allow_force_push` and `code_owner_approval_required`; and
- approval rules (name, type, `approvals_required`, eligible approver IDs) and
  approval settings where the tier exposes them;
- the selected tracker's verified Done policy, even for a mixed pairing.
  For GitLab, include tracker host/project ID, live `default_branch`,
  `autoclose_referenced_issues` and any configured Done workflow's identity
  and live enabled state. Closed already maps to Done without a board
  transition. Record `none` for other Done automation only when its absence
  is verified against the trusted binding and applicable automation
  inventory. An unknown required setting or workflow is never an absence.

A field that is `null` or absent in a complete 2xx read records the stable
value `unavailable`. Decide endpoint availability by edition, not status code:
when `GET version` reports `enterprise: false` (Community Edition), the
approval endpoints are `unavailable` and are not read. Otherwise a failed or
partial read is unknown state: stop with `stop-preserve`, never fingerprint
it, and never read a 403 or 404 as `unavailable`. Required tracker Done
inputs follow the same unknown-read rule. Recompute on relevant policy changes,
before merge and before resuming a parked claim. A changed fingerprint is
global merge-policy drift (`stop-preserve`), handled as in the GitHub binding.

## Reconciliation

Apply steps 2–5 of the GitHub binding's
[Remote reconciliation](github-delivery.md#remote-reconciliation) to every
GitLab read and write. Reconcile a failed or ambiguous write from the merge
request by source branch, the note by discussion or exact issue marker/link,
the discussion's `resolved` state, the issue's labels, assignees and state
events, or the merge request's `state`. An unknown result stops the dependent
lane; never send a duplicate.
