# Workflow Providers

Never install a provider implicitly.

## Conditional providers

| Skill | Source | Install |
| --- | --- | --- |
| `tdd` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill tdd` |
| `triage` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill triage` |
| `wayfinder` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill wayfinder` |
| `research` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill research` |

Use `tdd` only when explicitly requested or required by repository policy.
Ordinary behavioral implementation uses owner-driven meaningful tests under
`deliver-spec`; missing `tdd` does not block it. If invoked, identify its
user-confirmed seam and red-before-green requirements rather than silently
claiming they match the default delivery contract.

`to-plan` is required only while processing `Todo`. If it is unavailable,
block those planning items locally and continue implementation items whose
marker-owned plans and handoffs are current.

For ordinary implementation, require bundled `deliver-spec` and `shepherd`.
Invoke `deliver-spec` in Project-handoff mode. The ticket lead may implement
solo or delegate when independent work, isolation or specialist investigation
justifies the overhead. Keep repairs with their implementation owner and retain
architecture, integration and non-merge PR authority in the ticket context.
No separate `implement-with-subagents` installation is required.
Establish independent-review capability from runtime metadata without spawning a
capability-only reviewer. Review the integrated candidate once, then affected
repairs; reuse valid coverage. If review cannot run, block that ticket's delivery
without waiving final review. No external review skill or tracker is required.

`triage` is required only while processing an unblocked Todo
`needs-triage` item. If it is unavailable, block only the triage lane, continue
authorized execution, and report its source and exact install command from the
table.

`wayfinder` is required only while resolving an eligible configured Wayfinder
child. If it is unavailable, block only that Wayfinder Todo item and
continue ordinary planning and execution. Never install it implicitly or copy
its decision-map procedure into this workflow.

`research` is required only for a Wayfinder research child. The Wayfinder owner
must invoke it in a background subagent; a generic helper is not an equivalent
provider. If it is unavailable, block only research children and continue
other authorized lanes. Never install it implicitly.

The explicit `run-github-project` procedure may dispatch `triage` to its
recommendation boundary. Its disabled implicit invocation and maintainer
approval gate still prohibit automatic label, comment, or close mutations.

## Review

Use one independent reviewer for the bundled [review contracts](review-contracts.md).
Reuse current evidence from delivery rather than invoking additional review
skills by default. An explicitly requested external review skill keeps its own
procedure; it does not replace missing coverage or authorize edits by reviewers.
