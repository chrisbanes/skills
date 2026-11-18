# Issue 179 offline implementation

- [Source](https://github.com/chrisbanes/skills/issues/179) and [accepted brief](https://github.com/chrisbanes/skills/issues/179#issuecomment-6982713434)
- [Plan revision 1](https://github.com/chrisbanes/skills/issues/179#issuecomment-6983574267) with verified payload digest `227f01ad5db86c7777b3c0fb67b6eae1bbf67bd80d1b7ee24d7d4011ece290e2`
- Project item `PVTI_lAHOAAN4ns4BsKlazhJ3gqU` on board `PVT_kwHOAAN4ns4BsKla` with verified controller binding digest `cfc5e733c34d0d677ac2c387523b88a28340981c4c2825624fb1a686d8cc18e7`
- Branch `cb/issue-179-abandoned-gradle-recovery` from base `a90a4af6af1b5332354a584a4ea2bd15e27dc93c`. Implementation commit `c288741ddbac7aa7318e73b085de967356b061f1`. The base advance added five cases to the shared Kotlin and Gradle suite inventory. This change adds three to the advanced inventory. No Gradle wrapper, skill, or case path changed during the base advance.

## Offline observations

The recovery tests cover identity checks before process inspection, both locks held through the ledger write, byte-identical refusals, retained unopened logs, an unknown outcome associated with the active sequence and a subsequent managed fake Gradle run. The POSIX and Windows query boundaries run under mocks. Windows cases cover live, absent, denied, unexpected failure, exit query failure and a still-open exited process object. They check query-only handle rights, handle cleanup and zero calls to the signalling API.

The official [OpenProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess) and [GetExitCodeProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getexitcodeprocess) references describe the query APIs. Windows behavioral qualification remains pending on an authorized host with dedicated test processes and workflows. The unpublished patch mentioned in the issue was unavailable. No live model evaluation or provider mutation ran.

The evidence preservation check compares worktree paths, file modes and blob hashes outside this revision to the controller baseline. Independent review and publication remain controller-owned.

## Validation corrections

The first full run passed the wrapper suite and caught two suite-inventory
assertions still set to 29 cases. The paired correction updates the matrix
count and CLI call totals for 32 cases. The original failure is retained in
`preflight-full-test.log`. The focused wrapper run skipped the existing
procfs-dependent zombie test on macOS.
