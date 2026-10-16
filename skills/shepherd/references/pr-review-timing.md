# PR review timing

Start external review of a locally qualified candidate while CI runs; accept or
merge only with complete evidence applicable to the final head.

1. Complete affected local checks, independent integrated-candidate review and
   finding dispositions before publishing or requesting external review. Honor
   stricter explicit repository or invoked provider requirements, including
   local full-suite runs and any CI-before-review or CI-before-readiness rule.
2. Inspect the configured review provider's current documentation, repository
   configuration or observed behavior for this repository. Prefer review on a
   draft only when that evidence demonstrates both draft support and a usable
   trigger while CI is pending. Record the evidence and trigger; a provider name
   or generic draft support alone proves neither. Do not change external
   settings to obtain support.
3. Publish or reuse the verified PR head. Request draft review through the
   verified route while CI runs. If draft review is unsupported or unverified,
   permit marking the PR ready earlier and use the existing configured review
   trigger, within the caller's non-merge PR authority and explicit repository
   requirements. Report unverified capabilities; do not claim that readiness
   started review without provider readback. Verify the requested review targets
   the current head. If neither route can be established, report that review
   blocker while independent CI work continues.
4. Track PR draft/readiness, external review and CI separately. Marking a PR
   ready to trigger review is not delivery status `ready`, acceptance or merge
   authority. Pending CI or reviews keep delivery `pending`; failed or unknown
   required gates prohibit acceptance and merge. Required checks (including a
   CI-supplied full suite), reviews and finding dispositions must all pass and
   apply to the final head before delivery `ready` or authorized merge.
5. After every head or base change, reassess checks, local and external reviews,
   approvals and finding dispositions against the new candidate. Invalidate
   affected evidence and renew checks and review of changed ranges and their
   interactions; broaden when impact is unknown or an explicit rule requires it.
   Retain only demonstrably unaffected compatible coverage with its original
   tested head and rationale. Require CI-supplied full-suite results on the new
   head and verify required external review coverage applies there; an old green
   check or approval alone cannot qualify changed code. Renew affected local
   checks and independent review before a repair push, then let external review
   and CI proceed concurrently again.
6. Refresh the exact PR head and every applicable gate immediately before merge,
   under the selected workflow's authority and merge/queue rules. While CI is
   pending, enable authorized host auto-merge only when all non-CI gates hold
   and the host demonstrably protects every required gate across head changes:
   it must either suspend merging after any head change until all applicable
   gates are requalified, or enforce every required check, review and finding
   disposition's final-head applicability at merge time. CI enforcement alone
   is insufficient, even when CI runs on every head. Wake-time disabling cannot
   substitute for this host protection. Otherwise keep auto-merge disabled and
   report the missing enforcement.
   After a head change, requalify affected evidence before re-enabling auto-merge
   this controller disabled.

Finish with the exact head, actual review trigger/readback, CI and review gates,
finding dispositions and any unknown capability. Readiness alone never closes a
pending delivery.
