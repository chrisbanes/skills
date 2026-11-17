Use only supplied synthetic state and applicable skill references. Return the decision JSON in your response with exactly the named snapshots and fields below. Do not execute delivery, contact providers, start agents or change other files.

Independent states, complete reads except where noted: children-only: every child is CLOSED but root acceptance criterion “integrated export works” has not been verified. merge-only: final-head checks/reviews pass and the user authorizes merge but not issue closure; the PR body has Fixes #50. merged-open: verified merge, but #50 remains open. unknown-close: authorized close returned an error and readback is unavailable. done: all descendants and native blockers closed, root acceptance verified, merge and closure explicitly authorized, merge and root CLOSED readbacks verified. No additional gates exist.

Required output fields:

- children-only: root_done, next
- merge-only: native_closing_allowed, merge_before_corrected_readback, close
- merged-open: root_done, merge_again
- unknown-close: root_done, retry_before_reconciliation, preserve_evidence
- done: root_done

This is a no-change assessment: write no files, including scratch artifacts.

Put only the exact decision JSON object (no Markdown fences or prose) in the final structured response's `summary` string; put supporting reasoning in `evidence`.
