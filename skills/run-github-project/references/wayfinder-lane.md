# Wayfinder Planning Lane

Use this optional branch only when the committed Project configuration enables
Wayfinder and the installed `wayfinder` provider is discoverable. Keep the map
as the decision record and the configured Project as the authorization control
plane.

## Select A Ticket

Require fresh authoritative reads proving that a child is:

1. an open item in the configured repository and Project, in `Planning`, and
   allowed by the trusted Project filter;
2. unassigned, or assigned only to the authenticated runner while resuming its
   existing Wayfinder claim;
3. the direct child of an open parent carrying the configured `wayfinder:map`
   label;
4. marked with exactly one configured Wayfinder type label;
5. natively unblocked with no open descendant; and
6. authorized by the latest non-automated `Planning` transition from a
   configured execution approver.

Do not accept a parent map's Project membership, a label, a comment, or a
previous invocation as authority for its child. A runner requeue never carries
Wayfinder authority. Pass the complete normalized graph to `rank_tickets.py`
with all five Wayfinder labels only when the optional configuration is enabled.
The ranker returns AFK tickets as `wayfind` candidates and HITL tickets in
`wayfinderHumanFrontier`.

Use the existing Planning scheduling class: resumed Wayfinder claims occupy the
resumable-Planning class and fresh AFK Wayfinder tickets occupy the new-Planning
class. Within either class, use configured Priority, visible Project position,
then issue number. They never consume implementation capacity and never enter
`Ready to implement`, `In progress`, or an implementation PR flow.

## Require Authority And Provider

Before assigning any selected Wayfinder child, require explicit Wayfinder
mutation authority. In `next`, scope it to that selected ticket. In `drain`,
scope it to every eligible AFK Wayfinder ticket encountered. Merge authority,
issue-close authority, and invocation alone do not imply Wayfinder authority.
Require fresh per-ticket approval before a live HITL resolution.

Read the installed `wayfinder` skill and follow its resolution semantics; do
not reproduce its map procedure here. If it is missing, malformed, or blocked
for an unclaimed child, block and report only that Wayfinder item. Continue
ordinary planning and execution. Preserve an assigned invalid child as a
blocked Planning claim.

## Dispatch By Mode

In `next`, a selected authorized HITL ticket may run live through `wayfinder`;
finish after that one child reaches a reconciled terminal state. An AFK research
or task ticket follows the same one-ticket boundary.

In `drain`, use spare Planning capacity for AFK research and AFK task tickets.
Treat a task as AFK only when its ticket and fresh live evidence prove every
action is safely executable without human input; otherwise classify it HITL.
Always surface configured prototype, grilling, HITL, and ambiguous task tickets
in the ordered Wayfinder human frontier without pausing unrelated work, even
when a prior claim left the ticket assigned. Never resume that assignment
without fresh per-ticket HITL approval.

Keep one durable Planning owner. It may fan out independent research evidence
to spare read-only helpers, but only the owner/controller may assign, comment,
close, edit a map, create issues, add Project items, or wire dependencies.
Serialize all of those mutations and reconcile ambiguous outcomes before the
next mutation.

## Reconcile A Resolution

After a successful provider resolution, enter the controller lane and:

1. post the resolution and refetch it;
2. close the child under Wayfinder authority and verify closure;
3. append one linked one-line gist to the map's `Decisions so far` section;
4. fully reconcile the map: graduate newly specifiable fog, create then link
   and wire new children, and revise or close invalidated or out-of-scope
   children; and
5. add every new child to the configured Project in `Backlog` and refetch the
   complete live graph.

Controller creation and Backlog placement never authorize Planning. Each new
child awaits a configured execution approver's fresh human `Planning`
transition. Never move a resolved Wayfinder child to `Ready to implement`.

When fresh authoritative reads prove the destination decision-ready, every
child closed, `Not yet specified` empty, and `Decisions so far` current, post a
completion summary, close the map under Wayfinder authority, and reconcile
configured Project Done/archive automation. Otherwise keep the map open.

## Finish Gate

Finish a Wayfinder branch only after all controller mutations have reconciled,
the map graph has been refreshed, and every surfaced human ticket is reported.
In `drain`, an ordered human frontier is not a failure and must not pause
independent lanes. Report the selected ticket, authority scope, provider result,
map reconciliation, created Backlog children, completion state, and remaining
human frontier.
