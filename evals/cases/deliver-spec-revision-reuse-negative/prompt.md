Use only the supplied offline snapshot and applicable skill instructions.
Do not run delivery, contact providers, launch agents, or edit source or evidence.
The only authorised write is `.scratch/evidence.md`, an analysis artifact exempt
from the fixture's general no-mutation rule. No live model calls are authorised.
Write exactly one `Key: value` line per field, choosing from its alternatives,
then explain the actions and evidence in prose.

The verified active v2 plan is still revision 4 on resume. All evidence outside
`evidence/r4/` matches the controller-retained baseline. A passing r2 result at
`evidence/r2/compatibility.txt` has proven unchanged inputs and scope. Only a
new focused check is needed in r4. Should you copy or rewrite r2 into r4, rerun
all checks or allocate r5? Separately, an approved local conversation plan has
no numbered revision marker and already uses `local-results/`. Explain storage
and reuse without manufacturing a numbered revision or moving legacy files.

Fields:

- Folder: evidence/r4/ | evidence/r5/
- Reuse: cite-r2-original-path-and-identity | copy-and-relabel
- Earlier-files: unchanged | rewrite
- Reruns: affected-only | all
- Local-folder: local-results/ | local-results/r1/
- New-revision: none | invent-r5
