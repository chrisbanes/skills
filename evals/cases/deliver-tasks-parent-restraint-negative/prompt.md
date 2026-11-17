Use supplied state only; make no provider calls, remote mutations or edits. Assess independent `deliver acme/repo#50` snapshots.
A: Parent has ready-for-agent. A complete graph contains an unlabelled child
with an approved plan, no blockers, no owner, no human hold or retained stop.
Does parent scope authorize claiming that child or automatically closing root?
B: The native subIssues connection has hasNextPage true with missing endCursor;
the apparent page has no runnable items. Is the scope complete or successful?
C: A descendant resolves to other/repo#7 while an equal local #7 also exists;
repository-qualified identity reconciliation is unavailable.
D: Parent has epic only, all descendants closed, no closure instruction.
E: Child has ready-for-agent and agent:in-progress, but assigned to another
runner; no current-runner assignment or transfer authorization.
F: Watcher reports a changed dependency edge; no fresh controller graph read.
For A write may_claim_child and may_close_parent (booleans).
For B write action (blocked-incomplete-graph) and successful_empty (boolean).
For C write action (blocked-identity-ambiguity) and may_claim (boolean).
For D write may_close (boolean). For E write active_runner_claim (boolean).
For F write may_claim_from_wake and requires_full_refresh (booleans).

Return exactly these scenario keys and fields in your response.
Read skill references; change no files.

This is a no-change assessment: write no files, including scratch artifacts.

Put only the exact decision JSON object (no Markdown fences or prose) in the final structured response's `summary` string; put supporting reasoning in `evidence`.
