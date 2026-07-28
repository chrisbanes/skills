# GitHub Project Configuration

Copy this structure to `docs/agents/run-github-project.md` in the repository
that owns the queue. Replace every placeholder with live verified data. The
closest trusted `AGENTS.md` or `CLAUDE.md` must reference that exact file.

```markdown
# Run GitHub Project

## Repository

- Host: `github.com`
- Repository: `<owner>/<repository>`
- Base branch: `<branch>`

## Project

- Owner: `<organization-or-user>`
- Number: `<number>`
- URL: `<url>`
- Node ID: `<PVT_...>`
- Filter: `<optional trusted Project filter, or none>`
- Ready approver logins: `<login, login, ...>`

## Status

- Field name: `<Status>`
- Field ID: `<PVTSSF_...>`
- Ready name: `<Ready for agent>`
- Ready option ID: `<option-id>`
- In progress name: `<In progress>`
- In progress option ID: `<option-id>`
- Done name: `<Done>`
- Done option ID: `<option-id>`

## Priority

- Field name: `<Priority>`
- Field ID: `<PVTSSF_...>`
- Options in descending order:
  1. `<Critical>`: `<option-id>`
  2. `<High>`: `<option-id>`
  3. `<Medium>`: `<option-id>`
  4. `<Low>`: `<option-id>`

## Merge Policy

- Method: `<merge, squash, rebase, or merge queue>`
- Required reviews: `<repository rule>`
- Required checks: `<repository rule>`
- Done automation: `<none, set-status, or set-status-and-archive>`
- Automation description: `<workflow and trigger, or none>`
```

Keep human-readable names beside IDs so startup validation can distinguish a
rename from an ID that now identifies a different object. Preserve repository-
specific comments and additions when repairing stale mappings.
