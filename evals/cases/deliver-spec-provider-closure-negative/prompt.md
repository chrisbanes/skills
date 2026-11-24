Use only the immutable snapshots below to assess the next provider
operations. Do not contact providers, run delivery, or change repository files.
Explain the next actions and closure boundaries in your response. Change no files.
Use the action/state values implied below; do not invent capabilities. All
snapshots have an approved full contract and current readiness unless stated.
Local checks and independent review passed for head H1; required remote checks
and reviews pass unless stated. The owning standalone lead has merge and tracker
closure authority unless stated. All reads are complete unless stated.

Trusted Jira supplies source/readiness, marker read/write/supersede, canonical
ticket linking, close and terminal readback, except where explicitly missing.
GitHub supplies PR open/update, checks/reviews/feedback, merge and complete
closing-reference readback. Jira closure is never native to GitHub.

- `partial`: GitHub tracker chrisbanes/app#42 and GitHub host. PR merged H1 into
  default main, but only one acceptance criterion is satisfied; remaining work
  is explicit. Non-closing partial policy, host closing set empty. No tracker close.
- `wrong-host-link`: Jira APP-42, GitHub PR fully qualified but not merged;
  body/manual link unexpectedly closes chrisbanes/app#42. Correct links and
  reverify the empty closing set before acceptance or merge; no Jira close.
- `missing-close`: Jira APP-42, GitHub merge confirmed, Jira binding has no close
  operation. Preserve merge evidence; block tracker completion on that capability.
- `delegated`: Jira APP-42, GitHub PR qualified but unmerged; controller owns
  merge and close. Return ready evidence to controller, perform neither operation.
- `local-no-tracker`: Approved local spec, no tracker item, GitHub PR qualified
  and unmerged; no merge authority. Return the appropriate route and preserve
  the existing PR without continuing delivery or inventing a tracker link.
