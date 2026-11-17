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

Setup is requested, but migration is not approved. Produce the dry run. Snapshot retained-options is a previously verified complete migration: B/R still exist but are empty, the new config/reference pair is committed and valid, no old file or pending journal operations remain. Also assess snapshots adopted (only Todo/In Progress/Done, no legacy file), active (same legacy state but I5 is In Progress with an active lease), and config-only (adopted board, legacy file still present).

Use action values migration-awaiting-approval or configuration-valid. Represent moves as an object mapping item IDs to [old-option-ID, target-option-ID]; newly_eligible as item IDs; blocked_labelled as item ID to reason (contradictory-roles). Use apply_blocker active-lease when applicable. config_rename is [old-path, new-path]; remove_status_fields and add_sections contain exact field/section names in config order; trusted_references lists AGENTS.md then CLAUDE.md. Counts are numbers and flags are booleans.

Write `.scratch/review-decisions.json` with these snapshot keys and fields: legacy: action, moves, newly_eligible, blocked_labelled, label_changes, board_writes, repository_writes, journal_written, delete_options, config_rename, add_sections, remove_status_fields, trusted_references, preserve_pins; adopted: action, migration_required, writes; active: action, apply_blocker, writes; config-only: action, moves, create_optional_file; retained-options: action, writes, delete_options. Use JSON booleans/numbers/arrays/maps as appropriate. Explain the dry run and exact config reshape, original-state journal and readbacks, retry/rollback preconditions, activation boundary and human-only option deletion in your response.
