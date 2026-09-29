An authorized `next` run stopped after three required-CI repair rounds with
the same failure. Its claim, owner, worktree, branch, PR, and In progress status
were preserved. Without another code change, an external rerun of the failed
check has now completed successfully. A fresh reconciled read verifies that
the required check is terminal-green on the exact current PR head. The claim
is still valid. Other review and merge gates have not yet been rechecked.
Explain the next action using only this supplied state. Do not contact GitHub,
edit files, rerun CI, or mutate Project state.
