Assess the supplied complete binding snapshot before selecting the next ticket from its Project board. Use skill references and supplied state only. Make no provider calls or file changes.

The closest trusted committed AGENTS.md references each of these committed files on the verified base:

- `docs/agents/issue-tracker.md` says issues live in GitHub Issues for `acme/intake`.
- `docs/agents/triage-labels.md` maps `needs-triage` to `triage:review`, `ready-for-agent` to `agent:approved`, `ready-for-human` to `human:queue`, `needs-info` to `triage:clarify`, and `wontfix` to `triage:declined`.
- `docs/agents/deliver-tasks.md` selects GitHub code host `acme/product`, Project 8, and pins agent-work ID `LA_AGENT` without duplicating its name. Epic and all board settings resolve independently.

Complete live reads verify both repositories, Project 8 linked to the tracker, and the unique mapped labels in `acme/intake`. `LA_AGENT` belongs to that repository and has the exact mapped name. The Status options, scope, policies and permissions validate. There are no prior claims. No issue or action grant is supplied.

Also identify the two mapped labels the controller would use for a later
approved `needs-info` or `wontfix` triage disposition.

In the JSON decision object, use key `shared` for this snapshot. Give
`result`, `tracker`, `code_host`, `triage_label`, `agent_label`,
`human_label`, `needs_info_label`, `wontfix_label`, `agent_label_id`,
`identity_source` (committed-override-digest or runtime-fingerprint), and
`can_claim` (boolean).

Also assess these independent changes to the code-host setup. The board and
tracker configuration remain valid in each and all inputs are verified.

- `gitlab-default`: The code host is a verified GitLab project. Its
  `default_branch` is `trunk` at SHA
  `2222222222222222222222222222222222222222`. The trusted configuration
  omits `Base branch`. The project uses `ff` with squash disabled. Give
  `target_branch`, `target_sha`, and `merge_policy`.
- `github-queue`: GitHub `acme/product` uses the configured base `stable`
  at SHA `3333333333333333333333333333333333333333`. Its trusted merge-method
  preference is `squash`. Live rules require a merge queue on `stable` and
  use squash in the queue. Give `target_branch`, `target_sha`, and
  `merge_policy` (`merge-queue` or `squash`).

Put all three keys in the same JSON object.
