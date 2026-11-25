# Workflow status and recovery

1. Match the action to the request. For an explanation, give the applicable
   command and explain how to interpret its result. Review supplied snapshots
   directly. For an authorized live status check, run the following in its
   own tool call with the original workflow ID and global `--root` if supplied.

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py status --workflow <id>
   ```

2. Match `run` (sequence, wrapper/child PIDs, start time, working directory,
   command and question) to `result_sequence`. The latest stored `result`
   can belong to a previous run. Status returns immediately with up to 16 KiB
   of JSON and leaves logs unopened.

   | Status | Action |
   | --- | --- |
   | `idle` | The workflow is new. |
   | `running` | Poll status and wait for the owner. The run's held owner lock supplies activity evidence. A lock held by recovery does not. PIDs identify processes. |
   | `completed` | Check the matching `result.exit_status` for build or launch failures. |
   | `interrupted` | Report the recorded signal and bounded diagnostics. |
   | `uncertain` | Report the unknown outcome and investigate ownership under step 3. |
   | `abandoned` | Report an unknown outcome for that sequence and any `cleanup_error`. The ledger is settled even if cleanup failed. |
   | `finished` | The stored result has been removed. Retrieve needed results before finishing. An unknown ID fails closed. |

3. Treat legacy or incomplete ledgers, unproven ownership and ambiguous
   transitions as uncertain. Unrelated lock contention cannot establish
   activity. Use read-only evidence to identify the recorded wrapper, child
   and descendants. Absent PIDs alone cannot rule out live descendants.
   While any PID is live, possibly reused or unverifiable, or descendant
   ownership is unclear, leave the workflow unresolved. Do not terminate
   processes, rerun, replace, clean up or finish it.

4. Only after recovery is authorized and no live descendants remain, use
   the original workflow ID, active sequence and global `--root` if supplied:

   ```sh
   python3 <skill-dir>/scripts/gradle_run.py recover --workflow <id> \
     --sequence <n> --reason "<ownership evidence>" --no-live-descendants
   ```

   Recovery requires both locks and definitive absence of every recorded PID.
   If refused, report why and leave the workflow unresolved. On success,
   confirm `abandoned`, report the unknown outcome and any cleanup error,
   and reuse the workflow for later authorized validation. Normal log
   retention applies without opening the log.
