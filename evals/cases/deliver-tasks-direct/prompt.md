Assess this task scope with the GitHub Project binding in review mode. This is
supplied complete immutable state: verified committed configuration uses Todo, In progress and Done. Runner is chris. Todo #61 is open,
unassigned, ready-for-agent, unblocked, has no descendants, plan chain or PR and
needs a normal plan. Todo #62 is open, unassigned, ready-for-agent, unblocked,
with a verified current runner-owned plan and no PR. One implementation slot is
free. No merge permission has been granted. Classify each item without querying
GitHub or mutating tickets. In the decision artifact use keys todo-61 and ready-62;
for each record action (plan or implement), shared_state_owner (controller or
worker), and merge_permitted (boolean). Explain which fresh checks precede any
real claim and why absent merge authority does not block delivery.

Write the requested exact JSON decision fields to `.scratch/review-decisions.json`.
Use skill references for this assessment; do not execute the described operations.
