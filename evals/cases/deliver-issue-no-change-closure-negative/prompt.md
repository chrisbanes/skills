Use only the supplied snapshots and the applicable skill references. Write
nothing, run no commands and contact neither provider. Return one JSON object
keyed by scenario ID, with the fields `outcome` (`no-change` for verified
acceptance of the issue itself, or `unverified`),
`tracker_action` (`none`, `close_and_verify`, or `reconcile_closure`),
`host_action` (`none`, `open_draft`, or `merge` for this decision),
`retry` (boolean for an immediate repeat of an attempted write), and
`ticket_complete` (boolean).

The lead is assessing an issue on the selected GitHub tracker, with GitHub as
code host. There is no change request to open or merge. Unless a scenario
says otherwise, current verification proves full acceptance on the integrated
base, all descendants and blockers are freshly verified terminal, the lead has
explicit closure authority, and the tracker supports close and readback.

- `merge-grant-only`: The lead has merge authority and no closure authority.
- `stale-acceptance`: The only proof covers an old base and the current diff is
  empty. A material base change invalidated the proof.
- `partial-acceptance`: The evidence covers one of two required criteria.
- `open-descendant`: The issue itself meets its criteria, but a freshly read
  required descendant is open.
- `unknown-blocker`: The blocker query could not read its final page.
- `missing-capability`: The selected tracker can read the issue but has no
  verified close operation. The code host does not supply tracker capability.
- `delegated-owner`: The implementer has evidence, but the owning Project
  controller holds the tracker grant and must reconcile the outcome.
- `failed-close`: The authorized tracker close was rejected due to insufficient
  permissions and fresh readback shows the issue open.
- `unknown-close`: The close timed out; authoritative readback is unavailable.
  Determine the next action for the existing write.
- `unknown-readback`: The close returned success, but the fresh issue read
  cannot verify the repository identity. Assess ticket completion and the next
  action for that write.
