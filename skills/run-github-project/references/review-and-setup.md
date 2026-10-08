# Review and setup lanes

For `next` or `drain`, use the Setup section below only to validate the
existing binding as a read-only precondition. Require the trusted reference and
configuration pair to be committed on verified base; validate all required
fields and IDs against complete live reads, and record the committed digest,
default branch, and live merge-policy fingerprint. If any value is missing,
unknown, or drifted, stop and preserve work. The sole execution exception is
an already trusted, committed display-name-only change passing
[presentation-only renewal](project-config.md#renew-presentation-only-configuration).
Do not enter the setup repair flow or edit a binding during execution.

## Review

Read only the repository, supplied state, and remote state the user permits.
Apply live-authority, controller-ownership, unknown-outcome, and preservation
invariants to the requested seam. Do not configure a binding, rank/claim/
transition/triage/plan/delegate Project work, mutate issues/PRs/Project items,
push, merge, or close. Do not require execution dependencies, authority, or
agent capacity. Finish `review-complete` with evidence, safe next action, and
uncertainty, or `review-blocked` when permitted evidence is insufficient.

## Setup

Read closest trusted instructions and require an explicit reference to
`docs/agents/run-github-project.md`; use
[project configuration](project-config.md) as its structure. Require repository
identity, default/base branches and closure policy; Project owner/number/URL/node
ID; Status field and Backlog/Todo/Ready/In-progress/Done options; exact
needs-triage, epic, and human-work labels; complete optional Wayfinder labels;
Priority field/options; optional trusted filter; merge
method; Done automation/archive behavior. Store names with IDs; a renamed name
is repairable drift but an ID resolving elsewhere stops work. Never create or
rename Project fields/options. Apply the planning lane migration gate only when
adopting that Status schema, not when adding or repairing mappings for a schema
already in use. Humans perform any legacy-item placement; setup and execution
never promote Backlog or require transition-history authorization. Allow
`closing-keyword` only when base is the default branch.
When Agent Setup is present, validate unique profile names, required default
owner profiles, and runtime role/model/reasoning compatibility. Keep the
selected lead model unchanged. Agent selection uses configured defaults and
capability checks without an external routing service.

### Additive Setup for an Existing Repository

Start with the working-tree configuration, its committed version, and the
closest trusted instructions. Verify repository and Project identity against
complete live reads. Reconcile each value: retain existing values that still
match live state; add requested sections and missing required values; repair a
name only when its stored ID still identifies the same object. Change an
existing value only when the request or verified drift calls for it. Preserve
unrelated fields, IDs, filter, merge policy, comments, local edits, and trusted
instruction text. Never recreate the binding from the template or overwrite a
user choice merely to make it match a proposed default. An absent optional
section is normal, not drift.

If the trusted instructions already point to the exact configuration file,
leave them unchanged. If that reference is missing, propose the minimum patch
to those instructions and write it after confirmation, preserving their other
text and the existing configuration. Do not run the Status-schema migration
gate for an already adopted schema, move Ready items, reroute an existing ticket
owner, or touch Project, issue, or PR state.

When adding or updating Agent Setup, discover the current runtime's available
roles, models, reasoning levels, and access before proposing profiles. If the
request supplies no agent choices, propose the smallest setup:
one `default-owner` profile using `runtime-default` for model and reasoning,
named as both planner and ticket default, plus one `read-only-evidence` profile
when the runtime supports it. Prefer a read-only role capable of both evidence
analysis and independent review; otherwise include a separate review-capable
profile. Disclose a missing independent reviewer as a delivery capability
blocker. The [repair progress gate](ticket-lifecycle.md#repair-progress-gate)
needs that helper after a repeated non-CI failure. If the runtime has no
eligible read-only evidence role, disclose during setup that such a stall will
remain an exact ticket-local blocker; never invent a helper. Add other helper
profiles only when requested or needed for a specified capability. Remove obsolete
`Routing` and `TypeSafe judgment model` fields during an authorized setup edit
subject to the active-lease rules below; do not migrate live bindings during
execution. Resolve missing choices without duplicating a profile or replacing
a user pin.

Apply only the additions and evidence-backed changes, then validate the full
binding and any agent profiles against the runtime and complete live reads. If
it already matches the request, leave the files unchanged. If remote validation
is unavailable, keep the scoped local edit and report precisely which live
check remains unverified; do not report `configuration-valid`. Do not commit
implicitly. Finish `configuration-ready-to-commit` only when validation passes
and the diff is ready; once the configuration and trusted reference are
committed on verified base, report `configuration-valid` only after fresh
validation. Pause new claims while the edit is pending; existing claims may
continue on their unchanged binding.

Changing the committed configuration digest while a ticket still holds an old
lease invalidates it unless execution has verified the narrow
[presentation-only renewal](project-config.md#renew-presentation-only-configuration).
Setup does not perform that renewal or assume it will succeed. While old-digest claims exist, prepare the
edit only in an already separate configuration checkout. Keep the controller
and ticket checkouts used to resume those claims clean and on the old committed
binding. If no separate checkout is available, present the proposed patch
without writing it; setup does not create worktrees. Existing owners may finish
their claims against the old digest, including feedback and repair. Defer
committing the new configuration to verified base and activating it until all
old-digest claims finish. If validation passes, report
`configuration-ready-to-commit` with application or activation pending as
appropriate; do not change existing owners or leases. New routing and other
configuration changes apply only after activation.

When no configuration exists, discover linked Projects and fields, ask
unresolved questions one at a time, present complete configuration and the
minimum trusted-instruction patch together, and write only after confirmation
while preserving unrelated text. Creating or repairing the pair pauses
execution until both files are committed to verified base; do not commit
implicitly. Validate the pair live. A user-authorized dedicated configuration
commit may contain only that pair. Record committed digest, default branch, and
[live merge-policy fingerprint](project-config.md#live-merge-policy-fingerprint);
recheck them before every claim and merge and stop/preserve work on drift or
unknown state.

Treat a legacy `Execution approver logins` entry as obsolete configuration.
Remove it during an otherwise authorized setup edit when no old-digest claim
depends on the binding; otherwise report the deferred cleanup. Its presence or
contents never gate Todo eligibility.

Setup uses the read-only pagination, retry, and incomplete-read rules from
[remote reconciliation](remote-reconciliation.md). If a complete configuration
read cannot be established, discard partial state and return
`configuration-blocked`; setup never applies mutation reconciliation.
