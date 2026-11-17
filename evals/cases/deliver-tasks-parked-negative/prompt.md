Assess supplied complete immutable tracker-binding state for task delivery
in review mode. This hypothetical binding reports parked=true on four open items;
GitHub itself continues to report parked=false. All are unassigned and unblocked.
#91 is ready-for-agent with a current verified plan in Todo.
#92 has needs-triage in Todo. #93 has the human-work role in Todo.
#94 is an epic in Todo with all descendants closed. All other fields are valid.
For keys parked-91 through parked-94 record action (leave_untouched or process)
and preserve_dependencies (boolean). Determine whether any role label bypasses
the parked gate, and retain their blocker/descendant references in the complete
graph. These cases authorize no tracker changes, cleanup or new provider setup.

Return the requested exact JSON decision fields in your response.
Use skill references; make no provider calls or mutations.

This is a no-change assessment: write no files, including scratch artifacts.
