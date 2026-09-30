# Workflow Providers

Never install a provider implicitly.

## Required

| Skill | Source | Install |
| --- | --- | --- |
| `tdd` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill tdd` |
| `triage` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill triage` |
| `wayfinder` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill wayfinder` |
| `research` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill research` |

Require `tdd` only before a behavioral code change. If it is unavailable,
preserve that ticket's claim and block only its behavioral implementation;
continue documentation, configuration, read-only review, triage, and unrelated
tickets. Report its source and exact install command. Do not treat a
documentation-only change as behavioral merely because it accompanies a PR.

`to-plan` is required only while processing `Planning`. If it is unavailable,
block those planning items locally and continue implementation items whose
marker-owned plans and handoffs are current.

For ordinary implementation, require bundled `deliver-spec` and `shepherd`.
Invoke `deliver-spec` in Project-handoff mode with the ticket owner implementing
and repairing directly by default. Require `implement-with-subagents` only for
requested orchestration or independently useful parallel implementation.
Resolve one fresh independent read-only reviewer before implementation; give it
the materialized canonical source, repository standards, and all bundled review
contracts. No external review skill or tracker setup is required. If independent
review cannot run, block only that ticket without waiving review.

`triage` is required only while processing an unblocked Backlog
`needs-triage` item. If it is unavailable, block only the triage lane, continue
authorized execution, and report its source and exact install command from the
table.

`wayfinder` is required only while resolving an eligible configured Wayfinder
child. If it is unavailable, block only that Wayfinder Planning item and
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
