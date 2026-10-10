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

## Status

- Field name: `<Status>`
- Field ID: `<PVTSSF_...>`
- Backlog name: `<Backlog>`
- Backlog option ID: `<option-id>`
- Todo name: `<Todo>`
- Todo option ID: `<option-id>`
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

- Default planner profile: `<profile name>`
- Default ticket profile: `<profile name>`

| Profile | Capability | Best suited to | Runtime role | Execution model | Reasoning |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `default-owner` | `<bounded task description>` | `<role>` | `<model or runtime-default>` | `<level or runtime-default>` |
| `<evidence-name>` | `read-only-evidence` | `Repeated non-CI failure investigation` | `<read-only role, if available>` | `<model or runtime-default>` | `<level or runtime-default>` |

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

## Monitoring (optional)

- Poll interval seconds: `<120>`

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

The binding specifies how merging works. Establish invocation-scoped permission
under [run authority](authority-and-pauses.md).

Keep human-readable names beside IDs so startup validation can distinguish a
rename from an ID that now identifies a different object. Preserve repository-
specific comments and additions when repairing stale mappings.

`Todo` is the default display name for the lane that queues planning. Pass its
configured name through `--planning-status`; planning action names and
`blockedPlanningClaims` still describe that work. Current column membership is
authority. Never read transition history to prove authorization or a handoff.
Preserve an existing binding's verified lane name, including `Planning`, until
a human renames the live option and an authorized setup reconciles the same
option ID. Once that presentation-only edit is trusted and committed, execution
may [renew affected leases](#renew-presentation-only-configuration) after proving
equivalence; an unreconciled live rename still stops execution. A display-name
rename alone does not require moving items or running the Status-schema migration.

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

Humans own the Project schema and all promotion out of Backlog. Never create
or rename Status options, promote Backlog, or process Backlog work from the
runner. Before adopting a new schema, require zero `In progress` items and
have humans create and verify `Backlog`, `Todo`, and `Ready to implement` options,
configure their IDs, and place legacy work needing a new plan in Todo. Do not
retain an Agent Brief compatibility path. Revalidate
usable marker plans by their identity, integrity, and configured base; do not
require Status event history. An existing `Execution approver logins` entry is
obsolete and must not affect eligibility.

Omit Agent Setup to use runtime-default agents under the existing capability
rules. When present, require unique profile names, a default-owner profile for
both planner and ticket defaults, and a runtime role with the required access
for every profile. Include a `read-only-evidence` row when the runtime supports
it because the repair progress gate needs that helper. Ensure a configured
read-only profile also supports independent judgment-based review; the same
profile may cover evidence and review if its runtime role supports both. Add
`read-only-discovery` or `exceptional-investigator` rows only when wanted. When
no read-only evidence role is available, disclose that repeated non-CI stalls
remain ticket-local blockers. The named defaults are preferences; table order
is the deterministic fallback order for other eligible profiles. Give each
profile a short task description. Explicit execution models and reasoning levels
must be supported by that runtime; `runtime-default` defers the choice to it.
Profiles describe allowed agents, not new authority. Keep the user-selected lead
model and explicit agent-model pins unchanged. Select agents deterministically
under [agent routing](agent-routing.md); no routing service is used.
Legacy `Routing` and `TypeSafe judgment model` fields are obsolete: ignore them
at dispatch and remove them during an authorized setup edit, preserving active
binding leases under the setup procedure.

Omit Monitoring to check every 120 seconds. When present, `Poll interval
seconds` sets the `drain`
[Project Watcher](drain-scheduler.md#project-watcher) interval and must be a
positive number. It grants no authority. A mid-drain edit is ordinary
configuration drift under the existing rules; presentation-only renewal does
not cover it.

## Renew Presentation-Only Configuration

Execution may use this narrow exception when the trusted binding has already
changed on the verified committed base. It never edits a binding, trusted
instructions or the board. Use the same procedure at startup, before writes
and for active, planning, paused, parked and Wayfinder recovery leases.

1. Stop affected writers and new claims. Reconcile in-flight mutations and
   resource ownership; do not renew while a writer can still use the old lease.
   Retain every owner, assignment, draft, worktree, PR and historical record.
2. Load the old and new committed binding and trusted-reference identities,
   their digests, prior verified mappings and complete current live mappings.
   Require stable repository, Project, field, option and label identities.
   Permit only human-readable display-name changes attached to those same IDs.
   Prove unchanged lane meaning, selection/filter, priority order, role meaning,
   agent policy, base branch, authority, merge/closure/automation policy and
   [live merge-policy fingerprint](#live-merge-policy-fingerprint). Compare the
   entire binding, not just the renamed field; a same-ID rename alone is not
   proof of unchanged meaning. Missing old evidence, an uncommitted replacement,
   unknown equivalence, a changed ID or any semantic change stops the run.
3. Freshly revalidate membership, current-column authority, exclusivity,
   source/plan and any amendment, retained artifacts/heads and grants for each
   affected lease. Screen base drift under the existing plan rules. A
   presentation change does not revive Backlog work, pass qualification, alter
   a bounded grant, reset a repair budget or supply new invocation authority.
4. In the controller lane, publish one runner-authored issue record per affected
   ticket with `<!-- run-github-project:configuration-renewal:v1 -->`. Record
   old/new commits and configuration digests, stable IDs and old/new names,
   complete comparison and policy evidence, lease/artifact identities and
   predecessor renewal permalink/digest (or original lease for the root).
   Bind every retained historical marker by comment ID, permalink and semantic
   payload digest. Never edit that marker's original configuration digest.
   Reconcile an ambiguous create before retrying; refetch and verify exact
   author, body, payload digest and a single unforked, gap-free renewal lineage.
5. Renew the controller's effective leases only after every affected record is
   verified and each owner acknowledges the new lease before writing. Keep the
   old and new evidence plus the verified renewal links in the checkpoint;
   never silently replace history. Partial publication or acknowledgment keeps
   affected writes stopped until reconciled. Do not republish verified records.
6. On resume, reconstruct from original leases/markers and the complete verified
   renewal lineage. Refetch current identities and authority, and require the
   latest renewal's new digest to match the current committed binding. Retain
   the original marker payload and digest even after repeated renames. A cache
   or a renewal comment alone cannot prove equivalence or authorize execution.

For Wayfinder, normalize only this verified result through the optional
[configuration renewal binding](normalized-ticket.md#wayfinder-configuration-renewal).
The ranker validates its marker/current-digest binding, not live semantics.
Without verified renewal, every existing exact-digest mismatch remains a stop.
An unchanged merge-policy fingerprint is mandatory; policy drift never uses
this route. Keep invalid or incomplete renewal as an integrity blocker, not a
parking or retry signal.

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
