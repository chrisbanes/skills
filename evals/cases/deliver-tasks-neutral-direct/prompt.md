Assess this supplied immutable ranker input contract for task delivery in
review mode. The binding supplies the columns Backlog, Todo,
In progress and Done, and claim marker
{"status":"In progress","requiresAssignment":true}. Runner is chris.
Both items are open, unassigned, ready-for-agent, not parked, with no descendants
or PRs. #31 has itemId scope-31, itemRef TASK-31, no blockerRefs, is in Todo, and has a verified runner-owned current plan. #32 has itemId scope-32,
itemRef TASK-32, blockerRefs ["OTHER-9"], and is in Todo with no plan.
The blocker is outside the scope and remains open. Determine whether each is a
candidate; opaque references need no GitHub URL parsing. Record keys item-31 and
item-32 with action (implement or exclude). Derive implementation readiness from Todo and the verified plan leaf;
no Ready column or CLI input is configured.

Write the requested exact JSON decision fields to `.scratch/review-decisions.json`.
Use skill references; make no provider calls or mutations except this artifact.
