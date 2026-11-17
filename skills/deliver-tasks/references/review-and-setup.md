# Review and setup lanes

For binding validation or configuration, read the selected
[GitHub setup procedure](github-binding.md#binding-validation) before acting.

## Review

Read only the repository, supplied state, and remote state the user permits.
Apply live-authority, controller-ownership, unknown-outcome, and preservation
invariants to the requested seam. Do not configure a binding, rank/claim/
transition/triage/plan/delegate Project work, mutate issues/PRs/Project items,
push, merge, or close. Do not require execution dependencies, authority, or
agent capacity. Finish `review-complete` with evidence, safe next action, and
uncertainty, or `review-blocked` when permitted evidence is insufficient.

## Setup

Detect legacy boards/configuration through the
[approval-gated migration](github-binding.md#approval-gated-legacy-migration)
before ordinary setup. Discovery and a dry run grant no mutation authority.
Follow [GitHub setup](github-binding.md#setup), including its additive setup,
active-lease, confirmation and finish gates. An absent override file uses
read-only default resolution and may finish `configuration-valid`; only requested
file edits need the trusted committed instruction/configuration pair. Execution validates read-only; it
never enters setup repair.
