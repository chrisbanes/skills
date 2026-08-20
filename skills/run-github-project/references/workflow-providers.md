# Workflow Providers

Never install a provider implicitly.

## Required

| Skill | Source | Install |
| --- | --- | --- |
| `tdd` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill tdd` |
| `triage` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill triage` |
| `wayfinder` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill wayfinder` |
| `research` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill research` |

If `tdd` is unavailable, stop the execution lane and report its source and
exact install command. Permit a triage-only tail run to continue.

`to-plan` is required only while processing `Planning`. If it is unavailable,
block those planning items locally and continue implementation items whose
marker-owned plans and handoffs are current.

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

## Preferred Review Providers

These providers are optional. Prefer them when installed; otherwise use an
equivalent installed skill or execute the applicable bundled contract directly.

| Contract | Preferred skill | Source | Install |
| --- | --- | --- | --- |
| Correctness and standards | `code-review` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill code-review` |
| Reuse, clarity, and efficiency | `review-and-simplify-changes` | `Dimillian/Skills` | `npx skills add Dimillian/Skills --skill review-and-simplify-changes` |
| Over-engineering | `ponytail-review` | `DietrichGebert/ponytail` | `npx skills add DietrichGebert/ponytail --skill ponytail-review` |

After installation, restart or refresh the agent environment and verify each
installed skill is discoverable by its exact name before proceeding.
