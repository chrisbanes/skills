Assess this task scope with the GitHub binding in review mode on supplied complete
state. The only Status options are Todo, In progress and Done. #81 is unlabelled
Todo with no plan; #82 is unlabelled Todo with a valid plan; #83 is a runner-
assigned In progress item whose human removed ready-for-agent. It has a retained
branch, dirty worktree, PR and plan. No other work exists. Assess whether to
claim, plan, triage, close or clean up. Write keys unlabelled-81, unlabelled-82,
stopped-83, each with action (leave_untouched or process), and
preserve_dependencies (boolean). Explain writer shutdown, released capacity,
retained assignment and artifacts, and why later runs cannot restore the label
or resume until a human restores it. Make no provider calls or edits except
the requested artifact.

Write the requested exact JSON decision fields to `.scratch/review-decisions.json`.
Use skill references; do not execute the described operations.
