Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact services, or mutate source, plans, grants or
remote state. The only authorized write is `.scratch/decision.md`, an exception
to the fixture's no-mutation statement for this analysis report alone. No live
model calls are authorized.

Write one normalized `Key: value` line for each field below using the supplied
alternatives, then explain the evidence, limits and next actions in prose.
Deterministic checks cover the fields; semantic review covers the explanation.

Two approved tickets edit src/commands.ts in isolated worktrees: older #41 edits
parseDate, younger #42 edits formatSize. Inspection proves separate symbols,
independent checks and no behavioral dependency. There is no native edge or
exclusive resource. Both have spare capacity. Determine admission and merge order.
After #41 merges, git merge-tree against the verified new base is clean; policy
allows an older base and all of #42's checked assumptions remain valid.

Compare four variants: the younger needs parseDate's new return contract; a
repository-declared whole-file lock exists; merge-tree reports a real conflict;
and a clean merge invalidates an assertion assumption. Also consider a policy
requiring an up-to-date branch. If #42 discovers it needs #41's region mid-work,
state its stop/checkpoint/controller handoff. A merge-tree execution error has
not established mergeability.

Fields:

- Disjoint: admit-both | serialize-whole-file
- Merge-order: older-first | younger-first
- Clean-base: retain-head-and-checks | rebase-and-rerun
- Behavior-dependency: hold-dependent-work | admit-both
- File-lock: honor-lock | ignore
- Conflict: update-and-renew | retain-evidence
- Invalidated-assumption: renew-affected-evidence | retain-evidence
- Strict-policy: update-and-renew | retain-head
- Discovered-region: stop-and-report | continue-silently
- Probe-error: unknown | clean
