The run selected delegated mode at preflight because its validated full graph has a parallel point; that choice and existing ownership remain in force.

The host runtime's rules forbid shell-created worker checkouts, so the run created each worker checkout through the host's delegated-task worktrees. The host owns cleanup of those worktrees and exposes no operation that removes them.

All tasks, final checks, and joined review passed. Both worker owners have stopped, and each checkout's accepted commit and task branch reference are preserved. `git -C /workspace/worker-1 status --porcelain` and `git -C /workspace/worker-2 status --porcelain` both print nothing. The host's inventory readback attributes `/workspace/worker-1` to its run-created delegated task, but no longer lists `/workspace/worker-2` under any thread or task, although `git worktree list --porcelain` still shows it.

Review the completion report and the lifecycle action for each worker checkout. Include the retained integration checkout in the accounting. Local read-only inspection only; do not start owners, mutate files, run Git mutations or worktree lifecycle operations, delete directories through the shell, or contact an external service.
