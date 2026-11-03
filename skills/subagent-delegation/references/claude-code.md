# Claude Code delegation

Use this reference after explicit invocation of `subagent-delegation` when
Claude Code is the active runtime. The table is the user's routing policy,
not a claim that Claude and Codex models are equivalent.

1. Inspect available agent types, their installed Markdown definitions,
   allowed tools, and model/effort settings. Use a read-only discovery type
   for discovery and a resumable agent with suitable tools for implementation
   and repairs. `Explore` and `Plan` are one-shot; they are not repair owners.
   An independent reviewer must be fresh, read-only, and non-forked so it does
   not inherit the implementation conversation.
2. Preserve installed model and effort pins by omitting those fields in the
   Agent invocation: per-call overrides otherwise take precedence over agent
   frontmatter. For unpinned fields, select from the table and pass `model`
   and `effort` only when the runtime exposes them. Per-call effort requires
   Claude Code 2.1.292 or later and a non-fork invocation. Check provider and
   organization restrictions and global overrides; if they prevent a required
   choice, return the mismatch to the lead instead of silently substituting.
3. Route by the assignment's remaining judgment. Use supported Agent aliases
   (`haiku`, `sonnet`, `opus`, `fable`), not full model IDs or Codex names.
   Aliases resolve through the active provider, so verify effective settings
   rather than assuming a fixed version or account entitlement.

| Assignment | Model / effort |
|---|---|
| Purely mechanical: exact checks, simple extraction, no judgment | haiku / low |
| Computer use or visual interpretation with a defined outcome | sonnet / medium |
| Concise drafting or editing from supplied material | sonnet / low |
| Ordinary bounded implementation, fixes, refactoring, and UI fixes | sonnet / medium |
| Substantial synthesis across several sources, clear constraints | sonnet / high |
| Complex or ambiguous judgment across interacting components | opus / medium |
| Difficult correctness investigations or independent correctness reviews | opus / high |
| Conflicting evidence or demanding cross-component polish | opus / xhigh |

4. Reserve `fable` and `max` for justified exceptions: explain why
   `opus / xhigh` is insufficient and confirm availability. Repository size,
   elapsed time, missing inputs, or routine tool failures do not justify them.
5. Retain the original agent ID and use `SendMessage` for repairs. Model and
   effort overrides persist on resume; reassess them before a new assignment,
   and use a new suitable agent if the existing owner cannot meet its settings
   or capability requirements. Keep independent audits separate from repair
   owners. Remove the Agent tool from an agent's allowed tools when further
   delegation is forbidden; a runtime's default nesting permission is not
   authorization from the lead.
6. Check the session's actual completion behavior. A top-level controller can
   launch independent workers in the background and await notifications while
   doing other work. Interactive nested calls normally wait for their results.
   In headless `-p` or SDK sessions with fork mode off, nested agents can default
   to background and report to the main agent after their parent returns.
   When a parent needs those results before returning, explicitly use the
   runtime's foreground/wait mechanism (`run_in_background: false` where
   exposed). Put independent launches in one message to preserve parallelism.
   Establish required writer permissions before launch; report denied actions
   to the lead without a workaround or an unnecessary repeat approval.
7. Finish selection when the effective agent capability, settings, and result
   delivery satisfy the assignment. Return unavailable capabilities to the
   lead before dispatch.

## Sources

Checked against Claude Code 2.1.317 and official documentation on 2026-11-03:

- [Subagent configuration and lifecycle](https://code.claude.com/docs/en/sub-agents)
- [Model aliases, effort, and provider constraints](https://code.claude.com/docs/en/model-config)
- [Agent tool schema](https://code.claude.com/docs/en/agent-sdk/typescript#agent)
- [Explicit skill invocation](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)

These sources establish runtime mechanics. The assignment table is a user-approved
policy; live comparative model evaluations have not been run.
