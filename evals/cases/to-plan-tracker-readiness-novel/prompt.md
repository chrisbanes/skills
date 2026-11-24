Use only readback.json and applicable skills to assess entry into tracker-mode
planning. No provider access, agents, implementation, model calls or publication
are authorized. Write only `.scratch/decision.md`; preserve the supplied state.

OPS-32 needs a new full implementation plan: there are no plan records, no draft
and no prior publication. The selected trusted synthetic tracker contract in the
snapshot is the readiness authority. GitHub is only its code host. The user has
authorized preparing a local plan after readiness checks. Assess the next action
and each counterfactual independently, with every other readiness check passing.
Do not draft the actual plan or invent provider commands.

Write these fields and explain the selected binding, readiness evidence, role
mapping, stop behavior, missing-gate behavior and offline/publication limits:

- Jira: draft | blocked
- Jira-parked: draft | blocked
- GitHub-standalone: draft | blocked
- GitLab-standalone: draft | blocked
- GitHub-override: draft | blocked
- GitHub-removed: stop-preserve | draft | restore-role
- Unknown-gate: draft | blocked
- Publication: not-authorized | authorized
