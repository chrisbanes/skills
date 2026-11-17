Assess this supplied complete immutable scope in review mode. The configured
Status options are Todo, In progress and Done; no Ready option exists.
All implementation slots are occupied. Todo #81 is exclusively assigned to
runner chris, ready-for-agent, open, unblocked, with no descendants or PR. Its
planner just published and read back one verified runner-authored active plan
leaf against the current base and verified the full revision chain and digest.
The planner is quiescent and its clean planning worktree is reusable.
What happens now, and when the next implementation slot frees? Write artifact
key waiting-81 with status (Todo or In progress), retain_assignment (boolean),
release_planner (boolean), implementation_slot (boolean); key slot-freed-81
with action (claim or plan), status (Todo or In progress), refetch_lease (boolean).
Separately, #82 is unassigned Todo + ready-for-agent but has a forked plan
chain. Record invalid-82 with action (block or implement). #83 is an unassigned
Todo Wayfinder research child with its configured type label and verified map
parent, no implementation plan, and otherwise valid authority/provider state.
Record wayfinder-83 with action (wayfind or plan). Explain the required drift
screen and why neither new labels nor transition history grant authority.

Write the exact JSON decisions to `.scratch/review-decisions.json`.
Use references; make no provider calls or mutations except this artifact.
