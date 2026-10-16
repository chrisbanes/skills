Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/admission.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below, choosing
from the supplied alternatives, then explain the evidence, ownership, stop and
resume conditions in prose. The field lines are checked deterministically;
the explanation remains subject to semantic review.

A supplied accepted task graph at integrated head B0 contains S1 and
E1, with E1 depending on S1. Owner schema has implemented S1's new catalog
field and decoder API on an unintegrated branch. Its branch tests pass, but
integration and affected checks have not happened. E1, owned by exporter,
changes only export/Writer.kt and tests/WriterTest.kt. Its focused test consumes
the new decoder API and field; it cannot compile against B0. No useful separate
preparation slice is declared. Paths are disjoint and there is free capacity.

In an all-work variant, an accepted plan explicitly requires baseline B1 before
ANY exporter implementation, even though a new proposed fixture could test
independently at B0. No plan change is authorized. Decide whether to create that
slice or narrow the accepted prerequisite during dispatch.

Fields:

- E1: hold | dispatch
- Evidence: integrated-S1-and-affected-checks | S1-branch-tests
- Base: current-integrated-head | unmerged-S1-branch
- Graph: preserve-S1-to-E1 | remove-edge
- All-work-variant: hold-for-authorized-plan-change | invent-preparation
- Qualification: pending-integrated-head | complete
