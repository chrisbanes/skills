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
2. Before the first live qualification attempt, validate the harness offline;
   reuse that evidence while its harness and inputs remain unchanged, and renew
   it after an invalidating change. Use production store implementations in
   isolated store instances with a fake runtime. Inject a missing required
   delivery action and verify the harness detects it; do not turn that test
   into a new exactly-once delivery guarantee. Exercise delayed responses,
   archived conversations, assertion failure while execution is active, and
   shutdown/recovery with persisted outcomes. Verify recovery does not dispatch
   the same action again. Do not substitute an in-memory fake for the
   production store implementation. If these checks are absent or fail,
   withhold live qualification and repair the harness under its existing owner
   and repair-progress gate.
3. Before every live attempt, verify the retained conversation and execution
   identities, current execution state, recovery data, resource access, and
   remaining allowance. The offline fake runtime is not evidence of live
   behavior: use only the actual runtime, external effects, and isolation
   explicitly approved by the source. Do not inspect or mutate unrelated live
   data, or spend an attempt to discover whether access is available. Record
   the attempt identity and its exact allowance before starting it.
4. For asynchronous work, retain the returned execution handle and use bounded
   observation to establish its terminal state. Preserve existing acceptance,
   grant, dependency, and repair-progress gates. Qualification evidence applies
   only to the operation and inputs it actually covers; it does not renew a
   grant or reset a consumed allowance.
5. If an assertion or operation fails, stop the affected and dependent
   dispatch. Reconcile the outcome within the existing bounded procedure: check
   whether the action persisted, whether a delayed response or execution
   remains, whether the conversation was archived, and what shutdown or recovery
   state is known. Do not retry, start a conflicting action, or claim safe
   recovery while the prior outcome is unknown. Continue independent work only
   when it cannot touch the unresolved execution or state.
6. Before shutdown or handback, save a durable checkpoint containing the
   conversation and execution identities, last known execution state, exact
   failed condition, persistence/recovery findings, remaining allowance, and
   the next bounded reconciliation action. If an execution may still be active,
   use only a documented bounded stop or cancel operation when supported, then
   reconcile its result and persisted effects. Never force-terminate an
   unresolved execution. If no safe stop exists or its result remains unknown,
   retain the runtime, handle, and checkpoint, preserve the ticket as blocked,
   and hand it back without releasing the active execution or claiming safe
   recovery. Shut down only after terminality, persisted outcomes, and recovery
   state are known and safe.
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
   the changed contract under the old approval. A repair that restores an
   acceptance condition already stated by the source remains a repair, and a
   compatible test-environment fix does not itself require approval.

## Finish gate

Report qualification complete only when every finite pass condition and
required persistence/recovery observation has evidence tied to the exact
attempt and inputs, all executions are terminal or otherwise safely accounted
for, and the remaining delivery gates pass. Otherwise preserve the checkpoint
and report the exact unresolved operation, consumed allowance, and next action.

This is workflow guidance only. It does not mean a runtime automatically
enforces these checks or guarantees recovery.
