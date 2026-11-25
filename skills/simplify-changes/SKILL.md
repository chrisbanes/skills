---
name: simplify-changes
description: Use when the user asks to simplify changed code, clean up a specific implementation, or identify worthwhile simplifications.
---

# Simplify changes

Keep cleanups that preserve behavior and have a concrete benefit. An edit is
complete when the lead has verified that behavior.

1. **Read the request.** Report by default, including for bare `$simplify-changes`,
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
   If reviewers are unavailable or fail to start, continue solo through
   reconciliation, authorized edits, and the focused verification step.
   Cover any missing review concerns yourself. Briefly state who reviewed the
   change and what you checked across the four concerns when using this fallback.
4. **Reconcile findings.** Check proposals against callers and edge cases.
   Merge duplicates and drop speculative gains or shorter but less readable
   rewrites. If none qualify, finish in one sentence. For a report, give each
   finding's location, proposed edit and benefit.
5. **Edit.** In edit mode, identify the focused test command for the affected
   behavior before making accepted edits yourself.
   Inspect the final diff and repair or undo any behavior change.
6. **Run the tests.** In edit mode, run the existing focused tests for the edited
   behavior yourself before replying, including after a solo review. Use the
   project's test command or identify the runner from the test file. If a test
   fails, repair or undo the edit and rerun it. Report the command and result,
   or the specific blocker.
