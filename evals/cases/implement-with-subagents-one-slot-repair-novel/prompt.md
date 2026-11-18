Assess the next action in each snapshot using the supplied state and applicable
skill references. Keep the assessment read-only. Only read skill references.

An explicit implementation model pin routed the serial chain A → B to one
authorized resumable worker, W1. A was accepted from branch `task/a` at
`1111111`. The integration checkout is clean at recorded post-integration
head `2222222`, where A's affected check failed. Its output and original
acceptance evidence are recorded. B has not started. The only permitted
worker checkout is `/worktrees/w1`. It is still reserved for A, on
`task/a`, with no tracked or untracked changes and its needed artifacts
accounted for.

- idle: W1's turn has ended and no process is using its checkout.
- busy: Same state, except a validation process is still using that checkout.

For each snapshot return `owner`, `checkout` (exact path usable now or
null), `action` (repair or wait), `repair_base` (the recorded SHA),
`slot` (reserved or released), `original_branch` (preserve or reset),
`original_evidence` (retain or discard), `affected_check`
(rerun-on-repaired-integration, reuse-original, or skip), and `dependent`
(wait-for-integrated-checks or dispatch). Describe the eventual check after
the repair in both snapshots. Put only the decision JSON object in the
structured response's `summary` string, with `idle` and `busy` as its keys.
Put supporting reasoning in `evidence`.
