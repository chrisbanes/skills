Review these independent GitHub Project scheduler observations from supplied
state only. Network and mutations are forbidden. For each, give the safe next
action, preserved state and the evidence required before capacity or a write is
allowed. No missing permission may be inferred.

1. One auxiliary agent is permitted. A speculative planner owns a verified
   draft and has used 12 of its 30 active planning minutes. A required CI failure
   arrives for a retained delivery owner. The planner acknowledges a safe yield;
   its descendants are stopped and resources released. Repair lasts 40 minutes,
   with context compaction in the middle. Explain repair dispatch, resume, the
   remaining planner deadline and attempt count. In a variant, publication was
   already sent but its result is unknown: explain what must happen first.
2. Runtime permits six auxiliaries, repository four, invocation five. The
   implementation-slot limit is four. A planner and one delivery agent are
   active; other owners are idle. Independent runnable slices exist. Explain
   the two capacity ceilings, spare capacity use and why the ranker must accept
   max-claims four without creating an agent-capacity grant.
3. Two approved plans each have an independently testable disjoint slice, then
   both edit the same canonical repository path in separate worktrees. There is
   no native dependency. Describe admission, the exact shared edit and later
   integration/merge boundary. Contrast a native blocked-by edge, an inseparable
   seam and uncertain independence; those variants have no safe partial admission.
4. Three unchanged CI observations concern an occupied slot. A complete
   snapshot remains uninvalidated and no selection follows. Later a merge,
   a new selection after invalidation, an incomplete read and a finish decision
   occur. Explain targeted reads, changed-record hydration and full refreshes,
   with recorded reasons and operation-specific authority checks.
5. Observed planning is 00:00–00:10, implementation 00:05–00:15, and repair
   capacity wait 00:06–00:10. Report phase/wait durations and total observed wall
   span; explain compaction-safe interval identity. A second plan/review cycle
   then repeats without a delivered increment: describe a bounded diagnosis,
   not a new retry budget or assumed time saving.
