Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact services, or mutate source, plans, grants or
remote state. The only authorized write is `.scratch/decision.md`, an exception
to the fixture's no-mutation statement for this analysis report alone. No live
model calls are authorized.

Write one normalized `Key: value` line for each field below using the supplied
alternatives, then explain the evidence, limits and next actions in prose.
Deterministic checks cover the fields; semantic review covers the explanation.

PR #210 completes acme/widget#31 under closing-keyword policy on the default
branch. Its body also says "The follow-up will close #32". The complete provider
readback after creation contains #31 and #32. A body correction produces exactly
#31. Later a body edit reintroduces #32, while all checks are green. Explain the
readbacks and acceptance decisions after each write and immediately before merge.

In separate variants: a partial PR intentionally completes neither issue; a
fully implemented PR uses close-after-merge on a release branch; a partial PR
has merged but its ticket has remaining accepted work; and a readback
is paginated but only its first page arrived. Finally, a controller-run merge is
proven to have accidentally closed #32 with work pending. Its verified prior
Status was In progress, correction authority exists, and there were no human
changes. What recovery is required? If a human deliberately closed #32 afterward
or its prior Status is unknown, should recovery overwrite or guess?

Fields:

- Extra-reference: correct-and-recheck | accept-green-ci
- Before-merge: recheck-exact-set | reuse-old-read
- Partial-set: empty | ticket
- Partial-merge: retain-unfinished-claim | finish-ticket
- Release-set: empty | ticket
- Partial-read: block | accept
- Recovery: reopen-restore-comment-readback | leave-done
- Human-change: preserve-and-report | overwrite
