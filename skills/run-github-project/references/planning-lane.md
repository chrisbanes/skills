# Planning Lane

Use this lifecycle for Project items in `Planning` and for the verified handoff
into implementation.

## Authority And Plan State

Require both:

1. the exact `ready-for-agent` label; and
2. the latest transition into `Planning` to be either:
   - a non-automated event by a configured execution approver; or
   - the authenticated runner's non-automated machine requeue backed by its
     verified earlier Ready handoff.

The human transition authorizes autonomous plan publication and implementation.
The verified Ready handoff carries that authority across a machine requeue.
Ordinary issue-body or comment edits do not revoke it. A newer human transition
into `Planning` explicitly requests a new plan.

Recognize exactly one implementation-plan comment containing:

```html
<!-- to-plan:implementation-plan:v1 -->
```

Classify it as:

- **missing** when no marker comment exists;
- **current in Planning** when the authenticated runner authored it, it was last
  updated at or after the authorizing Planning event, and its planned branch
  matches the configured base;
- **stale after requeue** whenever the runner moved the item back to Planning,
  even when the marker itself is unchanged;
- **stale** when a newer authorizing Planning event exists, the comment was
  edited after its runner-authored Ready handoff, its author differs, or its
  planned branch no longer
  matches.

Do not recognize `## Agent Brief` or any legacy fallback. Record the plan
comment ID, permalink, author login, digest, creation and update times, planned
branch, and planned SHA in the authority lease.

A foreign-authored marker is a semantic planning blocker. Preserve assignment
and require its author or a maintainer to remove it; never edit it or create a
second marker.

## Plan A Planning Item

1. Enter the controller lane, assign the issue exclusively to the authenticated
   user, refetch and verify the assignment, then release the lane. Reconcile
   an ambiguous assignment before retrying. Preserve the assignment through
   planning and implementation.
2. Use one dedicated, reusable, clean planning worktree at a stable
   controller-recorded path outside the checkout, detached at the configured
   base. Refresh it only between tickets; never discard ignored build state.
3. Start a fresh ephemeral planning agent and invoke:

   ```text
   /to-plan --auto <canonical issue URL>
   ```

4. Allow bounded read-only discovery descendants from currently spare agent
   capacity. They never own the ticket or mutate state.
5. Never preempt planning after it starts. Planning does not occupy an
   implementation slot and does not reserve the controller lane during read-only
   work.
6. At the publish boundary, wait for the controller lane. Let `to-plan` create
   or update only its marker comment, then refetch it from GitHub.
7. Verify the exact marker, authenticated-runner author, digest, permalink,
   planned branch, planned SHA, and timestamps. Treat missing `to-plan` as an
   issue-local planning blocker; it must not block implementation items with
   current plans.
8. Move the item to `Ready to implement` as the authenticated runner. Refetch
   and require a non-automated Ready transition by that runner after both the
   Planning event and the plan's latest update. That reconciled event attests
   that `to-plan --auto` revalidated an identical older plan even when it made
   no comment edit.
9. In `next`, or when an implementation slot is free, move the same item to
   `In progress`, verify the full authority lease, and start its slot. Otherwise
   preserve the assigned verified Ready handoff, release the planner, and
   resume that handoff before new claims when a slot frees.

After a successful handoff, require the planning worktree to be clean with no
retained draft, detach it, snap it to the verified base, and keep it for reuse.
Preserve its exact path, base, and draft only when planning blocks and recovery
requires them.

Project schema mutations are never part of this procedure. Stop with the
required configuration repair when an expected field or option is missing.

Give each planning attempt a 30-minute deadline unless the user or repository
sets another. Agent loss, crash, or timeout is a liveness failure, not
preemption:

1. stop the failed planner when possible and release its agent capacity;
2. refetch assignment, Status, Planning and Ready events, and the marker plan;
3. reconcile an ambiguous comment or Status mutation before retrying;
4. complete an already-verified handoff, or restart a fresh planner in the same
   clean planning worktree;
5. after three failed attempts, preserve the assignment, block that planning
   item, release the lane, and continue unrelated work.

## Resume And Re-plan

Resume an assigned `Planning` item before starting new Planning work:

- run planning when the plan is missing or stale;
- finish the Ready handoff when the plan is current.

Resume an assigned `Ready to implement` item only when its current plan and the
later runner-authored Ready event form a verified handoff. Otherwise preserve
it as a blocked planning claim without consuming an implementation slot.

Before the Ready or In-progress transition, compare the planned SHA with the
current base:

- accept non-overlapping committed drift after screening the changed files,
  symbols, seams, contracts, and validation;
- move the item back to `Planning` when drift overlaps or overlap is uncertain.

That runner-authored machine requeue is the only automatic backward Status
transition. The ranker requires its verified prior Ready handoff, retains that
authority, and always resumes planning rather than handing the old plan back
directly. Any fresh human Planning transition supersedes it and requests a new
plan.

For a plan edit or another live-eligibility invalidation after Ready, preserve
the blocked handoff and require a human transition to Planning. That new event
authorizes re-planning; never silently bless the changed plan.

Semantic planning blockers are issue-local. Preserve the assignment and retry
them only when authoritative inputs change. Retry transient planner/tool
failures through the bounded reconciled recovery above. Never consume an
implementation slot merely to wait for a planning blocker.

## Scheduling

Use the ranker as the single selector for both lanes. Process classes in this
order:

1. existing implementation and PR claims;
2. resumable Planning and verified handoff claims;
3. new `Ready to implement` candidates;
4. new `Planning` candidates.

Within a class, use configured Priority, visible Project position, then issue
number.

In `next`, selecting a Planning item commits the invocation to that one issue:
plan it, hand it off, implement it, merge it, and reconcile it before finishing.
Do not select another issue.

In `drain`, follow the
[Drain Scheduler](drain-scheduler.md#scheduling) for planner dispatch,
active-agent capacity, and non-preemption.

## Migration Gate

Before adopting this schema:

1. require zero existing `In progress` items;
2. have a human create and verify `Planning` and `Ready to implement`;
3. configure their option IDs and execution approver logins;
4. have an execution approver move every legacy Ready item to `Planning`;
5. run `to-plan --auto` for each item, including those with an existing marker,
   before creating its runner-authored Ready handoff.

Do not automate Project option creation or rename. Do not preserve an Agent
Brief compatibility path.
