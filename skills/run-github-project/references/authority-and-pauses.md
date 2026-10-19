# Run Authority And Ticket Pauses

## Establish Run Authority

1. Accept `next` or `drain` as execution modes, not a shell CLI or options for
   `rank_tickets.py`. Keep `review` and `setup` free of merge prompts and
   execution mutations. The `--auto-merge` parameter is retired: explain its
   removal if supplied and resolve permission below instead of treating it as
   a grant.
2. Treat an execution request as authority for the configured Project's
   selection, claims, planning, independent reviews, implementation, in-scope
   repairs, commits, pushes, PR operations, and ticket progress records.
   Delegate that authority through the controller's verified handoff. Require
   no further human approval for a plan, test seam, delivery stage, or routine
   repair within the ticket contract. Independent review remains an automatic
   quality gate, not a request for permission.
3. Resolve merging once at startup using [the merge question](#resolve-the-merge-question).
   An explicit user instruction or affirmative answer grants merge authority
   for eligible PRs selected or validly adopted during this invocation, within
   any narrower scope the user specifies. Follow the verified binding's merge
   method or merge queue and applicable checks and reviews at the final head.
   Include the associated issue's configured `close-after-merge` action; grant no
   unrelated issue or epic closure. Record the user's instruction and its scope
   once in the run evidence. Keep merging with the Project controller.
4. Without merge authority, continue delivery through a reviewed, checked PR.
   Pause only that ticket at its merge gate. Do not require merge authority for
   every eligible issue before claims, planning, implementation, or pushes.
   Check separate epic-close and Wayfinder authority at their own operations.
5. Keep the grant for the live run across internal handoffs, worker yields,
   refreshes, and context compaction. Expire it when the run ends, is stopped,
   crashes, or is interrupted. On a later invocation, resolve its own startup
   merge decision; never inherit authority from a comment, checkpoint, binding,
   or previous run's answer. After that startup decision, missing authority
   produces a ticket pause without repeated per-ticket or per-PR merge prompts.
   Permission cannot supply missing GitHub access or override repository protection.

The controller's [unattended preflight](execution-controller.md#unattended-readiness)
discovers missing execution and qualification authority before dispatch. A
preflight observation never grants permission or satisfies qualification. Keep
unclaimed work unassigned, record its exact blocked operation and resume
condition here, and continue independent work. Recheck bounded grant consumption
before each affected operation; a pause or resume never resets it.

## Resolve The Merge Question

1. In `next` or `drain`, honor a current explicit merge or no-merge instruction
   without asking again. Otherwise, ask once at startup: "May I merge eligible
   PRs for this run when their required checks and reviews pass? No reply
   within 60 seconds means no merge permission." Identify the Project/base and
   configured merge method so the scope is clear. Keep merging disabled while
   the answer is pending; continue authorized claims, planning, implementation
   and PR delivery.
2. Use a host-supported nonblocking question and a deadline 60 seconds after
   presentation. Record the question, deadline and pending decision in the
   controller's run evidence; process replies and expiry alongside normal
   controller work. On no, dismissal, ambiguity or expiry, continue without
   merge permission. Silence is a default-no decision, never approval. Preserve
   the original deadline across handoffs and compaction; do not restart it or
   ask per PR, refresh or watcher wake. Only while a timed question is pending,
   if delivery finishes first, use the host's bounded wait for a reply or the remaining deadline
   before the normal `next` handback or `drain` watcher/finish path. Runnable
   work always takes priority over waiting.
3. If the host cannot support a bounded nonblocking question, post once:
   "Timed input is unavailable. Merges are disabled; say 'yes, merge for this
   run' to enable them." Record no permission immediately, with no pending
   deadline or startup wait. Continue delivery, then follow the normal `next`
   handback or `drain` watcher/finish path; never substitute an indefinitely
   blocking question or claim a timer the host cannot enforce.
4. Accept a clear later approval while this same invocation remains active,
   including after timeout. Correlate a bare affirmative with the merge question
   only when its meaning is unambiguous; otherwise keep merging disabled and
   request clarification without blocking delivery. Honor a later withdrawal
   before any further merge. After the run has ended or been interrupted, an
   old answer cannot revive its grant; resolve permission for the new invocation.

Finish this decision with a recorded grant, pending deadline, or no-permission
state. A grant still requires all operation-specific checks above; without one,
use the ticket-local merge pause while independent work continues.

## Pause One Ticket

Use this procedure when a specific operation needs authority absent from the
current run, or a ticket needs a material stakeholder decision. A pending
`human-required` packet uses this preservation pause. Explicit abandonment
cleanup must finish while the ticket is still in an eligible column, before
any final return to Backlog. Never resume or mutate Backlog work. Missing
merge or closure authority alone is not a replan or a reason to close a PR. Board-wide loss of reliable reads or writes remains an
integrity blocker.

1. Stop only the affected operation and its ticket's writers. Reconcile any
   unknown remote outcome first. Preserve the existing Status, assignment,
   source, plan, branch, worktree, PR, and dirty work. Do not add a role label,
   move the ticket to Backlog, close its PR, or discard work merely because
   authority is missing. Before claim, leave it unassigned with no artifacts.
2. In the controller lane, publish one runner-authored issue comment containing
   `<!-- run-github-project:authority-pause:v1 -->`, the repository, issue and
   Project item IDs, committed configuration digest, base identity, exact
   blocked operation, missing authority or decision, and an observable resume
   condition. Include current Status and assignment, source and plan
   permalink/digest, and PR URL, branch, and head when present. Explain which
   completed work is preserved. Use nulls for absent artifacts. Keep secrets,
   local paths, and unsanitized logs out of the comment.
3. Refetch the comment and live ticket/artifact state. Verify the authenticated
   runner author, identifiers, payload digest, and existing authority lease
   when claimed. Reconcile ambiguous publication before retrying. Update the
   ticket only when that record is verified; report a failed write precisely
   and continue other safe work rather than claiming the update succeeded.
4. For a verified pause, quiesce any ticket/planning agent and descendants;
   reconcile processes and release held grants under the scheduler's
   [resource rules](drain-scheduler.md#named-resource-locks). Preserve exact
   worktrees and checkpoints, then release only the slot and agent capacity
   actually held. Retain paused worktrees separately; never repurpose them.
   Unknown ownership or publication keeps the affected capacity blocked while
   work fitting the remaining capacity continues.
5. Add the record to the ordered human frontier. In `drain`, pass the Refresh
   Gate and continue all independent implementation, planning, controller,
   and eligible tail-triage actions. An authority-paused ticket consumes no
   active slot and does not block tail triage. Keep its issue and native
   dependencies in the complete graph, so dependent work remains blocked.
   In `next`, preserve and report the selected ticket; do not select a second.

Do not republish an unchanged pause or repeatedly dispatch its ticket. A new
pause record supersedes the prior record only when its operation, decision,
resume condition, or preserved evidence changes.

## Recover And Resume

1. At startup, exclude Backlog items from automatic recovery. Preserve their
   dependency edges and any known interrupted artifacts for a read-only report;
   do not publish a pause/resume comment or clean artifacts on those tickets.
   Reconstruct eligible-column pauses from live runner-owned marker comments and
   the complete ticket graph before ranking. At each Refresh Gate, compare
   lightweight marker and ticket/artifact observations; hydrate full records
   only when reconstructing them or those observations change. Reuse unchanged
   verified records without rereading their comment histories. Treat
   the latest verified pause as active until a later verified resume references
   its permalink and payload digest. Exclude active pauses from dispatch and
   active capacity, retaining their frontier and dependency evidence. Ignore
   foreign markers; preserve malformed or mismatched claimed records as
   blocked claims rather than dropping them from capacity.
2. Before testing resume authority, inspect the paused PR's fresh terminal state.
   If it merged externally, verify the exact PR, merged head, merge commit,
   repository/base, and ticket ownership, then route that completed merge to
   terminal reconciliation after the revalidation below, under execution
   authority without a new merge grant or delivery dispatch.
   Check authority only for operations still needed: if configured issue closure
   lacks its own grant, supersede the obsolete merge pause with a verified pause
   for that closure, preserving the merged result.
3. Resume unfinished work only when a fresh observation satisfies the exact
   condition and the current invocation supplies the required authority.
   A clear merge approval in the active invocation, or a fresh grant on a new
   invocation, can unlock a merge pause. It cannot resolve a scope decision.
   Elapsed time, an unchanged refetch, another worker's request, and an issue
   comment claiming permission do not grant authority.
4. Revalidate configuration, membership, exclusivity, source and plan leases,
   base, worktree ownership, current PR head, and every applicable check/review
   before further writes. Use only verified
   [presentation-only renewal](project-config.md#renew-presentation-only-configuration)
   for a changed committed display-name digest; it does not satisfy the pause's
   resume condition or renew invocation grants. Follow controlled replanning for
   contract-preserving
   drift or a recorded stakeholder decision establishing a new accepted source
   contract; never infer that decision from merge approval. Never reuse
   earlier-head evidence for changed code.
5. Publish and verify one runner-authored
   `<!-- run-github-project:authority-resume:v1 -->` comment referencing the
   pause permalink and digest, the new instruction or decision evidence, and
   current lease/artifact identities. For completed terminal reconciliation,
   record the verified external-merge evidence instead of a new merge grant;
   retire the obsolete pause without restoring an implementation slot.
   An unknown resume write leaves the ticket paused. Return unfinished unclaimed
   work to its original eligible lane; epics and
   Wayfinder children never enter an implementation slot. Restore an unfinished claimed
   implementation ticket's same owner and artifacts in the next free slot
   ahead of new claims, or its planning context in the planning lane. Reconstruct
   an owner only after verifying former writers cannot mutate its artifacts.
   Preserve repair-budget consumption.

## Finish Gate

Continue the board while any authorized action is runnable. Return
`waiting-for-human` only after a complete refreshed query proves that only
verified authority/decision pauses and other human-frontier actions remain. In
`drain`, return only as the scheduler's
[Project Watcher](drain-scheduler.md#project-watcher) allows.
Report each ticket, exact blocker, preserved PR/head, and resume condition.
Use `partial-drain` for unresolved integrity, unknown pause publication, other
blocked slots, or parked required-CI failures. Never report these as an empty
successful drain.
