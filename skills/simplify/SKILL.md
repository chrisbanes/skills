---
name: simplify
description: Use when the user asks to simplify changed code, clean up a specific implementation, or identify worthwhile simplifications.
---

# Simplify

Keep cleanups that preserve behavior and have a concrete benefit.

1. **Read the request.** Report by default, including for bare `$simplify`,
   requests for ideas or a focus alone. “Simplify this diff” or “clean this
   up” authorizes local edits. “Report only” always wins.
2. **Select the target.** Honor a supplied path, diff, commit range, PR or MR.
   Otherwise review staged, unstaged and non-ignored untracked changes together.
   On a clean worktree, diff from the merge base with the known target branch.
   Ask if the base is unclear. Stop if the selected diff is empty.
3. **Review in parallel.** [Brief four read-only reviewers](../subagent-delegation/references/subagent-selection.md#handoff-brief)
   on the same target. Have one look for existing helpers to reuse, one for
   simpler logic, one for wasted work, and one for places where adding or
   removing an abstraction would clarify the code.
   “Focus on X” sets a priority. “Only X” limits findings and edits to X.
   With fewer reviewers, cover all four concerns, solo if necessary, and
   briefly disclose the fallback.
4. **Reconcile findings.** Check proposals against callers and edge cases.
   Merge duplicates and drop speculative gains or shorter but less readable
   rewrites. If none qualify, finish in one sentence. For a report, give each
   finding's location, proposed edit and benefit.
5. **Apply and verify.** In edit mode, make the accepted changes yourself.
   Inspect the diff and run the smallest relevant checks. If a fix changes
   behavior, repair or undo your edit and recheck. Summarize edits, passing
   checks and any verification gaps.
