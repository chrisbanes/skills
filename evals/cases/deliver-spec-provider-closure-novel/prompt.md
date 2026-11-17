Use only the immutable snapshots below to assess the next provider
operations. Do not contact providers, run delivery, or change repository files.
Write `.scratch/review-decisions.json`, keyed by snapshot ID, with exactly these
fields per snapshot: `tracker`, `code_host`, `change_action`, `closing_keywords`
(boolean), `expected_host_closures` (array of canonical issue identities),
`tracker_action`, `ticket_complete` (boolean), `delivery_state`.
Use the action/state values implied below; do not invent capabilities. All
snapshots have an approved full contract and current readiness unless stated.
Local checks and independent review passed for head H1; required remote checks
and reviews pass unless stated. The owning standalone lead has merge and tracker
closure authority unless stated. All reads are complete unless stated.

Trusted supplied bindings: Jira supplies source/readiness, durable marker
read/write/supersede, canonical ticket linking, close and terminal readback;
GitHub supplies PR open/update, checks/reviews/feedback, merge and closing-reference
readback. GitHub has no native closure for Jira. All tickets are Jira APP-42 at
https://jira.example/browse/APP-42, with no GitHub issue counterpart.

- `mixed-open`: No PR yet; base main/default. Open one GitHub draft, use the
  canonical Jira non-closing link and write/refetch its PR permalink on Jira.
- `mixed-update`: Existing PR needs its body updated after a local repair;
  reviewed H1 remains current. Update/reuse it, retain the Jira link. CI pending;
  no merge or tracker close yet.
- `mixed-merge-unknown`: Merge response timed out. Authoritative GitHub merged
  state is unknown. Reconcile merge before any tracker close.
- `mixed-merged-open`: Merge H1/commit/base confirmed, Jira remains open; full
  contract satisfied. Close via Jira and verify; not complete before readback.
- `mixed-closure-unknown`: GitHub merge confirmed, Jira close response timed out;
  Jira terminal readback unavailable. Reconcile closure, do not merge again.
- `mixed-complete`: GitHub merge and Jira terminal closure both verified.
