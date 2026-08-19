# GitHub Project Configuration

Copy this structure to `docs/agents/run-github-project.md` in the repository
that owns the queue. Replace every placeholder with live verified data. The
closest trusted `AGENTS.md` or `CLAUDE.md` must reference that exact file.

```markdown
# Run GitHub Project

## Repository

- Host: `github.com`
- Repository: `<owner>/<repository>`
- Default branch: `<branch>`
- Base branch: `<branch>`

## Project

- Owner: `<organization-or-user>`
- Number: `<number>`
- URL: `<url>`
- Node ID: `<PVT_...>`
- Filter: `<optional trusted Project filter, or none>`
- Execution approver logins: `<login, login, ...>`

## Status

- Field name: `<Status>`
- Field ID: `<PVTSSF_...>`
- Backlog name: `<Backlog>`
- Backlog option ID: `<option-id>`
- Planning name: `<Planning>`
- Planning option ID: `<option-id>`
- Ready to implement name: `<Ready to implement>`
- Ready to implement option ID: `<option-id>`
- In progress name: `<In progress>`
- In progress option ID: `<option-id>`
- Done name: `<Done>`
- Done option ID: `<option-id>`

## Triage

- Needs-triage label: `<repository label mapped to needs-triage>`

## Work Roles

- Epic label: `<repository label mapped to epic>`
- Epic label ID: `<LA_...>`
- Human-work label: `<repository label mapped to ready-for-human>`
- Human-work label ID: `<LA_...>`

## Wayfinder (optional)

- Enabled: `<true or false>`
- Map label: `<wayfinder:map>`
- Map label ID: `<LA_...>`
- Research label: `<wayfinder:research>`
- Research label ID: `<LA_...>`
- Prototype label: `<wayfinder:prototype>`
- Prototype label ID: `<LA_...>`
- Grilling label: `<wayfinder:grilling>`
- Grilling label ID: `<LA_...>`
- Task label: `<wayfinder:task>`
- Task label ID: `<LA_...>`

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
- Issue closure: `<closing-keyword or close-after-merge>`
- Required reviews: `<repository rule>`
- Required checks: `<repository rule>`
- Done automation: `<none, set-status, or set-status-and-archive>`
- Automation description: `<workflow and trigger, or none>`
```

Keep human-readable names beside IDs so startup validation can distinguish a
rename from an ID that now identifies a different object. Preserve repository-
specific comments and additions when repairing stale mappings.

Treat the epic label as a work-shape declaration and the human-work label as a
next-action role. Require both mappings even when the current Project has no
matching issue. Never infer either role from issue titles or bodies. Humans
create and rename role labels; never do so from this workflow.

Omit the Wayfinder section, or set `Enabled` to `false`, to preserve the
ordinary workflow unchanged. When enabled, require every displayed Wayfinder
name and ID pair, validate each pair live at startup, and reject an ID that
resolves to another label. A renamed matching ID is repairable drift. The map
label identifies the parent map; the other four labels are mutually exclusive
child types. Never create, rename, or infer any of them.

Humans own the Project schema. Never create or rename Status options from the
runner. Before migrating an existing queue, require zero `In progress` items
and have an execution approver move every legacy Ready item to `Planning`.
Revalidate even an existing marker plan through the planning lane before its
runner-authored Ready handoff.

## Live Merge-Policy Fingerprint

At precondition validation, compute `sha256` over canonical JSON with sorted
object keys and sorted set-like arrays containing:

- the configured base branch and repository merge method or merge-queue mode;
- the live repository settings that permit that method;
- every active ruleset and branch-protection rule applying to the base, reduced
  to merge-queue requirements, required-review fields, and required-check names
  plus strictness; and
- the configured Done automation and the live Project workflow identities and
  enabled states that implement it.

Treat a failed or partial source read as unknown global state, not as a stable
fingerprint. Recompute the fingerprint before every merge, after a relevant
ruleset, branch-protection, repository-setting, merge-queue, or Project-workflow
event, and before resuming a parked implementation claim. A changed fingerprint
is global merge-policy drift: stop and preserve all work until the trusted
configuration and live policy are reconciled. Do not recompute it solely
because an unchanged parked claim appears in an otherwise fresh queue snapshot.
