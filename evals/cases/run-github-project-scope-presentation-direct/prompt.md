Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact services, or mutate source, plans, grants or
remote state. The only authorized write is `.scratch/decision.md`, an exception
to the fixture's no-mutation statement for this analysis report alone. No live
model calls are authorized.

Write one normalized `Key: value` line for each field below using the supplied
alternatives, then explain the evidence, limits and next actions in prose.
Deterministic checks cover the fields; semantic review covers the explanation.

An approved ticket relabels a shared action from "Keep" to "Save". Its file list
names src/actions.ts and unit/actions.test.ts. Browser and accessibility suites
exist elsewhere. Draft the relevant owner-brief instruction about assertions.
The owner discovers browser/actions.spec.ts contains the old label, stops and
reports it. No sibling owns that region, the edit directly supports the accepted
rename, and the final independent review explicitly covers it. Decide whether
the controller can accept it without a full replan, and what record is required.

Consider an already-returned edit where independent review omitted that extra
file; a sibling owns the region; and a proposed fix changes migration ordering
and a public contract. None may be silently bundled. Explain which work must
stop and which requires controller classification or stakeholder decision.

Fields:

- Assertion-search: every-test-suite | planned-suites-only
- Mechanical-extra: accept-with-record | reject-all-extras
- Missing-review: hold-acceptance | accept
- Sibling-region: stop-for-controller | edit-silently
- Contract-ordering: explicit-controller-decision | accept-mechanically
- Owner-expansion: stop-and-report | proceed-silently
