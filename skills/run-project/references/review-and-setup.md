# Review and setup lanes

For binding validation or configuration, read the selected
[GitHub](github-binding.md#binding-validation),
[Jira](../../deliver-issue/references/jira-binding.md#binding-validation) or
[GitLab](../../deliver-issue/references/gitlab-binding.md#scope-and-readiness) binding before acting.

## Review

Read only the repository, supplied state, and remote state the user permits.
Apply live-authority, controller-ownership, unknown-outcome, and preservation
invariants to the requested seam. Do not configure a binding, rank/claim/
transition/triage/plan/delegate Project work, mutate issues/PRs/Project items,
push, merge, or close. Do not require execution dependencies, authority, or
agent capacity. Finish `review-complete` with evidence, safe next action, and
uncertainty, or `review-blocked` when permitted evidence is insufficient.

For a supplied implementation routing decision, use
[Implementation ownership](../../subagent-delegation/references/subagent-selection.md#implementation-ownership)
with the described runtime and grants. Report the expected route or
ticket-local blocker and the unrelated work that can proceed.

## Setup

For Jira, use its [read-only setup validation](../../deliver-issue/references/jira-binding.md#binding-validation).
For GitHub, detect legacy boards/configuration through the
[approval-gated migration](github-binding.md#approval-gated-legacy-migration)
before ordinary setup. Discovery and a dry run grant no mutation authority.
Use [GitHub setup](github-binding.md#setup) for the GitHub role and
[GitLab setup](../../deliver-issue/references/gitlab-binding.md#setup) for each GitLab role. Preserve the
common [additive setup](github-binding.md#additive-setup-for-an-existing-repository),
[configuration format](github-binding.md#github-project-configuration), active-lease, confirmation and finish gates. An absent override file uses
read-only default resolution and may finish `configuration-valid`; only requested
file edits need the trusted committed instruction/configuration pair. Execution validates read-only; it
never enters setup repair.
