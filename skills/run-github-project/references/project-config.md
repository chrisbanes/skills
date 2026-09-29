# GitHub Project Configuration

Copy this structure to `docs/agents/run-github-project.md` in the repository
that owns the queue. Replace every placeholder with live verified data. The
closest trusted `AGENTS.md` or `CLAUDE.md` must reference that exact file.
For an existing binding, run `setup` from its current values instead of copying
this template over it. Follow the
[additive setup procedure](review-and-setup.md#additive-setup-for-an-existing-repository).

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

## Agent Setup (optional)

- Routing: `<configured or typesafe>`
- Default planner profile: `<profile name>`
- Default ticket profile: `<profile name>`
- TypeSafe judgment model: `<versioned model ID, only for typesafe routing>`

| Profile | Capability | Best suited to | Runtime role | Execution model | Reasoning |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `default-owner` | `<bounded task description>` | `<role>` | `<model or runtime-default>` | `<level or runtime-default>` |

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

Omit Agent Setup to use runtime-default agents under the existing capability
rules. When present, require unique profile names, a default-owner profile for
both planner and ticket defaults, and a runtime role with the required access
for every profile. Add helper rows only when wanted, using
`read-only-discovery`, `read-only-evidence`, or `exceptional-investigator`
capabilities. The named defaults are preferences; table order is the
deterministic fallback order for other eligible profiles. Give each profile a
short, distinct task fit when multiple profiles share a capability under
`typesafe` routing. Explicit execution models and reasoning levels must be
supported by that runtime; `runtime-default` defers the choice to it. Profiles
describe allowed agents, not new authority. Keep the user-selected lead model
and any explicit agent-model pin unchanged. Do not put API keys in this file.
`typesafe` routing is optional and sends a sanitized ticket brief to TypeSafe;
read [agent routing](agent-routing.md) before enabling it. TypeSafe may select
only an eligible configured profile, never a new model or the lead model. Log
confidence when exposed; do not configure an uncalibrated numeric cutoff.
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
