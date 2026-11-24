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
2. Follow the [implementation procedure](implementation-mode.md) in the
   supplied checkout. Keep the persistent ticket lead and repair owners.
   Verify independent-review capability from runtime metadata and fit any
   delegation within granted capacity. Use the [delivery record](evidence-and-review.md)
   for validation, routine repairs and verified integration amendments.
   For required [live qualification](qualification-failure.md), verify the
   finite pass conditions, offline result, live evidence, recovery checkpoint
   and remaining allowance before dependent work. The handoff authorizes
   in-scope implementation and repairs. For a factual mismatch in the plan,
   use only the controller-reserved diagnosis and repair allowance. Return
   ownership extensions, changed contracts and exhausted allowances to the controller.
3. Apply the [fast path](fast-path.md) only for a controller fast-path
   revision. Stop writes if a condition fails and return the
   [replan packet](#return-a-replan-packet). For an approved drain deferral,
   omit the deferred edit. Put its path and intended content or regeneration
   procedure and inputs in the PR body's `Deferred updates` section. Explain
   any empty contribution. At handoff verify the rule still applies, the diff
   omits the edit and the section matches this head. Return that evidence
   even for a pending PR. Report a deferral that would break this ticket.
4. For an empty final diff, verify full acceptance, the integrated base,
   clean head and applicable validation and review. Return `no-change` with
   that evidence before push, PR operations or shepherding. The controller
   reconciles tracker closure. Preserve the checkout if proof is missing.
   For a nonempty diff give one fresh independent read-only reviewer the
   [review contracts](review-contracts.md), source and delivery record.
   Honor explicitly invoked review providers. Reuse applicable coverage,
   return repairs to their owner and verify coverage of the final clean head
   before push. Report missing coverage as a blocker.
5. Push the reviewed head and reuse the verified PR, or create one draft if
   absent. Link the tracker item under the selected bindings and verify the
   complete closing-reference set against controller-authorized closure intent.
   Follow [PR review timing](pr-review-timing.md) for external review during
   CI. Use `shepherd` for actionable PR events and feedback. Quiesce the
   previous writer before any reassignment. Report verification, repair
   rounds, repeated failures and capacity waits to the controller, which
   applies its repair limits and CI parking policy. In drain, use its remote
   snapshot and yield between actionable events. It owns polling and resume.

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

Finish launched reviews and helpers. Return `ready` only after the final head
passes required checks and reviews with findings resolved. Use `pending` for
remote or controller-owned gates, `blocked` for a missing decision or capability,
and `no-change` for a verified satisfied outcome. Return the source, plan and
amendment identities, branch, PR and head, validation applicability, findings
and dispositions, review coverage, phase timings, and next operation or resume
condition. Include the [revision folder and written paths](evidence-and-review.md#isolate-plan-revision-evidence)
for the controller’s preservation check. Preserve unfinished work.
