# Wayfinder Todo Lane

Use this optional branch only when the committed Project configuration enables
Wayfinder and the installed `wayfinder` provider is discoverable. Keep the map
as the decision record and the configured Project as the execution control
plane.

In every human-facing frontier, narration, comment, and final report, refer to
the map and its children as `[title](URL)`. Use bare numbers and node IDs only in
machine-readable payloads and diagnostics.

## Select A Ticket

Require fresh authoritative reads proving that a child is:

1. an open item in the configured repository and Project, in `Todo`, and
   allowed by the trusted Project filter;
2. unassigned, or assigned only to the authenticated runner while resuming its
   existing Wayfinder claim;
3. the direct child of an open parent carrying the configured `wayfinder:map`
   label;
4. marked with exactly one configured Wayfinder type label;
5. natively unblocked with no open descendant.

Current Todo membership supplies authorization. Do not fetch or inspect its
transition history. Backlog children never qualify, including claimed items
with reconciliation markers.

Require the direct parent map's current Project column to be Todo or a later
configured column too. Block missing, unknown, or Backlog parent membership;
child authorization never grants permission to process its Backlog map.

Do not inherit a child's membership, Status, type, or blockers from its parent
map, a comment, or a previous invocation. Pass the complete normalized graph to `rank_tickets.py`
with all five Wayfinder labels only when the optional configuration is enabled.
Pass the invocation mode to the ranker. In `next`, AFK and HITL tickets are
normal `wayfind` candidates or `resume-wayfind` claims. In `drain`, only AFK
tickets are candidates; unassigned HITL tickets appear in
`wayfinderHumanFrontier` and assigned HITL tickets in `wayfinderClaimedHitl`.

When the user explicitly names a Wayfinder child in `next`, normalize its issue
number and pass `--wayfinder-ticket`. Select it instead of every new candidate,
even when Project ordering would choose another item. Never use explicit
selection to bypass another current-user claim; stop and report those durable
claims instead. Reject explicit Wayfinder selection in `drain`.

Use the existing Todo scheduling class: resumed Wayfinder claims occupy the
resumable-Todo class and eligible fresh Wayfinder tickets occupy the
new-Todo class. Within either class, use configured Priority, visible
Project position, then issue number. They never consume implementation capacity
and never enter `Ready to implement`, `In progress`, or an implementation PR
flow.

## Require Authority And Provider

