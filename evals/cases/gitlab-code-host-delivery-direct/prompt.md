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

- `mr-open`: No merge request exists for the task branch. Open one and link it.
- `pipeline-failed`: The head pipeline failed on a non-optional job.
- `not-mergeable`: The pipeline passed, but GitLab reports an unresolved
  discussion requesting a code change.
- `mergeable`: Every gate passes at H1 and no merge has been sent.
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

Explain each decision briefly in your response.
