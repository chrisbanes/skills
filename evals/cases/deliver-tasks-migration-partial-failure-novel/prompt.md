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

Exact plan approved; durable journal records original states before any writes. I1 write is verified Todo. I2 returns timeout, but complete readback finds Todo with unchanged labels/membership/assignment/archive state. I3 returns timeout and readback is incomplete. Config patch has not started. Assess partial. Separately assess retry-original: I3 complete fresh read proves original R and unchanged approved preconditions. Then the human requests rollback, with fresh complete state: I1 is still Todo but a human has added a label, I2 is unchanged Todo, I3 is proven original R. Config rename had actually completed in a different recovery snapshot: legacy path absent, destination equals approved bytes, AGENTS reference equals migration output, CLAUDE.md has concurrent human edits. Assess rollback. Assess missing-option separately: I2 is unchanged but original B no longer exists. No option creation/deletion is authorized.

Use action migration-blocked for unresolved outcomes. verified lists item IDs in supplied inventory order; I3 uses unknown, retry-with-fresh-preconditions or already-original-no-op. Rollback item dispositions use preserve-concurrent-change, restore-B-with-readback, already-original-no-op or rollback-conflict. Config dispositions use restore-legacy-remove-unchanged-destination or preserve-and-propose-inverse-patch; instruction dispositions use restore-original-with-readback or preserve-and-propose-inverse-patch. Retry/intent/readback/preserve/option flags are booleans; config_writes is a number.

Write `.scratch/review-decisions.json` with these snapshot keys and fields: partial: action, verified, retry_I2, I3, retry_I3, config_writes, preserve_journal; retry-original: I3, write_intent_first, readback_required; rollback: I1, I2, I3, config, AGENTS.md, CLAUDE.md, journal_inverse_operations, delete_options; missing-option: I2, create_option, delete_options. Use JSON booleans/numbers/arrays/maps as appropriate. Explain the dry run and exact config reshape, original-state journal and readbacks, retry/rollback preconditions, activation boundary and human-only option deletion in your response.
