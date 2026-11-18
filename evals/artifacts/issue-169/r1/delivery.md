# Issue #169 implementation evidence

- [Issue](https://github.com/chrisbanes/skills/issues/169)
- [Accepted brief](https://github.com/chrisbanes/skills/issues/169#issuecomment-6979594127)
- [Plan revision 1](https://github.com/chrisbanes/skills/issues/169#issuecomment-6982994176), verified payload digest `69f1655dff45c7dcf300a73fa7716393e9354f77e93129e7b30c0f67217bb034`
- Base `3d9da4774f441854a8ff4c513487301b057053ca`, branch `cb/issue-169-watcher-fingerprints`, binding digest `cfc5e733c34d0d677ac2c387523b88a28340981c4c2825624fb1a686d8cc18e7` from the controller
- Implementation diff SHA-256 `aa0bccfb59ee7d64e4a480cd1443e0009b05a889fc42c2ceb8dd344e712e5a87`. Reproduce with `git diff --binary 3d9da4774f441854a8ff4c513487301b057053ca HEAD -- references skills | shasum -a 256`.

## Offline validation

Node 24.22.1, npm 11.19.1 and Python 3.14.4.

| Command | Result |
| --- | --- |
| `npm ci --offline --no-audit --no-fund` | Installed 274 locked packages. npm reported the existing glob deprecation and optional fsevents install-script approval warning. |
| `python3 -m unittest skills/run-project/scripts/test_watch_project.py` | 56 passed after T1. The first T2 run stopped at import because the fake provider's f-string needed escaped braces. After correction, all 62 passed. |
| `python3 scripts/sync_references.py` | Updated mapped GitHub and scheduler copies. |
| `npm test` | Passed. Node 7 passed, repository Python 354 passed and 1 skipped, evaluation harness 427 passed. The Gradle process-table test requires Linux procfs and was skipped on macOS. |
| `npm run references:check` | Passed. |
| `npm run lint` | Passed. |
| `npm run evals:validate` | Validated 295 cases. |
| `git diff --check` | Passed. |

The fake-provider CLI covers PR A waking first, PR B changing before replacement, and the next wait reporting B. It also covers newly watched and removed PRs, a zero-PR refresh, invalid arguments, and preserved board and issue-comment drift.

The current-head check coverage keeps the aggregate pending while a check run or legacy status context finishes on a later page. It exercises reordered contexts, older-head-only changes, empty and null rollups, old baseline compatibility, ambiguous PR and head readback, malformed or incomplete pages, and an exhausted rate budget. No authoritative readiness or required-check decision moved into the watcher.

## Integration and evidence

Compared with the #163 branch at `e84e0f55e9b929c409ffd6c500d057da27b5d223`. The three scheduler copies were the only shared paths. Read-only three-way merges retained both the GitLab wait routing and the GitHub watcher procedure without conflict.

The supplied pre-change inventory matched the checkout's evidence tree before writes. The evidence path for this revision is `evals/artifacts/issue-169/r1/delivery.md`.

Independent review, integration against the controller's final #163 head, and publishing remain controller gates. Live provider runs and live model evaluations were outside this assignment.
