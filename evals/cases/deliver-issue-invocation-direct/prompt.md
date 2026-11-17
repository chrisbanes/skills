Use only this synthetic state and the applicable skill references. Write `.scratch/review-decisions.json` with one object per named snapshot and exactly the fields shown below. Do not execute delivery, contact providers, change labels or other files.

The user explicitly says “deliver acme/repo#91”. It is an open leaf with complete concrete acceptance criteria, no plan, no labels, no Project and no board config. No human hold, previous stop or owner exists; authenticated issue and repository reads are complete. Planning capability is available. No merge or closure grant exists. Compare the same unlabelled leaf offered to run-project on a configured board. Also assess a request with only a local spec file and no tracker item. Classify the initial route, not execution; do not publish a plan.

Required output fields (choose values from the facts and workflow):

- direct: next, requires_project, requires_ready_label, add_labels, merge, close
- board: next, claim
- local: next, tracker_write
