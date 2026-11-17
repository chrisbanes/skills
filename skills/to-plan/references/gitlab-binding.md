# GitLab Binding

## Core principle

Translate the controller's decisions into verified GitLab code-host operations;
this binding supplies no selection, mutation, merge or closure authority of its
own. GitLab is supported only as the **code host**. A GitLab repository never
implies a GitLab tracker: pair it with a supported tracker binding, such as the
[GitHub binding](github-binding.md#delivery-operations), selected independently
under [Delivery bindings](provider-bindings.md).

## Tracker role

A `gitlab` tracker has no trusted operation contract yet. Block every tracker
lane (source/readiness, markers, claims, linking, closure, Done) with
`configuration-blocked`, naming the missing contract. Do not substitute
GitHub commands or invent GitLab issue operations.

## Configuration

Use the existing `docs/agents/deliver-tasks.md` shape from the
[GitHub Project configuration](github-binding.md#github-project-configuration);
there is no GitLab-only section. Add these fields to the existing sections for
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

- `Tracker` `Repository` is required when the tracker is `github`, because the
  GitLab checkout origin cannot identify the tracker repository.
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
- `Issue closure` is always `close-after-merge` while GitLab is only the code
  host.

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
5. A missing `glab` executable is a capability gap, not invalid
   configuration: it blocks only the code-host lanes. Tracker reads, planning
   and local validation continue.
6. Treat any non-2xx response, timeout, malformed JSON or incomplete pagination
   as unknown state, never as absence. Retry reads and reconcile writes under
   [Reconciliation](#reconciliation).

## Code-host operations

Each operation names its REST call. `:id` is the configured Project ID; `:iid`
is the merge request IID.

1. **Identity and checkout:** `GET projects/:id` and
   `GET projects/<url-encoded path>` must return the same project, with
   `path_with_namespace` equal to `Repository` and the live `default_branch`.
   The checkout's `origin` (https or ssh form) must name `Host` and
   `Repository`. Any mismatch blocks under the drift rules above.
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
   the configured Project ID. The reviewed head must equal `sha`.
5. **Checks:** Pipelines are checks. Read
   `GET projects/:id/merge_requests/:iid/pipelines` and select the latest
   pipeline for the head: one whose `sha` equals the head, or a merged-results
   pipeline (`ref` `refs/merge-requests/<iid>/merge`, which tests a temporary
   merge commit with a different `sha`) only when it is the `head_pipeline` of
   operation 4's readback at that head. Read its jobs with
   `GET projects/:id/pipelines/:pipeline_id/jobs`. A job with
   `allow_failure: true` or a manual job is non-blocking unless the repository
   says otherwise. Report `success`, `failed`, `pending`/`running`, `canceled`
   or unknown; no pipeline for the head is pending, not passing.
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
   [PR review timing](pr-review-timing.md).
9. **Source link and closing references:** Put the tracker's canonical URL in
   the description as plain non-closing text (`Source: <URL>`). Never write
   GitLab closing patterns (`Closes`, `Fixes`, `Resolves`, `Implements` and
   their variants) while GitLab is only the code host. After every create or
   description edit and immediately before merge, read
   `GET projects/:id/merge_requests/:iid/closes_issues` as the host's effective
   closing-reference set; with no native closure it must be empty under
   [Delivery bindings](provider-bindings.md) step 5.
10. **Merge:** Refresh operations 4–6 and 9 and the
    [live merge-policy fingerprint](#live-merge-policy-fingerprint). Require
    invocation-specific merge authority, the caller's final-head gates,
    `detailed_merge_status` equal to `mergeable`, `draft: false`,
    `has_conflicts: false` and `sha` equal to the expected head. Re-read
    transient statuses (`checking`, `unchecked`, `preparing`) with bounded
    polling; a fresh draft can report `checking` rather than `draft_status`.
    Any other status refuses with zero writes and reports GitLab's status. Then
    send exactly one merge write with `sha=<expected head>` and `squash` from
    the policy: `PUT projects/:id/merge_requests/:iid/merge` without merge
    trains, or operation 11's train add with them. Never set auto-merge.
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
    evidence to the tracker binding for `close-after-merge`; GitLab closes
    nothing. GitLab may delete the source branch on merge; treat a missing
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
    `isDraft`, `closesIssue: false` and `linksIssue: true`.

## Unavailable operations

| Operation | Lanes blocked |
| --- | --- |
| Native closure through closing keywords | None; closure uses `close-after-merge` |
| Merge requests from forks | Delivery from a fork; use project task branches |
| Auto-merge | None; merge only through operations 10–11 |
| Approval reads on tiers without them | None by itself; record `unavailable` |

Return an unavailable operation precisely. Never fall back to `gh` or another
host for a GitLab target.

## Setup

`setup` supports a GitLab code host and makes no GitLab writes. Apply the
credential checks above, then read `GET projects/:id` (or the path when the ID
is not yet known), the default and base branches
(`GET projects/:id/repository/branches/<branch>`), merge settings,
`GET projects/:id/protected_branches`, `GET version` and, unless it reports
Community Edition, `GET projects/:id/approval_rules` and
`GET projects/:id/approvals`. Propose `Repository`, `Project ID`,
`Credential`, branches and `Merge Policy` values from those reads under the
GitHub binding's [additive setup](github-binding.md#additive-setup-for-an-existing-repository).
Finish with the applicable validation or proposed-edit result.

## Live Merge-Policy Fingerprint

Compute and recompute it as the
[GitHub fingerprint](github-binding.md#live-merge-policy-fingerprint) does,
with `sha256` over canonical JSON containing:

- the base branch, the configured `Method` and `Squash`;
- from `GET projects/:id`: `merge_method`, `squash_option`,
  `only_allow_merge_if_pipeline_succeeds`, `allow_merge_on_skipped_pipeline`,
  `only_allow_merge_if_all_discussions_are_resolved`, `merge_trains_enabled`
  and `merge_pipelines_enabled`;
- the protected-branch rules matching the base, reduced to push and merge
  access levels, `allow_force_push` and `code_owner_approval_required`; and
- approval rules (name, type, `approvals_required`, eligible approver IDs) and
  approval settings where the tier exposes them.

A field that is `null` or absent in a complete 2xx read records the stable
value `unavailable`. Decide endpoint availability by edition, not status code:
when `GET version` reports `enterprise: false` (Community Edition), the
approval endpoints are `unavailable` and are not read. Otherwise a failed or
partial read is unknown state: stop with `stop-preserve`, never fingerprint
it, and never read a 403 or 404 as `unavailable`. A changed fingerprint is
global merge-policy drift (`stop-preserve`), handled as in the GitHub binding.

## Reconciliation

Apply steps 2–5 of the GitHub binding's
[Remote reconciliation](github-binding.md#remote-reconciliation) to every
GitLab read and write. Reconcile a failed or ambiguous write from the merge
request by source branch, the note by discussion, the discussion's `resolved`
state or the merge request's `state`; never send a duplicate.
