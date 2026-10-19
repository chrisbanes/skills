Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/digest.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below,
using lowercase hexadecimal for digests and otherwise choosing from the
supplied alternatives,
then explain the evidence in prose. The field lines are checked
deterministically; the explanation remains subject to semantic review.

You are resuming a Project `drain` controller for
https://github.com/acme/widget/issues/31. Native minimization was unavailable, so revision 1 of the
plan was wrapped as superseded; `predecessor.json` holds its current REST API
readback, which now uses CRLF line endings. `replan-request.json` holds the
verified runner-authored autonomous-replan report naming that predecessor.
Both authors are the authenticated runner. Before normalizing the plan chain
for the ranker, decide whether the report's `previousPlanDigest` still matches
the wrapped predecessor. You may run local commands to hash the files; do not
contact GitHub.

Fields:

- Predecessor-digest: <lowercase hexadecimal payload digest of the predecessor>
- Replan-report: matches | mismatched
