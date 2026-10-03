# Live qualification and failure recovery

Use this procedure only when the approved source requires live qualification
that runs asynchronously or persists state in a real external store. Ordinary
offline checks and deterministic tests keep their existing validation path;
do not add a live qualification gate when the source requires none.

## Core principle

Treat each live qualification attempt as a bounded operation whose execution,
effects, remaining authority, and recovery state must stay known. A failed
assertion does not prove that an asynchronous action stopped or that a
persistent write did not happen.

## Procedure

1. Before dispatch, extract the finite pass conditions, accepted limitations,
   required evidence, and approved live allowances from the accepted source and
   plan. Record the required operation, external resource, credential/access,
   permissions, host capability, invocation-specific authority, and remaining
   attempt or budget allowance. If any prerequisite or allowance is missing or
   unknown, withhold only dependent dispatch and record its resume condition.
2. Before the first live qualification attempt, validate only the harness paths
   for capabilities present in the accepted source; reuse evidence while those
   paths and inputs remain unchanged, and renew it after an invalidating change.
   When qualification persists state, exercise the production store
   implementation in an isolated store instance and verify persisted outcomes
   across the applicable recovery path. When it runs asynchronously, use a fake
   runtime where that runtime path exists to exercise delayed responses,
   assertion failure while execution is active, and shutdown/recovery; detect
   missing required actions when action delivery is part of the contract,
   without creating a new exactly-once guarantee. Test archived conversation
   handling only when the conversation lifecycle exists, and check that recovery
   does not duplicate dispatch only when recovery can redispatch. Do not invent
   a store, conversation, archive state, or execution handle when those
   capabilities are absent. Do not replace a persistent production store with an
   in-memory fake. If a required applicable check is absent or fails, withhold
   live qualification and repair the harness under its existing owner and
   repair-progress gate.
3. Before every live attempt, verify conversation identity and archive state
   only when the conversation lifecycle provides them; verify an execution
   handle and current execution state for asynchronous work when the provider
   supplies them; and verify recovery data only for state the operation
   persists. In every case verify resource access, approved runtime/isolation,
   and remaining allowance. Offline fake-runtime evidence is not evidence of
   live behavior: use only the actual runtime, external effects, and isolation
   explicitly approved by the source. Do not inspect or mutate unrelated live
   data, or spend an attempt to discover whether access is available. Before
   dispatch, use the provider documentation or approved runbook to set a finite
   reconciliation deadline or maximum status-read count within the existing
   grant. If the source gives no bound, derive a routine, operation-specific
   bound from documented response behavior and the available grant; do not
   invent a universal timeout or request extra authority. Record the source,
   rationale, deadline/read budget, cadence, and attempt allowance before
   starting.
4. For asynchronous work, retain the provider-supported execution identity and
   observation mechanism; use an execution handle only when the provider
   supplies one. Observe it only within the recorded reconciliation bound.
   Record each read and its time. Stop when the execution is terminal or the
   deadline/read budget is exhausted. For synchronous work, reconcile only an
   explicitly unknown result using the recorded bound; do not poll for an
   execution handle. Preserve existing acceptance, grant, dependency, and
   repair-progress gates.
   Qualification evidence applies only to the operation and inputs it actually
   covers; it does not renew a grant or reset a consumed allowance.
5. If an assertion or operation fails, stop the affected and dependent
   dispatch. Reconcile within the recorded bound: check persistence only when
   the operation persists state; check delayed responses, active execution, or
   execution handles only for asynchronous work; and check archive state only
   when the conversation lifecycle supports it. On expiry, stop polling or
   follow-up reads; do not silently reset the bound, retry, start a conflicting
   action, or claim safe recovery while the prior outcome is unknown. Continue
   independent work only when it cannot touch the unresolved execution or
   state.
6. Before shutdown or handback, save a durable checkpoint containing only the
   identities and state that exist for this operation: conversation
   identity/archive state for a conversation lifecycle; provider-supported
   execution identity/observation mechanism and last known state for
   asynchronous work, with an execution handle only when supplied; persistence/
   recovery findings for persistent state; plus the exact failed condition,
   remaining allowance, reconciliation source, bound, reads used, expiry time,
   and next action. If
   an asynchronous execution may still be active after that bound, use only a
   documented bounded stop or cancel operation when supported, then reconcile
   its result and persisted effects under that operation's documented bound.
   Never force-terminate an unresolved execution. If no safe stop exists or its
   result remains unknown, retain the runtime, any provider-supported
   execution identity/observation mechanism or supplied handle, and checkpoint;
   preserve the ticket as blocked and hand it back without releasing the active
   execution or claiming safe recovery. Shut down only after applicable
   terminality, persistence, and recovery state are known and safe.
7. Keep ordinary implementation, test, fixture, and CI repairs with their
   existing owner and repair-progress gate; they do not require renewed
   stakeholder approval when they preserve the accepted contract. A repair or
   replan does not replenish live attempts or grants. For an approved-plan
   factual or seam mismatch, allow one focused diagnosis and at most two repair
   edit-and-validation cycles under the existing plan budget. Ordinary
   implementation, test, fixture, and CI repairs do not consume that
   plan-mismatch allowance. Consolidate a material change to requirements,
   accepted behavior, scope, acceptance, policy, risk, or approved live
   allowance into one decision request to the approver or Project controller.
   Stop the affected stage until that decision is recorded; do not implement
   the changed contract under the old approval. A contract-preserving
   implementation repair does not need renewed stakeholder approval. For a
   local conversation-plan repair, retain the existing approval only when the
   decision-complete source and its material choices are unchanged; revalidate
   and independently review the repaired plan. A revised GitHub plan must pass
   `to-plan`'s mode-specific approval, publication, and readback gates. Normal
   mode's renewed-approval requirement applies; verified Project `--auto` may
   satisfy that approval pause as `to-plan` defines, but does not waive
   publication, readback, or stakeholder approval for a material contract
   decision. A repair that restores an acceptance condition already stated by
   the source remains a repair, and a compatible test-environment fix does not
   itself require approval.

## Finish gate

Report qualification complete only when every finite pass condition has
evidence tied to the exact attempt and inputs, each applicable persistence,
asynchronous-execution, and conversation-lifecycle condition is safely
accounted for, and the remaining delivery gates pass. Otherwise preserve the
checkpoint and report the exact unresolved operation, consumed allowance, and
next action.

This is workflow guidance only. It does not mean a runtime automatically
enforces these checks or guarantees recovery.
