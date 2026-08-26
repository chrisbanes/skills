---
name: gradle-run
description: Use when planning to execute Gradle through `gradle`, `./gradlew`, or a custom `gradlew*` wrapper script, or diagnosing a Gradle build, compact workflow ledger, repeated failure fingerprint, check, test, lint, warning, or failure even when no new Gradle run is appropriate.
---

# Gradle run

## Core principle

Treat complete Gradle output as a temporary, sensitive artifact. Every
agent-initiated Gradle command runs through the compact-output wrapper; never
stream, `tee`, paste, or reopen a full build log.

## Procedure

1. Classify the request. Reuse a current successful result when unchanged
   source and inputs already answer the question. A focused task that validates
   another change is incidental; build/check/warning/failure work is a
   Gradle-centered workflow.
2. Resolve this skill directory and confirm `python3` plus
   `scripts/gradle_run.py`. If either is unavailable, stop and report that
   prerequisite; never run Gradle directly as a fallback.
3. Create one workflow before its first command and retain its opaque ID:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py create
   ```

   Run `create`, each `run`, and `finish` as standalone shell commands. Use the
   wrapper exclusively; it supplies `--console=plain` and `--no-scan` unless
   console behavior was selected or the user authorized `--scan`. Add
   `--warning-mode all` only for warning discovery or an explicit request. A
   `workflow is busy` result is an ownership violation: wait for the owner or
   correct ownership; do not start or finish concurrently.
4. For incidental validation, stay in the current agent and run the narrowest
   task that answers a non-empty verification question:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py run \
     --workflow <id> --scope targeted \
     --question "Does :module:test pass after this change?" -- \
     ./gradlew :module:test
   ```

   Do not substitute compilation for requested fixture tests. Read only the
   bounded JSON summary; report both the managed wrapper and nested Gradle task,
   the question, and its bounded answer.
5. For Gradle-centered work, create one fresh persistent Solver diagnostic
   owner with read-only repository access. It owns wrapper runs and diagnosis,
   may not edit or delegate Gradle ownership, and remains available for the
   workflow. Report its model and reasoning only when exposed. The parent owns
   repository edits. If that owner cannot exist, stop rather than running the
   loop in the parent.
6. Have the owner reuse actionable summaries, group warnings/failures by
   fingerprint, and return source/line evidence plus the narrowest next command.
   Run broad only for an aggregate question that targeted evidence cannot
   answer. On a repeated primary source/compiler fingerprint, stop rebuilding;
   inspect the cited source line and nearby declaration, import, or receiver
   context before revising the diagnosis. Verify each parent change with the
   same wrapper and narrowest applicable task. In the final diagnosis, name the
   focused inspection as the next action; do not claim a source fix before it.
   A new question does not permit a blind repeat.
7. Treat the full log as raw sensitive material even though summaries and
   ledgers redact common credentials. Never expose it in model-visible context.
   On interruption, use the wrapper's recorded signal and bounded partial
   diagnostics; it owns process-group/process-tree cleanup and durable ledger
   updates. Only logs still represented by the bounded recent-run ledger remain.
8. Finish after the last requested validation (targeted or broad) passes, or
   report unresolved fingerprints and why validation cannot continue. Summarize
   each question and bounded answer, then run:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py finish --workflow <id>
   ```

   Report that finish removed only wrapper-owned logs. A finished known ID is
   idempotent; an unknown ID or active workflow fails closed and leaves files in
   place. This skill does not constrain unrelated review, implementation, or
   subagents.
