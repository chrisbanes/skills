Use only this synthetic state and the applicable skill references. Write `.scratch/review-decisions.json` with one object per named snapshot and exactly the fields shown below. Do not execute delivery, contact providers, change labels or other files.

For each snapshot all reads are complete. owned: the named issue is already claimed by an active board controller. delegated: that board delegates only issue #91, which has children #92 and #93 not selected by the board. planner: the current direct-issue controller supplies its authenticated invocation grant, exact root/member identities, sole owner, no holds, no prior stop, and current operation permissions for an unlabelled leaf. The product contract is complete; plan publication approval is not granted. Decide who controls each operation and whether absent labels block planning.

Required output fields (choose values from the facts and workflow):

- owned: next, new_claim
- delegated: scope, select_children, merge_owner
- planner: next, requires_ready_label, publish
