Assess four independent supplied binding contract scenarios for task delivery
in review mode. Runner is chris. Every item is open, not parked, ready-for-agent,
unblocked, has no descendants or PRs, and has a verified current runner-owned plan.
All other configuration is valid and the existing five-column model remains.
A: marker {"status":"Working","requiresAssignment":true}, item status Working,
assigned only to chris.
B: marker {"label":"agent:active","requiresAssignment":true}, item status Todo,
labels include agent:active, assigned only to chris.
C: marker {"status":"Working","requiresAssignment":false}, item status Working,
unassigned.
D: marker {"label":"agent:active","requiresAssignment":true}, item status
In progress, assigned only to chris, but agent:active is absent.
These are normalized contract examples, not requests to implement a provider.
For artifact keys A, B, C, D record active_claim (boolean) and
resume_implementation (boolean). Do not infer an active claim from a legacy
column when the selected marker does not match.

Write the requested exact JSON decision fields to `.scratch/review-decisions.json`.
Use skill references; make no provider calls or mutations except this artifact.
