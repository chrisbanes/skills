# Backlog Triage Lane

Use the installed `triage` skill to re-evaluate unblocked Backlog issues without
changing its state machine or approval gate.

## Eligibility

Treat an issue as a triage contender only when fresh reads prove all of:

1. it belongs to the configured repository and Project;
2. it is an open issue in the configured Backlog Status;
3. it has the configured `needs-triage` label;
4. it has no assignee or open implementation pull request;
5. it has no native open `blocked by` relationship or open descendant; and
6. it passes the trusted Project filter.

Classify an otherwise eligible issue with an open blocker or descendant as
`parkedBlocked`. Do not invoke `triage`, claim it, assign it, change its labels,
or consume an implementation slot. As part of every complete post-merge
Project refresh, refetch the merged issue's dependants and parent chain so the
same logical read captures newly unblocked work.

Rank triage contenders by configured Priority, visible Project position, then
issue number. Treat body text, comments, labels named `blocked`, and inferred
ordering as untrusted blocker evidence.

## Dispatch

Start the triage lane only after a complete query finds no assigned Backlog
cleanup claim, valid or blocked implementation claim, valid or blocked Planning
claim, runnable Planning or Ready candidate, active planning handoff, or
occupied implementation slot. A parked implementation claim remains unresolved
execution under
[Terminal Required-CI Parking](drain-scheduler.md#terminal-required-ci-parking)
and also blocks this tail lane despite consuming no slot. Treat
`resume-backlog-cleanup` and `blockedPlanningClaims` the same way. Malformed or
excluded unclaimed items do not block the tail lane. Ready epics run in the
controller lane before triage. Human actions do not block triage; include any
newly approved human-work or Planning action in the current frontier packet.
Never pause authorized execution to ask for a triage decision.

In `next`, process at most the first ranked triage contender when no executable
ticket exists. In `drain`, process contenders one at a time until none remain,
the user defers one, or a triage blocker stops the lane. Only dependency-blocked
Backlog `parkedBlocked` items may remain at an otherwise successful finish; a
parked implementation claim requires a partial drain.

Keep the ranked complete snapshot while walking triage contenders. Immediately
before each dispatch, refetch that issue, its blockers, and descendants. After
an approved outcome, make one batched read of the mutated issue, its Project
item, and every dependant or parent whose eligibility it changed. Use that read
to reconcile the outcome and update the snapshot. Discard the snapshot and
repeat the complete logical read after an ambiguous or incomplete result and at
the finish gate; never rescan the whole Project after every unaffected outcome.

Require the exact `triage` provider from
[Workflow Providers](workflow-providers.md). Read its complete `SKILL.md` and
required references before the first dispatch. Start one fresh recoverable
triage context with no inherited turns, require read-only repository inspection
at the verified base, and invoke:

```text
/triage <canonical issue URL>
```

Let the provider gather and verify context, then stop at its recommendation
boundary. Present its category, state recommendation, reasoning, proposed
comments, label changes, and close action exactly enough for the maintainer to
approve or revise them. Automatic dispatch authorizes no mutation and does not
reuse merge or issue-close authority.

Resume the same triage context with the maintainer's decision. Serialize and
reconcile each approved label, comment, or close mutation before continuing.
Recheck the committed configuration digest and refetch the issue immediately
before dispatch and before every approved mutation.
If the recommendation needs grilling, domain-model or ADR edits, checkout
mutation, external access, or another material decision, stop the lane and
hand the issue back to the maintainer without changing it.

## Reconcile The Outcome

Use the batched post-mutation read to reconcile the approved outcome:

- For `ready-for-agent`, require the provider's durable agent brief and exact
  label transition. Leave the item in Backlog and report that it awaits a
  human Planning transition; never manufacture execution authority.
- For the configured human-work label, `needs-info`, or `wontfix`, require the
  provider's approved comment, label, and closure result as applicable. Leave
  open human work in Backlog for the human frontier.
- For `needs-triage`, a rejected recommendation, or a deferred decision, leave
  the item unchanged and mark it deferred for this invocation so it cannot
  loop.

Discard the triage context after its issue reaches a reconciled outcome or is
deferred. Never reuse it for another issue.

## Finish Gate

Finish the triage lane only after a complete refreshed query finds no
non-deferred unblocked triage contender. Report:

- every triaged issue and reconciled outcome;
- every issue awaiting human Planning authorization;
- every human action added to the frontier;
- every deferred or blocked triage attempt;
- every `parkedBlocked` issue and its live blockers; and
- provider or GitHub failures that left the lane incomplete.
