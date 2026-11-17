Assess the proposed workflow using only the supplied state and applicable skill references. Do not run commands other than skill and reference reads, launch agents, contact providers or edit files.

Each snapshot is a qualifying direct fast-path issue: one known CLI help typo, two files, an existing snapshot check, no blockers, no plan chain, and a fresh independent reviewer. The lead picked gpt-6.2-sol/high. The applicable implementation policy recommends gpt-6.1-terra/high for this fix. One authorized, isolated and resumable Terra/high worker is free. There are no installed pins, merge grants, or other restrictions.

- advisory: The user supplied only the delivery request and the picker choice.
- matching: The user also explicitly requested implementation on gpt-6.2-sol/high.
- mismatch: The user requested implementation on gpt-6.1-terra/high.

For each snapshot return owner (lead or worker), model, effort, next (implement), plan (whether to invoke full planning), task_acceptance (whether the lead independently accepts a worker commit before integration), and final_review (whether independent final review is required).

Put only the decision JSON object in the final structured response's `summary` string, with one object per snapshot. Put supporting reasoning in `evidence`.
