Assess the supplied immutable startup snapshots for a Project board run in
read-only mode. Do not query providers or perform operations. The trusted
committed configuration and each snapshot are in `gitlab-state.json`. Unless a
snapshot says otherwise, the checkout origin matches the configured host and
path, no credential override variable is set, `glab` is installed, every read
is a complete 2xx response and live values equal the recorded fingerprint
inputs.

Write `.scratch/review-decisions.json`, keyed by snapshot ID, with exactly
these fields: `action`, `code_host_lanes` and `tracker_lanes` (`available`
or `blocked`). `action` is one of `configuration-valid` (the binding resolves;
capability gaps are reported per lane), `configuration-blocked` (repairable
configuration drift or a missing binding contract blocks the run until setup
or a contract fixes it), `stop-preserve` (merge-policy drift, an identity that
now names a different project, or unknown state stops all work and preserves
it) or `refuse-start` (the run must not start).

- `policy-drift`: The live pipeline requirement differs from the recorded fingerprint.
- `credential-override`: `GITLAB_TOKEN` is set while the source is `glab:`.
- `renamed-path`: Project ID 88001 now has a different path.
- `id-mismatch`: The configured ID and path resolve to different projects.
- `tier-unavailable`: The Free tier returns `null` merge-train fields, recorded
  as `unavailable` when the binding was set up.
- `partial-read`: The approval-rules read failed after bounded retries.
- `glab-missing`: `glab` is absent; GitHub tracker reads are complete.
- `gitlab-tracker`: The override selects a `gitlab` tracker as well; no other
  work is runnable without a tracker source.

Explain the resolution and each restraint briefly in your response.
