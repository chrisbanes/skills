Assess immutable supplied complete state only; do not call GitHub/git or write configuration. Conventional defaults are available, as in the default-binding case: GitHub tracker/code host, invocation Project 7, git acme/repo, default main, sole merge method squash, unique conventional columns/roles, no Priority. Closest trusted committed AGENTS.md references the committed docs/agents/queue-overrides.md on verified base. It contains only these overrides:

```markdown
# Deliver tasks
## Tracker
- Provider: `github`
## Code host
- Provider: `github`
## Scope
- Type: `project`
- URL: `https://github.com/orgs/acme/projects/8`
## Repository
- Base branch: `release`
## Status
- Todo name: `Planning`
- Todo option ID: `OPT_PLAN`
## Work Roles
- Agent-work label: `agent:ready`
- Agent-work label ID: `LA_AGENT`
- Human-work label: `human:next`
- Human-work label ID: `LA_HUMAN`
## Merge Policy
- Issue closure: `close-after-merge`
```

Live Project 8 exists uniquely; OPT_PLAN identifies its Planning option in its Status field, the live In Progress and Done options resolve uniquely. Both pinned role IDs match exact names in acme/repo; roles are distinct, all other defaults resolve. The release branch exists. No prior claims. Snapshot valid is this state. Snapshot wrong-id differs only in that OPT_PLAN belongs to another field/Project. Snapshot renamed differs only in that OPT_PLAN now has the live name Waiting. Snapshot untrusted differs only in that the exact-file AGENTS reference is absent. Snapshot uncommitted differs only in that the override exists solely in the working tree.

Write `.scratch/review-decisions.json`: valid records action (configuration-valid), scope (project-8), base (release), planning_status (Planning), agent_role (agent:ready), human_role (human:next), closure (close-after-merge), identity_source (committed-override-digest), requires_file (true). For wrong-id, renamed, untrusted, uncommitted record action (configuration-blocked), falls_back_to_defaults (boolean), edits_config (boolean). Explain override precedence, inherited fields, exact identity checks, drift, independent provider roles and preserved existing leases.