Before assigning any selected Wayfinder child, require explicit Wayfinder
mutation authority. In `next`, scope it to that selected ticket. In `drain`,
scope it to every eligible AFK Wayfinder ticket encountered. Merge authority,
issue-close authority, and invocation alone do not imply Wayfinder authority.
Require fresh per-ticket approval before a live HITL resolution.
If a required grant is absent, record an unclaimed
[authority pause](authority-and-pauses.md#pause-one-ticket) for that child and
continue other drain work. Do not hold up the board for a permission prompt.

Read the installed `wayfinder` skill and follow its resolution semantics; do
not reproduce its map procedure here. If it is missing, malformed, or blocked
for an unclaimed child, block and report only that Wayfinder item. Continue
ordinary planning and execution. Preserve an assigned invalid child as a
blocked Todo claim.

## Dispatch By Mode

In `next`, a selected authorized HITL ticket may run live through `wayfinder`;
finish after that one child reaches a reconciled terminal state. An AFK research
or task ticket follows the same one-ticket boundary. The current interactive
context is that one Wayfinder session so HITL remains a live human exchange.

In `drain`, use spare Todo capacity for AFK research and AFK task tickets.
Treat a task as AFK only when its ticket and fresh live evidence prove every
action is safely executable without human input; otherwise classify it HITL.
For every non-research AFK child selected by `drain`, start a fresh Wayfinder
provider context and never reuse it for another ticket. That provider context
is the canonical Wayfinder session boundary. The drain controller may continue
with another AFK child only through another fresh context.

For a research child, require the provider to invoke the installed `research`
skill in a background subagent. Give it the ticket question and map Notes,
require primary-source citations in one repository Markdown artifact on a
throwaway `research/<name>` branch in an isolated research worktree, and return
its linked context pointer to the Wayfinder owner. A drain invocation may
process multiple research tickets under Wayfinder's research exception, but it
must claim each child before dispatch. A generic discovery helper is not a
substitute for the `research` provider.

In `drain`, return unassigned prototype, grilling, HITL, and ambiguous task
tickets in the ordered `wayfinderHumanFrontier`. Return an otherwise eligible
HITL ticket already assigned to the runner in the separate
`wayfinderClaimedHitl` attention collection. Never call an assigned ticket part
of the frontier, and never resume it without fresh per-ticket HITL approval.

Keep one durable Todo controller lease, but not one reusable provider
context. Only the controller may assign, comment, close, edit a map, create
issues, add Project items, or wire dependencies. The research subagent owns
only its throwaway research branch and artifact. Serialize tracker and Project
mutations and reconcile ambiguous outcomes before the next mutation.

## Reconcile A Resolution

After a successful provider outcome, enter the controller lane. Require either
`resolved` for a decision on the route or `out-of-scope` for a scope boundary.
Post and refetch the resolution answer or scope-disposition comment. Before any
terminal mutation, compute one exact reconciliation plan covering the correct
map section, fog changes, child creates/updates/closes, parent-child and
dependency edges, Project additions, child terminal state, and possible map
completion. Post and refetch a durable runner-authored marker comment with this
machine-readable payload:

```json
{
  "markerVersion": 1,
  "disposition": "resolved",
  "mapNumber": 7,
  "projectItemId": "PVTI_child",
  "outcomePermalink": "https://github.com/owner/repository/issues/52#issuecomment-1",
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

Before mutating an existing issue, refetch its current Project column. Require Todo or a later configured column for each map or child being
updated or closed, including additional out-of-scope children. If any target
is in Backlog, missing, or unknown, preserve the recorded reconciliation and
report the exact human promotion needed; never promote or mutate that target.
An already-closed Done target satisfies only its recorded completed step.

Treat an authorized new child's initial body, dependency links, and Backlog
placement as one recorded creation operation under the eligible parent. Verify
exact creation ownership before resuming an incomplete operation. Once initial
Backlog placement is verified, do not edit or dispatch that child; leave later
changes and promotion to humans.

Apply the recorded plan idempotently and in this order:

1. close the selected child when still open and verify closure;
2. refetch its exact Project item by the marker's node ID and apply the
   configured Done automation contract exactly as for a merged issue: wait for
   and verify configured Status/archive automation, or set and verify only
   Status Done when Status automation is absent; never archive or remove it
   manually;
3. for `resolved`, append exactly one `[child title](URL) — one-line gist` to
   `Decisions so far`; for `out-of-scope`, append exactly one linked gist plus
   the reason to `Out of scope` and never add that child to `Decisions so far`;
4. fully reconcile the map: graduate newly specifiable fog, clear each
   graduated patch from `Not yet specified`, create all now-precise children
   before wiring native blocking edges, and update or delete invalidated tickets
   exactly as the provider directs and granted authority permits. When GitHub
   deletion is unavailable, close an invalidated ticket with the reason and do
   not index it as a decision or scope boundary. When another ticket is now out
   of scope, close it and add its linked gist and reason only to `Out of scope`.
   Reconcile every additionally closed child's configured Project Done/archive
   outcome by exact item ID;
5. add newly created children to the configured Project in Backlog as their
   initial placement and verify that value under the recorded creation operation.
   Refetch the complete live graph; and
6. only when fresh reads prove the destination's way is clear, no open child
   remains, `Not yet specified` is empty, and `Decisions so far` plus
   `Out of scope` are current, non-duplicative indexes for their respective
   outcomes, post the map completion summary, close the map, and reconcile its
   configured Project Done/archive outcome in the same way.

Never move a resolved Wayfinder child to `Ready to implement`.

When any completion condition does not hold, keep the map open. Unassign the
selected child only after every recorded mutation and every applicable terminal
Project outcome is verified. Leave the marker comment in place as inert audit
evidence. The marker makes a crash after canonical child closure resumable; it
does not justify reordering map reconciliation ahead of that closure.

## Resume Reconciliation

At startup, query runner-assigned marked Wayfinder children independently of
the ordinary open-Project inventory. First check the current child and parent
columns: Backlog never resumes, even with a valid marker. Refetch the marker,
its recorded Project item even when archived, the child, the direct map parent even when closed, and
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
In `drain`, an ordered human frontier or assigned HITL attention collection is
not a failure and must not pause independent lanes. Report the selected linked
ticket name, authority scope, provider result, map reconciliation, created
children awaiting human promotion, completion state, remaining human frontier,
and assigned HITL
attention.
