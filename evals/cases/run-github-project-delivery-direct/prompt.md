Review the next steps for `drain --auto-merge` using only
this supplied state. Do not run providers, agents, commands, or mutations.

The binding and exclusive claim are verified. Issue #42 is ready-for-agent and
In progress with a current approved `to-plan --auto` plan at digest `plan42`.
The plan has already passed independent review against these exact inputs.
Its stable tasks T1 and T2 have explicit acyclic dependencies, concrete
acceptance criteria, and approved behavior-test seams; T2 depends on T1, so
there is no useful parallel work. Resumable workers implemented the slices
sequentially through one reusable isolated checkout; the persistent ticket
agent accepted their commits and integrated them into its clean delivery
worktree based on verified main. Its integrated candidate head is `d1ce`, its diff is nonempty, and applicable checks are green.
A fresh independent reviewer has reported correctness and repository-standards
coverage at `d1ce`; the configured Project review contracts for reuse,
clarity, efficiency, and over-engineering are not yet covered. The binding uses
close-after-merge and squash. Explain how one reviewer completes missing
coverage, how the exact reviewed head becomes the draft PR head, who owns any
repair, and which owner may merge and close the issue. No external review-skill
or tracker setup is available or required. Do not treat this analysis request
as permission to execute the described run.

The caller permits the ticket coordinator and one active descendant at a time.
The independent reviewer occupies that descendant capacity now, so an
implementation worker cannot run concurrently with it. Explain whether this
limits completion of missing review coverage, and how to proceed if the review
finds a code repair requiring the retained original worker.
