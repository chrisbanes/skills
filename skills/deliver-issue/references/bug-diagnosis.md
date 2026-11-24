# Bug diagnosis

Establish the cause and a way to verify the fix before choosing an
implementation route.

1. Confirm the expected behavior and the affected baseline, within the verified
   standalone scope, readiness, ownership and operation grants. Keep current
   verified plans on their existing delivery route. Skip new investigation
   when applicable evidence already establishes the cause and how to verify the
   fix. A bug label alone does not trigger diagnosis.
2. Keep diagnosis with the current owner. When `diagnosing-bugs` is available,
   use its reproduction and hypothesis-testing guidance through diagnosis. Prefer
   a focused check that reproduces the reported symptom on the affected baseline.
   When the skill is absent, use repository checks and targeted local probes
   without installing it. When a runnable reproducer is unavailable, assess
   traces or comparable evidence under this procedure even if the provider's
   reproduction phase stops. Accept that evidence only if it establishes the
   cause and supports a concrete check of the corrected behavior. A trace
   showing only the symptom or a failure to reproduce it is insufficient.
3. Record the baseline, symptom, evidence for the cause, and verification recipe
   in the existing delivery record. Redact sensitive output and keep temporary
   probes out of the delivery diff. Leave the fix and regression test to the
   implementation owner. Reuse the reproducer as a regression test where it
   exercises the actual failure. After the fix, check that the original
   scenario now meets the expected behavior or run the equivalent verification.
4. Re-evaluate every existing [fast-path condition](fast-path.md) using the
   diagnosis as evidence. Use the fast path when all conditions pass.
   Otherwise pass the evidence to `to-plan` under the existing approval gates.

## Finish gate

Advance to the chosen implementation route only with applicable evidence for
the cause and a concrete verification recipe. If the evidence falls short, hold
the affected fix, record what was tried and the exact artifact, access or result
needed to resume, and continue independent work. If acceptance is already
verified, follow [verified no-change closure](provider-bindings.md#verified-no-change-closure).
