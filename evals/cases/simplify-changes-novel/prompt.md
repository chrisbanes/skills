What cleanup opportunities do you see? Focus on allocations. This host has no
review agents. Use this supplied snapshot of the checkout.

- Staged, `export.py:9` now returns `list(sorted(ids))`. Callers expect a fresh
  sorted list with duplicates intact.
- Unstaged, `send.py:18` guards the only call to `send(item)` with
  `if enabled == True:`. The parameter is always a built-in boolean.
- New untracked, non-ignored `preview.py:4` returns `list(sorted(ids))` as
  well. Preview callers also expect a fresh sorted list.
- The branch also contains an earlier, committed duplicate parse in
  `legacy.py`. That file has no local edits.
