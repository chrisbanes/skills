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

You just published revision 2 of the autonomous implementation plan for
https://github.com/acme/widget/issues/31. Before publishing, you recorded the draft's payload digest
as `e3367715a0ad1c0c4bded77bd84faa38d190f61fcee5dfd363e6a378eb87a7e5`. The file `readback.json` holds the
refetched comment exactly as the GitHub REST API returned it. Its author and
revision chain are already verified. Recompute the payload digest from the
readback and decide whether publication is verified. You may run local
commands to hash the readback; do not contact GitHub.

Fields:

- Digest: <lowercase hexadecimal payload digest of the readback>
- Readback: verified | mismatch
