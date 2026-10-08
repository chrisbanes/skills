Review four independently approved delivery requests, each considered both
manually and under a verified Project handoff with the same current source,
plan, reviews and test seams. Except for D, each integration checkout starts clean; editing
workers and final independent review capability are available. The Project
controller retains board, claim, issue and merge authority. Use supplied
evidence only.

A corrects one misspelt word in an existing Markdown paragraph. The exact edit
is fully understood and low risk, and no useful independent coordination or
implementation can overlap it; briefing a worker takes more work than the edit.

B makes an equally clear small Markdown change, but independent ready delivery
work is available for the coordinator to advance while a worker handles it.

C is a one-line code repair to an earlier task-owned implementation. The
original resumable worker is retained. Its PR and exact current candidate head
are known, and the coordinator could make the edit quickly.

D is the same trivial edit as A, but the current checkout contains unrelated
uncommitted changes, including an overlapping user edit. No verified clean task
checkout is available. Handoff cost and lack of useful overlap are unchanged.

For each, explain who edits, which workflow gates still apply, whether task
splitting or an extra worker checkout is justified, and how unaffected evidence
can be reused. Do not start agents, execute commands, contact providers, edit
files or treat this review as execution authority.
