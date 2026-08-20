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
Pass the invocation mode to the ranker. In `next`, AFK and HITL tickets are
normal `wayfind` candidates or `resume-wayfind` claims. In `drain`, only AFK
tickets are candidates and HITL tickets appear in `wayfinderHumanFrontier`.

Use the existing Planning scheduling class: resumed Wayfinder claims occupy the
resumable-Planning class and eligible fresh Wayfinder tickets occupy the
new-Planning class. Within either class, use configured Priority, visible
Project position, then issue number. They never consume implementation capacity
and never enter `Ready to implement`, `In progress`, or an implementation PR
flow.

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

After a successful provider resolution, enter the controller lane. Before any
terminal mutation, compute one exact reconciliation plan covering the map gist,
fog changes, child creates/updates/closes, parent-child and dependency edges,
Project additions, child terminal state, and possible map completion. Post and
refetch the resolution, then post and refetch a durable runner-authored marker
comment with this machine-readable payload:

```json
{
  "markerVersion": 1,
  "mapNumber": 7,
  "projectItemId": "PVTI_child",
  "resolutionPermalink": "https://github.com/owner/repository/issues/52#issuecomment-1",
  "configurationDigest": "sha256:configuration",
  "planDigest": "sha256:semantic-reconciliation-plan",
  "plannedMutations": [
    {"kind": "update-map", "issueNumber": 7, "digest": "sha256:map-body"}
  ]
}
```

Wrap it with the marker
`<!-- run-github-project:wayfinder-reconciliation:v1 -->`. Record every
mutation with a unique operation key and the exact intended state. For an
existing object, also record its stable node ID or issue number. For a new
issue, include the operation key in its marker-owned body so recovery can find
the result before retrying creation. Exclude presentation-only text from
`planDigest`. Assignment is the durable lease. Do not close the child, edit the
map, or perform another terminal mutation until the marker is authoritative.

Apply the recorded plan idempotently and in this order:

1. append one linked one-line gist to the map's `Decisions so far` section;
2. fully reconcile the map: graduate newly specifiable fog, create then link
   and wire new children, and revise or close invalidated or out-of-scope
   children; and
3. add every new child to the configured Project in `Backlog`, then refetch and
   verify the complete live graph;
4. close the resolved child when still open and verify closure;
5. refetch its exact Project item by the marker's node ID and apply the
   configured Done automation contract exactly as for a merged issue: wait for
   and verify configured Status/archive automation, or set and verify only
   Status Done when Status automation is absent; never archive or remove it
   manually; and
6. when the marker's verified completion predicate now holds, post the map
   completion summary, close the map, and reconcile its configured Project
   Done/archive outcome in the same way.

Controller creation and Backlog placement never authorize Planning. Each new
child awaits a configured execution approver's fresh human `Planning`
transition. Never move a resolved Wayfinder child to `Ready to implement`.

When the completion predicate does not hold, keep the map open. Unassign the
resolved child only after every recorded mutation and every applicable terminal
Project outcome is verified. Leave the marker comment in place as inert audit
evidence.

## Resume Reconciliation

At startup, query runner-assigned marked Wayfinder children independently of
the ordinary open-Project inventory. Refetch the marker, its recorded Project
item even when archived, the child, the direct map parent even when closed, and
the complete live map graph. Require exactly one authoritative marker, its
author and sole assignee to be the authenticated runner, its Project item and
map identities to match, and its configuration digest to match the invocation's
committed configuration.
Normalize it as `wayfinderReconciliation`; the ranker returns
`resume-wayfinder-reconciliation` ahead of new Wayfinder work.

Reapply only missing recorded mutations, reconciling an ambiguous outcome by
authoritative read before retrying. A closed child or map and an already-Done
or archived Project item satisfy their corresponding steps. Stop and preserve
the assignment if the plan, identity, configuration, or remote outcome cannot
be proven. Never infer a replacement plan or publish a second marker.

## Finish Gate

Finish a Wayfinder branch only after all controller mutations have reconciled,
the child has reached its configured Done/archive outcome, its assignment has
been removed last, the map graph has been refreshed, and every surfaced human
ticket is reported.
In `drain`, an ordered human frontier is not a failure and must not pause
independent lanes. Report the selected ticket, authority scope, provider result,
map reconciliation, created Backlog children, completion state, and remaining
human frontier.
