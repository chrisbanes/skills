---
name: gradle-run
description: Use when planning to execute Gradle through `gradle`, `./gradlew`, or a custom `gradlew*` wrapper script, or diagnosing a Gradle build, check, test, lint, warning, or failure.
---

# Gradle run

## Core principle

Treat complete Gradle output as a temporary artifact, never conversation
context. Every agent-initiated Gradle command goes through the compact-output
wrapper; never stream, `tee`, paste, or reopen a complete build log.

## Procedure

1. Classify the request. A focused Gradle command that only validates another
   implementation change is incidental validation. A build, check,
   warning-cleanup, or failure-investigation loop is a Gradle-centered
   workflow.
2. Resolve this installed skill's directory and confirm `python3` and
   `<skill-dir>/scripts/gradle_run.py` are available. If either is
   unavailable, stop before running Gradle directly and report the failed
   prerequisite.
3. Create one wrapper workflow before the first command:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py create
   ```

   Retain the returned opaque workflow identifier. Use only this wrapper to
   run Gradle. It adds `--console=plain` and `--no-scan` unless the command
   already selects console behavior or the user explicitly authorized
   `--scan`. For warning discovery, include `--warning-mode all` in the Gradle
   command; otherwise include it only when the user asks for it.
4. For incidental validation, stay in the current agent and run the smallest
   owning task with a non-empty verification question:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py run \
     --workflow <id> --scope targeted \
     --question "Does :module:test pass after this change?" -- \
     ./gradlew :module:test
   ```

   Read only the bounded JSON summary and continue from its failed tasks,
   fingerprints, and excerpt. Do not inspect its log unless a user explicitly
   requests that artifact.
5. For a Gradle-centered workflow, create one fresh portable Solver diagnostic
   owner. Report its model and reasoning only if the runtime exposes them. Give
   it read-only repository access and ownership of wrapper runs and diagnosis;
   it must not edit source, tests, configuration, or generated project files,
   and it must not delegate Gradle ownership. The parent owns every repository
   edit. If a fresh persistent owner cannot be created, stop rather than make
   the parent run the workflow loop.
6. Have that owner reuse prior actionable summaries, group warnings and
   failures by fingerprint, and return exact file or line evidence plus the
   narrowest next command. Run an initial broad command only when existing
   targeted evidence cannot answer the recorded question. The owner stays
   available for the whole workflow and verifies each parent change with the
   same wrapper and the narrowest applicable task.
7. Record `broad` only for aggregate project checks. Give every broad run a
   distinct question that a narrower task cannot answer. The wrapper flags
   repeated commands and primary failure fingerprints; if the primary failure
   repeats, stop the run loop and revise the diagnosis before running another
   unchanged command. If the wrapper is interrupted, use its recorded signal
   and retained log; it stops the isolated Gradle process group before
   returning.
8. Finish after the requested broad validation passes, or report unresolved
   warning fingerprints and the reason validation cannot continue. Summarize
   the compact ledger, then delete only the wrapper-owned logs:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py finish --workflow <id>
   ```

   Finish retains a small marker so repeating the same finished identifier is
   idempotent while an unknown identifier fails closed. If finish cannot
   validate the managed identifier, leave all files in place and report the
   failure. This skill does not constrain unrelated review, exploration,
   implementation, or other subagents.

## RED/GREEN agent scenarios

1. Direct: “Run `check` and fix every warning.” RED runs repeated full
   builds with their logs in context. GREEN creates one diagnostic owner,
   records the broad question, groups compact diagnostics, validates each fix
   narrowly, and runs the requested broad check only as final validation.
2. Novel: a final broad check finds a downstream failure after targeted tasks
   pass. GREEN records the new question, targets the owning task, and only
   broad-reruns once that task passes.
3. Repetition: an unchanged failure fingerprint survives a claimed fix. GREEN
   stops rebuilding and asks for a revised diagnosis; it does not treat a new
   question string as permission for a blind repeat.
4. Fail closed: the wrapper, Python runtime, or persistent diagnostic owner is
   unavailable. GREEN runs no direct Gradle fallback and reports the missing
   prerequisite. A valid-looking but unknown finish identifier also fails; it
   is not treated as a previously completed workflow.
5. Counterexample: “After changing this Kotlin helper, run
   `:module:test`.” GREEN uses the wrapper but keeps this incidental focused
   validation with the current agent.
6. Boundary: while a Gradle workflow runs, a user starts an unrelated review
   subagent. GREEN permits it; this skill owns Gradle output handling and
   diagnostic delegation only.
7. Interruption: Ctrl-C arrives twice while Gradle has a signal-resistant
   worker process. GREEN tolerates the second signal, stops the isolated process
   group, retains the log, and records SIGINT in the compact ledger before
   returning. RED re-enters cleanup, leaves either process running, or loses the
   interruption record.
