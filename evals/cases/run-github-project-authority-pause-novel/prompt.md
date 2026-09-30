Assess an ongoing `drain` without merge authority using
only this state. Do not run commands, providers, agents, or mutations.

Ticket #51 holds the sole implementation slot. It has a verified exclusive
claim, a clean skill-owned worktree, one reviewed PR at head h51, all required
checks green, and no unresolved feedback. Nothing in the current user request
grants merging. Ticket #52 is unrelated, Ready to implement, and has a current
verified plan. Ticket #53 is natively blocked by #51. Board reads, issue-comment
writes, and claims still work. The controller can quiesce all #51 descendants
and verify/release its resource grants. Ticket #54 is an unassigned ready epic
with no closure grant. No new Project Status option exists.

Later, a fresh invocation is `drain --auto-merge`. #51 has
a verified runner-owned authority-pause comment, unchanged exclusive ownership,
and the same PR head. #55 has a separate verified pause asking for a stakeholder
scope decision which has not been supplied. Its original worker returned a
human-required replan packet proposing a changed acceptance contract. No human
has directed abandoning its partial branch or transferring it to Backlog.
Consider also a changed-head branch
of this later observation where the prior review no longer covers the diff.
Explain the immediate ticket updates, capacity and dependency behavior, later
resume conditions, and finish state when only verified human pauses remain.
