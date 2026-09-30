The current checkout has an unrelated uncommitted migration file. The supplied
ticket graph is valid, and the runtime could create a separate clean worktree.
The proposed implementation workflow would create that worktree and dispatch
owners immediately while leaving the dirty checkout alone. Review the next
action under the agreed starting-state rule. Do not create worktrees, start
agents, edit files, or contact a provider.
