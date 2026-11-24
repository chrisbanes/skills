Assess four independent bindings before selecting the next ticket from a Project board. Use only the supplied state and skill references. Make no provider calls or file changes. In each snapshot the verified base, code host, board, scope and workflow policy are valid. The trusted committed `deliver-tasks.md` sets tracker GitHub `acme/intake`, agent-work name `agent:approved` and its matching ID. All delivery values verify live.

- `tracker-conflict`: A trusted, exact-file referenced and committed tracker guide declares GitHub Issues in `acme/other`. Both repositories are real.
- `role-conflict`: A trusted, exact-file referenced and committed triage guide maps `ready-for-agent` to `agent:other`. Both labels exist in the tracker repository.
- `uncommitted`: A trusted exact-file reference names the triage guide, but the guide's working-tree label mapping was edited and does not match the committed guide.
- `legacy`: No trusted exact-file reference names the shared guides. A local draft triage guide happens to exist and maps `ready-for-agent` to `agent:other`.

Return the JSON decision object with one key per snapshot, each containing `result` (`configuration-valid` or `configuration-blocked`), `lookup` (`tracker-repository`, `agent-work-label`, `shared-config-trust` or `none`), `uses_legacy_binding` and `edits_config` (booleans).
