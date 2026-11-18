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

- `native-open`: GitHub tracker chrisbanes/app#42 and GitHub code host. No PR
  exists; base main is default; closing-keyword policy and native closure are
  verified. Next open one draft PR and link it; no merge has occurred.
- `native-merged`: Same item/policy; authorized PR merge of H1 and exact native
  closing set read back, and the issue is confirmed closed. No more host action.
- `nondefault-merged`: GitHub item chrisbanes/app#43, GitHub PR merged into
  integration (not default), close-after-merge policy. Host closing set empty,
  full outcome in base verified, issue open. Next close via tracker and refetch;
  ticket completion still awaits that readback.
- `no-change-open`: GitHub issue chrisbanes/app#44 is open. Current acceptance
  checks verify every criterion on integrated main. The complete fresh
  descendant and blocker reads confirm all required outcomes are satisfied.
  The standalone lead has explicit tracker closure authority only, and the
  tracker supports close and readback. There is no PR or new merge.
- `no-change-closed`: Same outcome after authorized close and authoritative
  repository-qualified CLOSED readback. There is no further operation.
