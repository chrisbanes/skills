Assess workflow setup with the GitHub binding on immutable supplied complete state only. Do not contact providers, run git, or actually migrate any files or board; only write the decision artifact. All unspecified identity/permission/default resolution is unique and valid. Repository acme/repo, Project 7/P7, Status field S has B=Backlog, T=Todo, R=Ready to implement, P=In Progress, D=Done. Complete item inventory, all open/non-archived/unassigned/unparked without blockers: I1 in B labels [LA=ready-for-agent], I2 in B labels [], I3 in R labels [LA] and verified active plan leaf, I4 in B labels [LA, LH=ready-for-human], I5 in T labels []. Other unique roles: LN=needs-triage, LE=epic. No active/paused/parked old-digest leases or writers unless a snapshot says otherwise. Existing workflows are compatible.

Both closest trusted committed AGENTS.md and CLAUDE.md reference exact committed docs/agents/run-github-project.md on verified base abc. Working files match committed bytes. Destination the documented new default config path is absent. Full legacy config:

```markdown
# Run GitHub Project
## Repository
- Host: `github.com`
- Repository: `acme/repo`
- Default branch: `main`
- Base branch: `release`
## Project
- Owner: `acme`
- Number: `7`
- URL: `https://github.com/orgs/acme/projects/7`
- Node ID: `P7`
- Filter: `none`
## Status
- Field name: `Status`
- Field ID: `S`
- Backlog name: `Backlog`
- Backlog option ID: `B`
- Todo name: `Todo`
- Todo option ID: `T`
- Ready name: `Ready to implement`
- Ready option ID: `R`
- In progress name: `In Progress`
- In progress option ID: `P`
- Done name: `Done`
- Done option ID: `D`
## Triage
- Needs-triage label: `needs-triage`
- Needs-triage label ID: `LN`
## Work Roles
- Agent-work label: `ready-for-agent`
- Agent-work label ID: `LA`
- Human-work label: `ready-for-human`
- Human-work label ID: `LH`
- Epic label: `epic`
- Epic label ID: `LE`
## Merge Policy
- Method: `squash`
- Issue closure: `close-after-merge`
- Done automation: `set-status`
<!-- Preserve this custom comment and every existing nonlegacy setting. -->
```

The human explicitly approves the exact displayed moves, config patch, trusted-reference patch, and local migration-journal.json location. A fresh complete read is identical, all writers are quiesced and there are no old leases. Journal persistence/readback and all authoritative write readbacks succeed. Assess apply, plus changed-before-apply (I1 gains a human label after approval) and journal-failed (journal persistence fails). No config commit is authorized.

Use action values configuration-ready-to-commit, migration-awaiting-approval or migration-blocked. moves_verified contains item IDs in supplied inventory order. Every other field is a JSON boolean except mutation_writes/writes, which are numbers, and label_changes, which is an array of actual changes.

Write `.scratch/review-decisions.json` with these snapshot keys and fields: apply: action, journal_before_first_write, journal_has_original_bytes, journal_has_original_status_ids, journal_has_approval_and_plan, moves_verified, label_changes, config_and_references_verified, delete_options, implicit_commit, start_execution; changed-before-apply: action, renew_approval, writes; journal-failed: action, mutation_writes. Use JSON booleans/numbers/arrays/maps as appropriate. Explain the dry run and exact config reshape, original-state journal and readbacks, retry/rollback preconditions, activation boundary and human-only option deletion in your response.
