Use the supplied snapshots and applicable skill references. Read only the needed skill files. Return one JSON object keyed by snapshot, with `next` (`diagnose`, `fast-path`, `reuse-plan`, `board-handoff`, `clarify`, or `no-change`) and `start_new_diagnosis` (boolean) in each. Do not execute delivery, contact providers, or edit files.

All the following issues carry a bug label. Unless otherwise stated, each is a verified, authorized direct delivery with no holds and no plan.

- `known-fix`: A current failing test and a one-variable probe already establish a reversed internal comparator as the cause and the test as verification. Every fast-path condition passes.
- `approved-plan`: A current verified plan already covers an intermittent failure, with evidence and an affected regression check.
- `board-owned`: The active board controller sent a verified single-ticket implementation handoff with a current approved plan. No material mismatch emerged.
- `unclear-outcome`: The observed response is clear, but the ticket has conflicting requirements about what the response should be.
- `already-fixed`: On the current integrated base an existing fix passes an acceptance check exercising the original failing path. The active approved plan's full acceptance and dependencies are verified, there is no remaining diff or change request, and no new closure authority.
