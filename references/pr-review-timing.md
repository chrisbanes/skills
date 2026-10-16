# PR review timing

Start applicable external review of a locally qualified candidate while CI runs; accept or
merge only with complete evidence applicable to the final head.

1. Complete affected local checks, independent integrated-candidate review and
   finding dispositions before publishing or requesting external review. Honor
   stricter explicit repository or invoked provider requirements, including
   local full-suite runs and any CI-before-review or CI-before-readiness rule.
   Reuse independent coverage only with verified scope and head applicability.
   When coverage is missing, including for a standalone PR without a delivery
   record, obtain one fresh independent read-only integrated-candidate review
   against source requirements, repository standards and the full diff; include
   the behavioral coverage account. Return findings to the repair owner. Hold
   publication if required review cannot run and report the missing capability.
2. Determine from trusted repository requirements and the caller which external
   PR reviews are required, optional or not applicable, separately from local
   independent review. Verify whether required CI starts on drafts or only after
   readiness regardless of external review applicability. If no provider is
   configured and none is required, record external review as not applicable
   and skip external trigger discovery; continue CI and local independent
   qualification. An explicitly required but unavailable
   provider is a blocker, not absence of a requirement.
   For applicable external review, inspect the provider's documentation,
   repository configuration or observed behavior for this repository. Prefer review on a
   draft only when that evidence demonstrates both draft support and a usable
   trigger while CI is pending. Record the evidence and trigger; a provider name
   or generic draft support alone proves neither. Do not change external
   settings to obtain support.
3. Publish or reuse the verified PR head. For applicable external review,
   request draft review through the verified route while CI runs. If draft review is unsupported or unverified,
   permit marking the PR ready earlier and use the existing configured review
   trigger, within the caller's non-merge PR authority and explicit repository
   requirements. Independently, when CI only starts after readiness, request
   applicable supported draft review first if available, then promptly mark
   ready to start CI on that same head, even when no external review applies.
   Wait for neither review nor CI completion before this transition unless
   an explicit repository rule requires it. Report unverified capabilities;
   do not claim readiness started review without provider readback. Verify the
   requested review targets the current head. If neither route can be established for required external
   review, report that blocker while independent CI work continues. Report an
   unavailable optional route without inventing an acceptance gate.
4. Track PR draft/readiness, external review and CI separately. Marking a PR
   ready to trigger review is not delivery status `ready`, acceptance or merge
   authority. Pending required CI or required reviews keep delivery `pending`;
   failed or unknown required gates prohibit acceptance and merge. Required checks (including a
   CI-supplied full suite), reviews and finding dispositions must all pass and
   apply to the final head before delivery `ready` or authorized merge. Optional
   review that is pending or unavailable adds no gate; actionable findings
   already received still require disposition under the selected workflow.
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
   under the selected workflow's authority and merge/queue rules. While required
   remote CI or reviews are pending, permit authorized host auto-merge only when
   local qualification, finding dispositions and authority apply to the current
   head, conflicts are absent, and the host demonstrably blocks merging on every
   pending required gate and protects every required gate across head changes:
   it must either suspend merging after any head change until all applicable
   gates are requalified, or enforce every required check, review and finding
   disposition's final-head applicability at merge time. CI enforcement alone
   is insufficient, even when CI runs on every head. Only pending remote gates
   may remain; failed or unknown required gates hold auto-merge enablement.
   A required approval need not arrive before enablement when the host enforces
   it: host-silent approval and CI completion can then finish the merge.
   Wake-time disabling cannot substitute for this host protection. Otherwise keep auto-merge disabled and
   report the missing enforcement.
   After a head change, requalify affected evidence before re-enabling auto-merge
   this controller disabled.

Finish with the exact head, review applicability and any trigger/readback,
required CI/review gates, finding dispositions and any unknown capability.
Readiness alone never closes a pending delivery.
