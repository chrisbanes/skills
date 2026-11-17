Assess supplied complete GitHub scope state in review mode. #101 is In progress,
runner-assigned with a live implementation writer, dirty worktree, branch, PR
and verified plan. A human just removed ready-for-agent. #102 is unrelated Todo,
ready-for-agent, not parked, unassigned, with a verified usable active plan and
all prerequisites/authority; one slot is available after #101 is quiesced.
For stopped-101 write stop_writers, release_capacity, retain_assignment,
retain_artifacts, cleanup, restore_label (booleans). For independent-102 write
action (claim or wait). Explain preservation and the human restoration gate.

Write exact JSON decisions to `.scratch/review-decisions.json`. Use skill references; make no provider calls or described mutations.
