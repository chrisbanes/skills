Assess the supplied complete binding snapshot before selecting the next ticket from its Project board. Use skill references and supplied state only. Make no provider calls or file changes.

The closest trusted committed AGENTS.md references each of these committed files on the verified base:

- `docs/agents/issue-tracker.md` says issues live in GitHub Issues for `acme/intake`.
- `docs/agents/triage-labels.md` maps `needs-triage` to `triage:review`, `ready-for-agent` to `agent:approved`, and `ready-for-human` to `human:queue`.
- `docs/agents/deliver-tasks.md` selects GitHub code host `acme/product`, Project 8, and pins agent-work ID `LA_AGENT` without duplicating its name. Epic and all board settings resolve independently.

Complete live reads verify both repositories, Project 8 linked to the tracker, and the unique mapped labels in `acme/intake`. `LA_AGENT` belongs to that repository and has the exact mapped name. The Status options, scope, policies and permissions validate. There are no prior claims. No issue or action grant is supplied.

Return the JSON decision object with key `shared` and fields `result`, `tracker`, `code_host`, `triage_label`, `agent_label`, `human_label`, `agent_label_id`, `identity_source` (committed-override-digest or runtime-fingerprint), and `can_claim` (boolean).
