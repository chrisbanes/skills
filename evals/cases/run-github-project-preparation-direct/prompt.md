Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/admission.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below, choosing
from the supplied alternatives, then explain the evidence, ownership, stop and
resume conditions in prose. The field lines are checked deterministically;
the explanation remains subject to semantic review.

The younger fallback ticket has no native blockers or open descendants.
Both accepted plans were inspected at committed base B0. Optics owns O1 in
render/Glass.kt. Fallback task F1 explicitly permits owner fallback to add
fixtures/fallback.json and tests/test_fallback_fixture.py and run
`python3 -m unittest tests.test_fallback_fixture` from repository root at B0.
That test consumes only the existing fixture schema; it does not import the
renderer or require O1. F2 changes render/Glass.kt after O1 is integrated and
its affected checks pass. The plan requires the integrated optics baseline for
F2 and final qualification, and explicitly permits F1 before it. No shared
mutation belongs to F1. Both owners' records can be completed before dispatch.
An implementation slot and active-agent capacity are free. Device grant GPU1
remains held by optics; F1 needs no device or other exclusive resource. A file
grant for render/Glass.kt becoming free would not complete O1 integration.

Also assess a native variant: the same younger issue instead has an open native
blocked-by edge to optics. Do not change that edge.

Fields (choose one alternative after each colon):

- Preparation: admit-F1 | hold
- Owner: fallback | unassigned
- Paths: fixtures/fallback.json, tests/test_fallback_fixture.py | render/Glass.kt
- Check: python3 -m unittest tests.test_fallback_fixture | final-only
- Stop: before-F2-and-render/Glass.kt | after-shared-edit
- GPU1: retained-by-optics | released
- Qualification: pending-integrated-head | complete
- Native-variant: hold-whole-ticket | admit-F1
- Plan: preserve | silently-reorder
