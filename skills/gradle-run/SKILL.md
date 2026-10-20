---
name: gradle-run
description: Use when planning to execute Gradle through `gradle`, `./gradlew`, or a custom `gradlew*` wrapper script, including a quick compile or test check after an edit, or diagnosing a Gradle build, recovering a workflow's status, compact workflow ledger, repeated failure fingerprint, check, test, lint, warning, or failure even when no new Gradle run is appropriate.
---

# Gradle run

## Core principle

Treat complete Gradle output as a temporary, sensitive artifact. Every
agent-initiated Gradle command runs through the compact-output wrapper; never
stream, `tee`, paste, or reopen a full build log.

Every `create`, `run`, `status`, and `finish` invocation is the entire shell command for
that tool call. Prefixes, assignments, conditionals, pipes, command chains, and
follow-up inspection invalidate lifecycle evidence even when Gradle succeeds.

## Procedure

1. Classify the request. Reuse a current successful result when unchanged
   source and inputs already answer the question. A focused task that validates
   another change is incidental; build/check/warning/failure work is a
   Gradle-centered workflow.
2. Resolve this skill directory. If `python3` or `scripts/gradle_run.py` is
   unavailable (a failing standalone `create` shows this), stop and report that
   prerequisite; never run Gradle directly as a fallback. Invoke the project's
   designated entrypoint (normally `./gradlew`) as provided; do not read its
   source to second-guess it or substitute another launcher script.
3. Create one workflow before its first command and retain its opaque ID:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py create
   ```

   Run `create`, each `run`, and `finish` as standalone shell commands. Do not
   combine one with `ls`, `test`, variable setup, `git`, `rg`, `&&`, `;`, a
   pipe, or a newline containing another command. If `create` fails, retry a fresh
   standalone `create` before any `run`. Use the wrapper exclusively; it
   supplies `--console=plain` and `--no-scan` unless console behavior was
   selected or the user authorized `--scan`. Add `--warning-mode all` only for
   warning discovery or an explicit request. If `run` or `finish` reports
   `workflow is busy`, inspect status and wait for the owner; keep one execution
   owner and avoid a duplicate build.

   If a tool session disappears or the run's outcome is unknown, use the same
   workflow ID (and the same global `--root` if one was supplied):

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py status --workflow <id>
   ```

   Status is read-only and returns immediately with at most 16 KiB of JSON.
   `run` identifies the active or latest run by sequence, wrapper/child PIDs,
   start time, working directory, command and question. `result` is the latest
   stored bounded terminal summary, identified by `result_sequence`; while a
   new run is active it may describe the previous run. Status never opens logs.
   Poll status on `running`; a held lock specific to that run supplies activity
   evidence, while PIDs are identity only. Unrelated workflow lock contention
   leaves an abandoned run `uncertain`. `completed` includes failed builds and launch
   errors: check `result.exit_status`. `interrupted` requires a recorded signal.
   `uncertain` covers abandoned active records, missing locks, incomplete/legacy
   ledgers and transitions without sufficient evidence. Report that uncertainty;
   the next action is an ownership investigation, not completion inferred from
   a PID, a rerun (even conditional or later), cleanup, `finish`, or process
   termination. A new workflow is `idle`; after
   `finish` it is `finished` and its result has been removed. Unknown IDs fail
   closed. Finish only after retrieving the needed result.
4. For incidental validation, stay in the current agent and run the narrowest
   task that answers a non-empty verification question:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py run \
     --workflow <id> --scope targeted \
     --question "Does :module:test pass after this change?" -- \
     ./gradlew :module:test
   ```

   Do not substitute compilation for requested fixture tests, or skip a
   requested run because it may find no tests; run it and report that caveat.
   Read only the bounded JSON summary; report both the managed wrapper and
   nested Gradle task, the question, and its bounded answer.
5. For Gradle-centered work, keep diagnosis, repository edits, and wrapper
   execution with the current implementation owner by default. Delegate a
   bounded read-only investigation only when it offers useful independent
   analysis. Select and brief an optional helper using the shared
   [selection and handoff reference](references/subagent-selection.md).
   Keep one wrapper execution owner at a time; a helper reports evidence and
   recommendations to that owner. Continue directly when no helper is available.
6. Reuse actionable summaries, group warnings/failures by
   fingerprint, and return source/line evidence plus the narrowest next command.
   Run broad only for an aggregate question that targeted evidence cannot
   answer. On a repeated primary source/compiler fingerprint, stop rebuilding;
   inspect the cited source line and nearby declaration, import, or receiver
   context before revising the diagnosis. Verify each source change with the
   same wrapper and narrowest applicable task. In the final diagnosis, name the
   focused inspection as the next action; do not claim a source fix before it.
   A new question does not permit a blind repeat: rerunning an unchanged task
   under a relabeled question is still a repeat.
7. Treat the full log as raw sensitive material even though summaries and
   ledgers redact common credentials. Never expose it in model-visible context.
   On interruption, use the wrapper's recorded signal and bounded partial
   diagnostics; it owns process-group/process-tree cleanup and durable ledger
   updates. Only logs still represented by the bounded recent-run ledger remain.
   If a bounded result reports cache access denied before Gradle starts, report
   the exact path and recommend only an explicit writable-root entry for that
   existing cache directory, for the user to authorize. Stop there: do not
   apply it, plan a follow-up rerun, `finish`, or new workflow, disable the
   sandbox, or relocate caches.
8. Finish after the last requested validation (targeted or broad) passes, or
   report unresolved fingerprints and why validation cannot continue. In the
   final response, quote each non-empty `--question` and give its bounded
   answer; command history is not a substitute for reported evidence. Then run:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py finish --workflow <id>
   ```

   Report that finish removed only wrapper-owned logs. A finished known ID is
   idempotent; an unknown ID or active workflow fails closed and leaves files in
   place. This skill does not constrain unrelated review, implementation, or
   subagents.
