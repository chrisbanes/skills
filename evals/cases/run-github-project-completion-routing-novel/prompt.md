Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact services, or mutate source, plans, grants or
remote state. The only authorized write is `.scratch/decision.md`, an exception
to the fixture's no-mutation statement for this analysis report alone. No live
model calls are authorized.

Write one normalized `Key: value` line for each field below using the supplied
alternatives, then explain the evidence, limits and next actions in prose.
Deterministic checks cover the fields; semantic review covers the explanation.

In Claude Code, a ticket owner needs a nested independent reviewer before it
can return. Further delegation is authorized. Draft its handoff brief ending and
nested launch instruction. Contrast with the top-level controller launching two
independent owners whose completions it receives normally.

A prior nested reviewer was accidentally launched in the background. Its report
for head H1 arrives at the controller; the owner is waiting for that result.
How should the controller route it? In a variant the owner has advanced to H2.
Later the owner has pushed and returned complete evidence but repeatedly sends
that same report saying it is waiting on background work, with no actionable
event. What should the controller do while preserving future repair ownership?

Fields:

- Nested-review: foreground | background
- Top-level-owners: background | foreground
- Misrouted-result: relay-to-owner | ignore
- Stale-review: renew-affected-coverage | accept-H1-for-H2
- Repeated-report: cancel-active-turn-preserve-owner | keep-waiting
