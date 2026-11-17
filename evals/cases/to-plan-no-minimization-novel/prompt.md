Use only the supplied offline readback.json and applicable skills. No provider access,
GitHub commands, agents, implementation or model calls are authorized. The only
write is `.scratch/decision.md`; preserve state.md and the supplied records.

A trusted synthetic tracker binding supports exact marker reads and append-only
writes but cannot minimize or edit predecessors. The snapshot is the complete
readback after revision 2 was published under recorded approval by runner;
source/readiness and baseline checks were recorded before capture. Both records
remain visible. The retained draft has exactly revision 2's payload and baseline.
Assess the chain and the next action; do not publish anything.

Write these normalized fields, then explain binding operations, authority,
lineage, digest verification, optional presentation and evidence limits:

- Active: <stable permalink of the active full-plan record>
- Digest: <lowercase hexadecimal payload digest>
- Presentation: warning | blocked
- Next: no-op | republish | edit-predecessor
- Fork: blocked | accepted (if another revision 2 also superseded revision 1)
- Gap: blocked | accepted (if revision 2 were numbered 3)
- Foreign: blocked | accepted (if revision 2 had another author)
- Tampered: blocked | accepted (if its body changed after approval)
