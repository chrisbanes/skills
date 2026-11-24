# Project controller handoff

Deliver only the implementation ticket exclusively claimed by the active
`run-project` controller. The controller owns scheduling, claims, tracker
state, merge, closure and checkout retirement throughout the handoff.

## Procedure

1. Verify the packet against live state on entry and resume. Match the
   selected [tracker and code host](provider-bindings.md), ticket, runner,
   claim and authority leases, source, effective plan and task graph, fixed
   base, checkout, branch and PR head. Carry forward the active revision
   evidence folder and controller preservation baseline, review coverage,
   implementation settings, capacity and consumed repair allowances. Resume
   the same owner, candidate and PR. Only the controller renews a lease. Return
   missing or conflicting evidence to the controller before writing.
2. For a controller fast-path revision, verify the [fast-path conditions](fast-path.md)
   before writes and on resume. Return a [replan packet](#return-a-replan-packet)
   if a condition fails. For a factual plan mismatch, use only the reserved
   diagnosis and repair allowance. Return scope changes and exhausted allowances
   to the controller.
3. If the controller approved a drain deferral, omit that edit. Include its path,
   intended content or regeneration steps and inputs in the PR’s `Deferred updates`
   section. Explain an empty contribution, flag any deferral that breaks the
   ticket, and verify the section against the diff even when the PR is pending.
4. Follow [Deliver an approved outcome](delivery-lifecycle.md) in the supplied
   checkout with the board’s [review contracts](../../run-project/references/review-contracts.md), qualification
   limits and closure intent. Return verification, repair rounds, repeated
   failures and capacity waits to the controller. In drain, use its remote
   snapshot and yield between actionable events.

## Return a replan packet

When repository evidence invalidates the approved plan or the required
adjustment exceeds its accepted contract, stop writes and return one packet to the controller containing:

- disposition: `autonomous-replan` or `human-required`;
- active plan permalink and payload digest;
- exact evidence and invalid assumption;
- current accepted stakeholder contract, upstream policy, and risk posture;
- recommended direction;
- verified base SHA, branch and PR heads, and retained dirty-work summary.

Classify the packet as:

- `autonomous-replan` when accepted behavior, scope, acceptance criteria,
  upstream policy, and risk posture remain unchanged and repository evidence
  supports a contract-realizing resolution, even when it affects a public
  interface, schema, persisted representation, seam, or testing contract;
- `human-required` only when the accepted stakeholder contract or upstream
  policy must change, new security, privacy, or permission policy must be
  established, an unsupported compatibility commitment or irreversible
  migration must be approved, or credible data-loss risk must be accepted.

For `autonomous-replan`, require the evidence supporting that classification.
For `human-required`, require the exact decision plus the authoritative issue,
specification, or ADR that must change. Return no packet when the ticket is
already implemented, superseded, contradicts an ADR, or remains ambiguous after
applying this rule.

## Finish gate

Finish launched reviews and helpers. Return the delivery outcome, source and
plan/amendment identities, branch, PR and head, applicable checks and reviews,
finding dispositions, phase timings and next action. Include the
[revision folder and written paths](evidence-and-review.md#isolate-plan-revision-evidence)
for the controller’s preservation check. Retain the checkout and evidence
for pending or blocked work.
