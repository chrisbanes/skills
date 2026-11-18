Use only the immutable snapshots in `gitlab-state.json` and below to assess the
next provider operations. Do not contact providers, run delivery, or change
repository files. Write `.scratch/review-decisions.json`, keyed by snapshot ID,
with exactly these fields per snapshot: `tracker`, `code_host`, `change_action`
(`open_draft`, `update`, `repair` or `none`), `closing_keywords` (boolean),
`expected_host_closures` (array), `merge_permitted` (boolean: may an authorized
merge call be sent now), `tracker_action` (`link`, `close_and_verify` or `none`),
`ticket_complete` (boolean) and `delivery_state` (`pending`, `merged` or
`blocked`).

Trusted configuration: tracker `github` with Repository `acme/app`; code host
`gitlab`, Host `gitlab.example.com`, Repository `acme/platform/app`, Project ID
`88001`, Credential `glab:gitlab.example.com`, base `main`, issue closure
`close-after-merge`. The source is https://github.com/acme/app/issues/42; it has
no GitLab issue counterpart. All reads in the file are complete 2xx responses,
the merge-policy fingerprint is unchanged, the credential checks passed, local
checks and independent review passed for head H1, and the standalone lead has
merge and tracker-closure authority. The full contract is satisfied by H1.
Where present, the independent closing inventory is current for the recorded
project, MR, head, and base. It covers directives in the description, commits
and merge text, plus all manual links across projects and confidential issues.
A successful endpoint response on its own does not establish that coverage.

- `mr-open`: No merge request exists for the task branch. Open one and link it.
- `pipeline-failed`: The head pipeline failed on a non-optional job.
- `not-mergeable`: The pipeline passed, but GitLab reports an unresolved
  discussion requesting a code change.
- `mergeable`: No merge has been sent. All gates other than the candidate
  checks pass at H1. Use the selected pipeline and job responses to decide
  whether checks pass.
- `merge-train`: This snapshot's project uses merge trains (its own
  `merge_policy` replaces the top-level one, and the recorded and live
  fingerprints both match it); the authorized merge call was sent and
  accepted as a merge-train add, and the request is on the train.
- `merged-results`: This snapshot's project runs merged-results pipelines (its
  own `merge_policy` applies and matches the fingerprints). The only pipeline
  tests a temporary merge commit `MR1`, not H1; it succeeded and is the merge
  request's `head_pipeline` at H1. Every other gate passes and no merge has
  been sent.
- `merged`: Readback shows the request merged at H1 with its commit on `main`;
  the GitHub issue is still open.

Include each ID in `pipeline_variants` as a separate decision. For each
variant, start with its `base_snapshot`, replace only the supplied top-level
fields, and apply `merge_request_overrides` to the named MR fields, if supplied.
Any variant's `merge_policy` replaces the top-level policy and matches both
fingerprints. The `pipelines` and `jobs` arrays are the complete responses
from the MR pipeline and selected pipeline jobs endpoints, respectively.
When supplied, `refreshed_merge_request` is the response to a second MR
read after listing pipelines, and `jobs_by_pipeline_id` gives the complete
jobs response for each listed pipeline instead of the default `jobs`.

Explain each decision briefly in your response.
