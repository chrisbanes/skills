Use only supplied synthetic state and applicable skill references. Write `.scratch/review-decisions.json` with exactly the named snapshots and fields below. Do not execute delivery, contact providers, start agents or change other files.

The user directly requests root acme/repo#50. Its approved root plan includes a final integration change after children. The complete graph contains closed child #60 with open grandchild #61; #61 is blocked by external other/repo#9. Sibling #70 has no blockers and an approved plan. Nothing has a human hold or competing owner. A and B are independent PR-structure scenarios: A has an approved cohesive delivery plan covering two tightly coupled children in one PR; B has an approved plan for two independently shippable changes in dependency order. No external-blocker scope expansion has been granted.

Required output fields:

- scope: includes_root_work, includes_open_grandchild, ask_external_scope, implement_external, continue_issue, root_done
- A: preserve_plan, pr_count
- B: preserve_plan, pr_count
