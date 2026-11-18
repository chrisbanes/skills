Use only the supplied state and applicable skill instructions. Read skill entrypoints and needed Markdown references using standalone `cat` commands. Do not execute the workflow, run other commands, contact providers, launch agents or change files.

In `drain`, the controller just reconciled the squash merge of #80's PR into the verified base and moved #80 to Done. #80's plain Git worktree on `cb/issue-80-cache-key` holds a HEAD contained in the merged PR. Its ticket agent and test processes have stopped. `git status --porcelain` lists `?? scratch/notes.md` and `?? build-debug.log`; no tracked file is modified, no evidence references either file, and ignored `build/` output also exists. What happens to #80's worktree and local branch, and what does the run report record?

Assess these independent Project no-change snapshots as well. The runner has
no host write access. The tracker supports close and readback.

- `no-change-worker`: In an active Project drain pass, current verification
  and applicable review prove full acceptance at the verified integrated
  base. The checkout and HEAD match that base and the final diff is empty.
  The worker has evidence to hand off. The controller owns closure and Done.
- `no-change-controller`: The controller verifies the same current evidence,
  exact issue and claim, explicit tracker grant, and complete satisfied
  descendant and blocker state. Close returns authoritative CLOSED readback.
  The exact bound Project item is read back as Done under configured
  automation. There is no PR, remote branch, or unresolved host write. The
  run-created plain Git checkout is unlocked and clean at the acceptance
  base, all processes have stopped, and required artifacts are preserved.
  The authorized retirement operation succeeds and inventory confirms absence.
- `unknown-done`: The tracker is confirmed CLOSED but verification of the
  expected Done automation on the exact item is unavailable.
- `different-head`: Closure and Done are verified, but checkout HEAD is a
  local-only commit above the verified acceptance base. Its tree is identical.
- `unknown-transport`: Closure, Done, and the checkout proof are verified,
  but the checkout is managed and the runtime cannot confirm a removal or
  host-owned handoff transport.
- `unknown-retirement`: Same plain Git checkout as the successful scenario,
  but the removal attempt timed out and the inventory is unavailable.

Return one JSON object with exactly these keys and fields. Use lowercase
hyphenated tokens and booleans. Give the merged scenario's exact observed
porcelain lines in order and the readback used for the decision.

- `merged`: `porcelain`, `checkout`, `branch`, `checkout_readback`.
- `no-change-worker`: `return`, `push`, `open_pr`, `shepherd`.
- `no-change-controller`: `tracker`, `done`, `checkout`, `branch`,
  `checkout_readback`, `complete`.
- `unknown-done`, `different-head`, `unknown-transport`, `unknown-retirement`:
  `checkout` (`retain` or `reconcile-before-retry`), `branch`, `complete`.

Use `retire`, `delete`, `keep`, `inventory-absent`,
`close-and-verify`, and `verified` where applicable.
