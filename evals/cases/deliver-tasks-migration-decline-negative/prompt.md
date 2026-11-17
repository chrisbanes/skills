Assess workflow setup with the GitHub binding on immutable supplied complete state only. Do not contact providers, run git, or actually migrate any files or board; leave every file unchanged. All unspecified identity/permission/default resolution is unique and valid. Repository acme/repo, Project 7/P7, Status field S has B=Backlog, T=Todo, R=Ready to implement, P=In Progress, D=Done. Complete item inventory, all open/non-archived/unassigned/unparked without blockers: I1 in B labels [LA=ready-for-agent], I2 in B labels [], I3 in R labels [LA] and verified active plan leaf, I4 in B labels [LA, LH=ready-for-human], I5 in T labels []. Other unique roles: LN=needs-triage, LE=epic. No active/paused/parked old-digest leases or writers unless a snapshot says otherwise. Existing workflows are compatible.

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

After seeing the full dry run the human says: "Decline migration. Leave everything as it is." Assess declined. Also assess silence (no response after the proposal), execute (drain invoked on this legacy state), and destination-conflict (new config already exists with unrelated human overrides; no reconciled patch approved).

Explain each snapshot in your response without editing any files: declined finishes migration-declined with zero board/repository/journal writes; silence keeps approval pending; execute blocks configuration instead of migrating; destination-conflict blocks until a preserving patch is approved. Explain why neither setup nor approval of another plan authorizes mutation. Leave all Status options intact.
