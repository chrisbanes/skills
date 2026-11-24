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
`deliver-issue`; missing `tdd` does not block it. If invoked, identify its
user-confirmed seam and red-before-green requirements rather than silently
claiming they match the default delivery contract.

`to-plan` is required only while processing `Todo`. If it is unavailable,
block those planning items locally and continue implementation items whose
marker-owned plans and handoffs are current.

For ordinary implementation, follow the [controller handoff](../../deliver-issue/references/project-handoff.md)
to the installed `implement-with-subagents` skill. A missing executor blocks
only affected implementation or repair. Retain the claim, evidence and owner
and continue independent work. Use `shepherd` for CI and PR feedback.

`triage` is required only while processing an unblocked Todo
`needs-triage` item. If it is unavailable, block only the triage lane, continue
authorized execution, and report its source and exact install command from the
table.

`wayfinder` is required only while resolving an eligible configured Wayfinder
child. If it is unavailable, block only that Wayfinder Todo item and
continue ordinary planning and execution. Never install it implicitly or copy
its decision-map procedure into this workflow.

`research` is required only for a Wayfinder research child. The Wayfinder owner
must invoke it in a separate subagent; a generic helper is not an equivalent
provider. If it is unavailable, block only research children and continue
other authorized lanes. Never install it implicitly.

The explicit `run-project` procedure may dispatch `triage` to its
recommendation boundary. Its disabled implicit invocation and maintainer
approval gate still prohibit automatic label, comment, or close mutations.

## Review

Use one independent reviewer for the bundled [review contracts](review-contracts.md).
Reuse current evidence from delivery rather than invoking additional review
skills by default. An explicitly requested external review skill keeps its own
procedure; it does not replace missing coverage or authorize edits by reviewers.
