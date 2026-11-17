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
- `not-mergeable`: The pipeline passed, but GitLab reports an unresolved discussion.
- `mergeable`: Every gate passes at H1 and no merge has been sent.
- `merge-train`: The project uses merge trains; the authorized merge call was
  sent and accepted, and the request is on the train.
- `merged`: Readback shows the request merged at H1 with its commit on `main`;
  the GitHub issue is still open.

Explain each decision briefly in your response.
