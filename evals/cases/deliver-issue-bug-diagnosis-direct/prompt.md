Use the supplied snapshots and applicable skill references. Read only the needed skill files. Return one JSON object keyed by snapshot. Do not execute delivery, run checks, contact providers, or edit files.

An explicit direct delivery request names a verified leaf issue. The CLI must preserve escaped spaces when loading a local config. Its current baseline drops them, but there is no current plan or evidence locating the cause. All scope, readiness, and ownership checks passed. An external skill named `diagnosing-bugs` is installed.

- `intake` is the initial snapshot above. Give `next` (`diagnose`, `plan`, or `fast-path`), `method` (`provider`, `local`, or `none`), and `fix_during_diagnosis` (boolean).
- `diagnosed` is a later snapshot for the same issue. A focused config-loading test reproduces the dropped spaces on the identified baseline. A targeted probe isolates an internal normalization error. One internal file and its test suffice, and every existing fast-path condition now passes. Give `next` (`plan` or `fast-path`), `retain_cause_and_verification` (boolean), and `regression_test_owner` (`diagnosis` or `implementation`).
