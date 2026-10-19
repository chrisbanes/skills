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

You are autonomously replanning https://github.com/acme/widget/issues/31. Your reviewed
draft is `.scratch/plan-draft.md`, written as revision 4. The active leaf is
revision 3; `active-leaf.json` holds its REST API readback, and its author and
chain are verified. The baseline is unchanged. Decide whether publication
needs a new revision. You may run local commands to hash the files; do not
contact GitHub, and leave the draft in place for this exercise.

Fields:

- Digest: <lowercase hexadecimal payload digest of the active leaf>
- Publication: no-op | new-revision
- Write: none | create-comment
