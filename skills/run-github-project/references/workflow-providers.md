# Workflow Providers

Never install a provider implicitly.

## Required

| Skill | Source | Install |
| --- | --- | --- |
| `tdd` | `mattpocock/skills` | `npx skills add mattpocock/skills --skill tdd` |

If `tdd` is unavailable, stop and report its source and exact install command.

`to-plan` is required only while processing `Planning`. If it is unavailable,
block those planning items locally and continue implementation items whose
marker-owned plans and handoffs are current.

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
