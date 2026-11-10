# Claude Code delegation

Use this reference when Claude Code is the active runtime. The table is the user's routing policy,
not a claim that Claude and Codex models are equivalent.

1. Inspect available agent types, their installed Markdown definitions,
   allowed tools, and model/effort settings. Use a read-only discovery type
   for discovery and a resumable agent with suitable tools for implementation
   and repairs. An independent reviewer must be fresh, read-only, and non-forked so it does
   not inherit the implementation conversation.
2. Preserve installed model and effort pins by omitting those fields in the
   Agent invocation: per-call overrides otherwise take precedence over agent
   frontmatter. For unpinned fields, select from the table and pass `model`
   and `effort`; if the runtime does not expose a field the table requires,
   return the mismatch to the lead before dispatch rather than omitting it.
   Per-call effort requires
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
| Computer use or visual interpretation with a defined outcome | opus / medium |
| Concise drafting or editing from supplied material | sonnet / low |
| Ordinary bounded implementation, fixes, refactoring, and UI fixes (default) | sonnet / medium |
| Substantial synthesis across several sources, clear constraints | sonnet / high |
| Complex or ambiguous judgment across interacting components | opus / medium |
| Difficult correctness investigations or independent correctness reviews | opus / high |
| Conflicting evidence or demanding cross-component polish | fable / high |

4. `fable / high` is the top routine row. Reserve `max`, and `fable` above
   `high`, for justified exceptions: explain why `fable / high` is
   insufficient and confirm availability. Repository size, elapsed time,
   missing inputs, or routine tool failures do not justify them. If `fable`
   is unavailable or not entitled on the active provider, use `opus / xhigh`
   and report the substitution to the lead; never downgrade silently.
5. Follow the [Claude Code handoff rules](subagent-selection.md#claude-code)
   for resuming owners, forbidding nesting, one-shot `Explore` and `Plan`,
   result delivery, and writer permissions. Model and effort overrides persist
   on resume; reassess them before a new assignment, and use a new suitable
   agent if the existing owner cannot meet its settings or capability
   requirements. Keep independent audits separate from repair owners.
6. Finish selection when the effective agent capability, settings, and result
   delivery satisfy the assignment. Return unavailable capabilities to the
   lead before dispatch.
