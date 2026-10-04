# Behavioral review and repair

## Core principle

Review production behavior and repair demonstrated failures as a coherent batch.
Test results support that review; passing tests or high test counts do not
establish correctness coverage.

## Procedure

1. Request full-candidate coverage for the first independent review, from the
   fixed verified base to the candidate, including identified uncommitted work.
   For follow-ups, supply the repair range and its interactions with the
   previously reviewed effective diff; require a result for every affected
   contract and a disposition for every finding. Widen to the full candidate
   when requirements changed, prior evidence is invalid, affected scope cannot
   be bounded or an explicit provider requires it. Retain applicable prior
   coverage, recording reviewed identities and covered scope; a repair-only
   comparison cannot establish coverage of interactions it excludes. Combined
   validation and independent review must cover the final clean head before
   publication; do not relabel an old result as a current-head run.
2. Alongside each review verdict, record a concise account of important
   production paths and boundary cases actually examined, the evidence used,
   and material uncertainty or unexamined interactions. Use the existing delivery
   record with its candidate, base and scope; do not create another receipt or
   demand an exhaustive path inventory. A verdict without this account leaves
   review coverage unestablished. Preserve explicitly invoked review providers'
   output and add the account to the delivery record when needed.
3. For a demonstrated boundary defect, trace other callers and transformations
   governed by the same rule. Inspect relevant neighboring cases and repair and
   test those that violate the accepted contract before publication. For example,
   a source-size failure warrants checking transformations that can expand the
   retained representation, not just the original input limit. Record inspected
   cases and evidence for leaving any unchanged. Reuse the smallest existing
   behavior only where semantics align; retain consumer-specific identity,
   privacy, persistence and recovery requirements. Do not expand a concrete
   failure into a universal checklist, unrelated audit or speculative framework.
4. Track completed external review rounds and their finding IDs against the
   previously accepted candidates in the same record. After two consecutive
   rounds find substantive defects in previously accepted code, classify the
   findings as missed behavior, repair regressions or related boundary failures
   using the accepted/repaired diffs and observed behavior. Resolve uncertain
   classification in the audit. Nits, repeated reports of an already-known
   finding, CI failures and pending reviews do not count as qualifying rounds;
   a completed round without substantive defects breaks the sequence.
5. On that trigger, hold the next publication and request one fresh independent
   read-only audit of the implicated behavior and its consumers, including the
   related cases from step 3 and repair interactions. Give it the approved
   requirements, fixed base/current candidate, prior findings and dispositions,
   and existing evidence without inherited implementation context. Require
   evidence-backed findings, the coverage account from step 2, and a `ship`,
   `fix-first` or `rethink` verdict. Return one consolidated repair batch to the
   original implementation owner (route each owned part to its original owner
   when several are implicated). Do not repeat this audit on the same evidence;
   record the rounds it consumed and assess later new rounds from there.
6. Preserve ownership, grants, capacity limits and consumed repair budgets.
   This audit waives neither independent final review nor required CI; reuse
   its coverage where it satisfies final-review contracts for the candidate.
   If required audit capability is unavailable, retain the candidate
   and report missing coverage before publication. Apply the selected workflow's
   existing material-change, exhausted-budget and repair-progress gates. After
   the owner's consolidated repair, renew affected checks and independent review
   of the changed behavior and interactions, reusing demonstrably valid evidence.

## Browser failure evidence

For a failed browser check involving asynchronous reads, record whether the
relevant read was pending, settled successfully, failed or remained unknown at
the assertion. Identify each failed state assertion separately, with expected
and observed state; a combined records/draft/focus/position timeout is not a
diagnosis. Use bounded waits tied to the intended settled condition and retain
the relevant request/refresh state and DOM or equivalent diagnostic snapshot
under normal privacy controls. Do not infer data loss from a pending read,
hide a settled failure behind a longer timeout, or claim a cause when evidence
is missing. Obtain that evidence before selecting a repair.

## Finish gate

Publish only when the required review coverage is established, implicated
neighboring failures are repaired or have evidence-backed dispositions, and
affected validation and independent review cover the actual final candidate.
Keep the selected workflow's clean-head, CI and mutation-authority gates intact.
