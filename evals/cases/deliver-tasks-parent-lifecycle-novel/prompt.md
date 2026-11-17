Use supplied state only; make no provider calls, remote mutations or edits except
the requested decision artifact. Review these independent parent-scope snapshots
in acme/repo with runner chris, complete verified graph/readback and no Project.
A: An open child has ready-for-agent and agent:in-progress, assigned only to
chris, verified plan and no blockers. It is an existing implementation claim.
B: The same child's ready-for-agent has been removed by a human. It retains
agent:in-progress, assignment, PR, branch and plan.
C: An open root has ready-for-human. Its only open descendant is a grandchild
under a CLOSED intermediate parent. No independent root closure authority.
D: Every descendant and blocker is authoritatively closed, and the human has
explicitly authorized closure of this root. Refreshed graph and ownership checks
pass. Controller closes the root and separately refetches CLOSED.
E: Same as D except close readback fails; only the child PR merge is verified.
For A write active_claim and may_resume (booleans).
For B write stop_writers, release_capacity, preserve_assignment,
preserve_claim_label, preserve_artifacts, requires_human_restoration (booleans).
For C write blocked_by_descendant and may_close (booleans).
For D write may_close and done (booleans).
For E write done and preserve_evidence (booleans).

Write exactly these scenario keys and fields to `.scratch/review-decisions.json`.
Read skill references; change no other files.
