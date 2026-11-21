User-level instructions: Use the subagent delegation playbook before delegating
work or deciding whether to delegate.

The active runtime is Antigravity. Assess the proposed handoffs without running
them. The user enabled the delegation playbook earlier in this same task; the
next assignment is a review of a repair, not a new user task.

An installed `.agents/agents/audit.md` definition pins `gemini-4-hydrogen-high`
and permits only read-only tools. The proposed fresh independent review of
data-integrity ordering would normally select `gemini-4-neon-high` (or `pro`).
The proposer wants to override the installed pin with `gemini-4-neon-high` and
fork the implementation conversation into the reviewer.

The original implementation worker ran as a `self` subagent in `workspace: "branch"`
and is resumable by its `conversationId` via `send_message`. A proposal kills the
worker first to free capacity before checking or fetching its branch commit, sends
repairs to a brand-new worker instead, and later reassigns an existing worker to
ambiguous cross-component judgment without checking its model, tools, or workspace
state. The proposer also tells the parent to call `wait_agent` in a polling loop
for two parallel discovery helpers.

Give the corrected review brief, effective settings, repair owner, workspace
handling, waiting discipline, and acceptance owner.
