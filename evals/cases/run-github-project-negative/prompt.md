The only remaining items are unlabelled Todo: #1 has no plan; #2 has a verified
plan; #3 is a bare epic with all descendants closed. #4 is an In progress item
whose human removed ready-for-agent while its writer ran; it retains assignment,
branch, dirty worktree and PR. #5 is assigned to the runner in Todo without the
agent label, with an old verified cleanup report, retained branch, worktree and
PR. Review what automatic queue work may do. Explain how writers stop, capacity
is released and all artifacts and assignments are preserved without cleanup.
A later run sees exactly the same state: can it resume or restore the label?
Use supplied immutable state only; do not contact providers or modify it.
