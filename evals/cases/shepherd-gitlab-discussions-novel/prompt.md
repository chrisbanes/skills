Use only the immutable snapshots in `gitlab-state.json` to decide each GitLab
merge-request discussion action. Do not contact providers, push, or change
repository files. The target is a GitLab merge request (origin on
`gitlab.example.com`); the user asked you to keep it moving, including replies,
pushes and thread resolution. Each fix is in scope and its affected checks pass.

Write `.scratch/review-decisions.json`, keyed by snapshot ID, with exactly these
fields: `cli` (the CLI used for the target), `reply` (boolean: post or keep the
in-thread reply), `resolve` (boolean: resolve the discussion now), `fallback`
(`none` or the other CLI you would use) and `report` (`none` or `unavailable`).

- `reply-push-ok`: The fix was pushed and the reply posted.
- `local-only`: The fix is committed locally but not pushed yet.
- `push-failed`: The push of the fix was rejected.
- `answer-only`: A question needs only an in-thread answer, which was posted.
- `unavailable-op`: The fix was pushed and the reply posted, but this instance
  rejects the resolve endpoint.

Explain each decision briefly in your response.
