Assess the proposed workflow using only the supplied state and applicable skill references. Do not run commands other than skill and reference reads, launch agents, contact providers or edit files.

The worktree is clean. tdd, agreed seams and one independent final reviewer are available throughout. The lead is gpt-6.2-sol/medium. The user opts into automatic implementation routing and pins implementation effort to high. For the full chain below, the installed Codex policy selects gpt-6.1-terra/xhigh. Two authorized resumable gpt-6.1-terra/high workers, W1 and W2, each have safe isolation available. W1 is the proposed chain owner. No installed role pins apply.

- chain: A precedes B. A has not begun. The proposal assigns both tasks to W1 and retains W1 for repairs. B remains held until A is accepted, integrated and its affected checks pass on the integrated head.
- split: Same state, but the proposal assigns A to W1 and B to W2.
- repair: W1 implemented both items under the serial route. After integration, B's validation failed. Its failed integrated head is clean and retained and W1 is available to repair from that head in isolation.
- parallel: In this separate graph A and B have disjoint writes and no prerequisites, and C depends on both. The same opt-in and pin apply, and both workers match the resolved settings for all three items. There are two free implementation slots. The proposal assigns A and B to W1 and W2 now and C to a worker after both pass their integrated checks.

Return the following exact field names, using actual model IDs and effort names:
- chain: valid, model, effort, owner (W1, W2, or lead), next (dispatch or hold), dependent (wait-for-integrated-checks or dispatch), final_review
- split: valid, next (dispatch or correct-owner)
- repair: owner (W1, W2, or lead), next (repair-forward or reset), final_review
- parallel: valid, frontier (task IDs listed alphabetically), tail_owner (worker or lead), task_acceptance, final_review

Put only the decision JSON object in the final structured response's `summary` string, with one object per snapshot. Put supporting reasoning in `evidence`.
