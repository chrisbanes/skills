# Review and setup lanes

For `next` or `drain`, use the Setup section below only to validate the
existing binding as a read-only precondition. Require the trusted reference and
configuration pair to be committed on verified base; validate all required
fields and IDs against complete live reads, and record the committed digest,
default branch, and live merge-policy fingerprint. If any value is missing,
unknown, or drifted, stop and preserve work. Do not enter the setup repair flow
during execution.

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
ID; Status field and Backlog/Planning/Ready/In-progress/Done options; exact
needs-triage, epic, and human-work labels; complete optional Wayfinder labels;
Priority field/options; execution approvers; optional trusted filter; merge
method; Done automation/archive behavior. Store names with IDs; a renamed name
is repairable drift but an ID resolving elsewhere stops work. Never create or
rename Project fields/options. Apply the planning lane clean-cutover gate, and
allow `closing-keyword` only when base is the default branch.

When configuration or trusted reference is absent, discover linked Projects and
fields, ask unresolved questions one at a time, present complete configuration
and minimum trusted-instruction patch together, and write only after
confirmation while preserving unrelated text. Creating/repairing pauses
execution until both files are committed to verified base; do not commit
implicitly. Validate the pair live. A user-authorized dedicated configuration
commit may contain only that pair. Record committed digest, default branch, and
[live merge-policy fingerprint](project-config.md#live-merge-policy-fingerprint);
recheck them before every claim and merge and stop/preserve work on drift or
unknown state.

Setup uses the read-only pagination, retry, and incomplete-read rules from
[remote reconciliation](remote-reconciliation.md). If a complete configuration
read cannot be established, discard partial state and return
`configuration-blocked`; setup never applies mutation reconciliation.
