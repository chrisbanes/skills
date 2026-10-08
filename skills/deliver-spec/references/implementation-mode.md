# Implementation-mode procedure

1. Read repository instructions and record the fixed base, branch, exact `HEAD`
   and dirty-work inventory in the existing delivery record. Reuse a suitable
   clean isolated checkout; stop on unrelated or uncertain changes. Never stash,
   reset or absorb user work. Inventory checkouts through their owning runtime
   and apply the lifecycle rules below; never infer ownership from their names.
2. Choose solo or delegated implementation. Tightly coupled work may stay with
   the lead. Delegate only when independent work, isolation or specialist
   investigation justifies it. Use runtime metadata to establish independent
   final-review capability; do not spawn a capability-only reviewer. Follow
   [Evidence and review](evidence-and-review.md) for owner-driven testing,
   proportional checks and evidence reuse.
3. For supplied task graphs, verify unique IDs, declared dependencies and an
   acyclic graph; reserve `none` for the root marker. Treat legacy plans without
   dependency metadata as sequential. Keep an unsplit request in one item;
   do not manufacture slices or agents. Record shared-file/interface constraints.
   A dependent starts only after prerequisite integration and affected checks,
   including the planned boundary evidence under
   [to-plan's boundary-validation rule](boundary-validation.md).
4. When delegating, apply [subagent selection](subagent-selection.md) and the
   runtime requirements below. Confirm edit, validation, commit and resumable repair
   capability; retain the owner handle. Fit descendants within actual caller,
   runtime and repository capacity and respect Project scheduling priority.
   Give each concurrent writer a distinct isolated checkout; serialize shared
   writes and dependencies. Never switch a checkout used by an owner or process.
   Reference the existing record for scope, acceptance, base, path, branch,
   ownership and checks; no new permission packet is needed. Tell owners they
   are not alone and must preserve others' changes. Keep architecture with the
   lead and task repairs with their original owner. If that owner is lost,
   reconcile and quiesce its writers before recording an explicit reassignment.
5. Have each owner implement, run meaningful affected checks, self-review and
   commit only owned changes. Record results and evidence pointers once;
   delegated owners report in the [subagent selection](subagent-selection.md)
   return format with each command's exit code, tested SHA, tail and log path.
   For delegated work, inspect the complete task diff, commit range, clean state
   and check evidence, including the complete log when acceptance needs it,
   before integration; assertions alone are insufficient. Reuse
   compatible passing evidence. Return incomplete work to its owner. Solo work
   needs no separate task-acceptance receipt.
6. Integrate accepted work in dependency order. Record the clean pre-attempt SHA.
   If a Git operation conflicts before completion, abort that operation and
   verify the exact SHA and clean state are restored; otherwise stop. Give the
   original owner the conflict to repair on a fresh unique branch from that base
   in an idle isolated checkout, preserving the original task branch and commits.
   After completed integration, record the resulting SHA and renew only affected
   validation.
   Release dependents without a second acceptance ceremony.
7. If completed integration fails checks, preserve the failed integrated `HEAD`,
   pause dependents and repair forward. Never reset or discard it. Investigate
   unclear attribution read-only, retain unaffected owner branches, and have the
   responsible owner repair from the failed head. Account for dirty validation
   artifacts before continuing. Inspect and integrate the repair, then rerun
   affected checks; stop if the failed state cannot be preserved or repaired.
8. Apply [Evidence and review](evidence-and-review.md), complete lifecycle
   accounting at completion, interruption and blockers, and satisfy the
   entrypoint's finish gate.

## Runtime requirements

Choose agents by capability, not runtime role name:

- Implementation owner: can edit, run validation and commit in its assigned
  checkout, and can be resumed in the same session for repairs.
- Independent reviewer: starts without the implementation conversation and
  makes no writes. When the runtime cannot enforce read-only access, verify
  afterwards that the reviewer's checkout is unchanged.

Runtime caveats:

- [Claude Code](https://code.claude.com/docs/en/sub-agents): `Explore` and
  `Plan` are one-shot and cannot own an item. The lead creates each run-owned
  plain Git worktree with
  `git worktree add -b <task-branch> <path> <integrated-sha>`, verifies its
  branch and SHA, and passes the absolute path in the brief. Never use
  `Agent(isolation: "worktree")`; it bases on the default branch, not the
  integrated `HEAD`.
- [OpenCode](https://opencode.ai/docs/agents): `build` is a primary agent, not
  a delegable subagent.
- [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent):
  no built-in subagent; inspect its delegation extension and agent
  definitions. A bare or non-resumable Pi cannot own an item: stop and report
  it.

## Worker checkout lifecycle

Maintain this record in the workflow's existing reporting context, not a new
committed ledger. Record each checkout's provenance and runtime identity, exact
path, owner, task branch and base, accepted commits, integration and check
evidence, active use, and disposition. Distinguish the stable integration
checkout, run-created worker slots, and pre-existing or adopted checkouts.
Never infer ownership from a directory name. Pre-existing, adopted, pinned,
and shared checkouts are not automatically retired.

Release a slot only after its accepted task commit and original branch ref are
recorded and preserved, integration succeeds, affected checks pass at the exact
integrated SHA, its owner and processes stop using it, it is clean, and needed
untracked or ignored artifacts are accounted for. Otherwise retain it. Before
reuse, create a fresh unique task branch from the recorded current integrated
SHA, verify the branch and SHA, and hand off the exact path, branch, base, and
instructions. Never reset or delete an old branch to reuse its checkout.

Retire released surplus slots when remaining work no longer needs their
capacity, retaining one for sequential work and only justified capacity for
future concurrent writers. At completion, retire all eligible run-created
worker slots. On a blocker or interruption, retire eligible surplus when
execution remains available; retain active, unfinished, failing, dirty, or
otherwise unsafe checkouts. If interruption prevents cleanup, report it at the
next opportunity. Preserve the integration checkout, user work, and required
ignored artifacts. Do not force cleanup to meet a capacity cap.

Use the runtime's native operation for managed worktrees and verify retirement
through provider inventory. For plain Git worktrees owned by the run, remove
only the exact eligible path without force and verify it is absent from
`git worktree list --porcelain`. Never shell-delete a managed checkout, force
removal, prune globally, or delete branch refs. If ownership or eligibility is
uncertain, retain and report the checkout.

Account for every run-created checkout as retired with verified readback or
retained with a reason. Record the integration checkout as retained and explain
retained exclusions. If eligible retirement fails or cleanup capability is
missing, report code verification separately and mark the workflow
cleanup-incomplete; do not claim overall completion. Include the exact path,
error, and provider readback. Do not retry blindly.


## Ownership boundaries

- Keep remote mutations with the controller unless the user explicitly grants
  another owner and repository instructions permit it. PR and tracker delivery
  are outside this workflow.
- Reuse each item owner for its repairs and follow-up checks. Do not split an
  item across agents or transfer it merely to clear a review finding.
- Read-only helpers may discover or review independently. They do not edit,
  commit, or replace an implementation owner.
- Never absorb another item's edits or pre-existing user changes into an
  owner's commit.
