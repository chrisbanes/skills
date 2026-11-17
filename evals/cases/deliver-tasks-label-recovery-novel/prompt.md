Assess supplied complete immutable scope in review mode. The only Status options
are Todo / In progress / Done. #111 retains a PR, branch, plan, assignment and
CI-parking record in In progress; ready-for-agent was removed in a previous run
and is still absent. Current merge approval and fresh green checks are present.
For absent-111 write resume, restore_label, retain_artifacts (booleans).
In a separate observation a human restores ready-for-agent on #111, parked=false,
and all ownership, plan, configuration, head, operation authority and reviews
revalidate with a free slot. For restored-111 write action (resume or replan).
#112 has needs-triage. Its approved triage recommendation is ready-for-agent;
for triage-112 write controller_adds_agent_label (boolean), next_actor (human or
controller). #113 still carries ready-for-agent and has explicit human direction
to abandon partial work; cleanup and PR closure are verified. For abandoned-113
write final_status (Todo or In progress), final_role (ready-for-human or
ready-for-agent). Explain write ordering and why no path restores agent authority.

Write exact JSON decisions to `.scratch/review-decisions.json`. Use skill references; make no provider calls or described mutations.
