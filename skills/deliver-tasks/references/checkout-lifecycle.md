# Checkout Lifecycle

Every checkout a run creates ends either retired with verified readback or
retained with a stated reason. The calling workflow defines when its work is
delivered; this reference defines how checkouts are created, recorded, reused
and retired.

## Create

1. Use the runtime's native managed worktree only when the runtime can both
   create it at an exact SHA and remove it with an inventory readback.
   Otherwise create a plain Git worktree with
   `git worktree add -b <task-branch> <path> <exact-sha>`. A runtime that can
   create but not remove worktrees, such as T3 Code, uses plain Git worktrees.
2. Verify the new checkout's branch and HEAD SHA before handing off its exact
   path, branch, base and instructions.

## Record

Maintain this record in the workflow's existing reporting context, not a new
committed ledger. Record each checkout's provenance and runtime identity, exact
path, owner, task branch and base, accepted commits, integration and check
evidence, active use, and disposition. Distinguish the stable integration
checkout, run-created checkouts, and pre-existing or adopted checkouts.
Never infer ownership from a directory name. Pre-existing, adopted, pinned,
and shared checkouts are not automatically retired.

## Release and reuse

Release a checkout only after its delivered work is preserved under the calling
workflow's delivery condition, its owner and processes stop using it, and
needed untracked or ignored artifacts are accounted for. Otherwise retain it.
For a worker slot, delivered means its accepted task commit and original branch
ref are recorded and preserved, integration succeeds, and affected checks pass
at the exact integrated SHA.

Before reuse, require a clean checkout, create a fresh unique task branch from
the recorded current integrated SHA, verify the branch and SHA, and hand off
the exact path, branch, base, and instructions. Never reset or delete an old
branch to reuse its checkout. A clean detached checkout, such as a planning
checkout, is reused by detaching it at the recorded current base SHA.

## Retire

For a pool of worker slots, retire released surplus checkouts when remaining
work no longer needs their capacity, retaining one for sequential work and only
justified capacity for future concurrent writers. At completion, retire all
eligible run-created checkouts. On a blocker or interruption, retire eligible
surplus when execution remains available; retain active, unfinished, failing,
or otherwise unsafe checkouts. If interruption prevents cleanup, report it at
the next opportunity. Preserve the integration checkout, user work, and
required ignored artifacts. Do not force cleanup to meet a capacity cap.

For each eligible run-created checkout:

1. Record the exact `git -C <path> status --porcelain` output in the run
   report.
2. Retain and report the checkout when it has staged or modified tracked files,
   a locked worktree, or a HEAD that is not delivered.
3. Copy out or account for any untracked or ignored artifact that an owner,
   process, or evidence still needs.
4. Remove the checkout. Use the runtime's native operation for a managed
   worktree. For a plain Git worktree, run `git worktree remove --force <path>`
   once; step 2 already retained tracked changes and locks, so only untracked
   and ignored files are dropped.
5. Verify the path is absent from the provider inventory or from
   `git worktree list --porcelain`; one listing may verify several removals.

Never shell-delete a managed checkout, run `git clean` or `git reset`, pass
`--force` twice, prune globally, or delete a branch ref the calling workflow
does not name. If ownership or eligibility is uncertain, retain and report the
checkout.

## Account

Account for every run-created checkout as retired with verified readback or
retained with a reason. Record the integration checkout as retained and explain
retained exclusions. If eligible retirement fails or cleanup capability is
missing, report code verification separately and mark the workflow
cleanup-incomplete; do not claim overall completion. Include the exact path,
error, and provider readback. Do not retry blindly.
