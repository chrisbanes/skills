User-level instructions: Use the subagent delegation playbook before delegating
work or deciding whether to delegate.

The active runtime is Claude Code. Assess the proposed handoffs without running
them. The user enabled the delegation playbook earlier in this same task; the
next assignment is a review of a repair, not a new user task.

The installed reviewer definition pins model=sonnet and effort=high and permits
only read-only tools. The proposed fresh independent review of data-integrity
ordering would normally select opus/high. Agent invocation overrides frontmatter.
The proposer wants to pass opus/high and fork the implementation conversation.
The original worker is resumable via SendMessage; it previously received
sonnet/medium overrides. A proposal sends repairs to a new agent instead, then
reassigns the old worker to ambiguous cross-component judgment without checking
its persisted model or effort.

For interactive Claude Code, nested calls normally wait. In a separate headless
SDK session with fork mode off, nested agents default to background and report
completion to the main agent after a parent returns. The headless parent needs
two independent discovery results before returning and has permission to delegate.
Agent exposes run_in_background. Explain both session paths rather than assuming
they share one notification rule. Give the review brief, effective settings,
repair owner, and acceptance owner.
