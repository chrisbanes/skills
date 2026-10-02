# Integration amendments

## Core principle

Retain settled work through a reviewed, append-only integration decision. An
amendment changes how the existing approved outcome is integrated, never its
requirements, architecture, policy or authority. It is not a readiness receipt.

## Classify before drafting

1. Refresh the source and decisions, native blockers, readiness, full-plan
   history, ownership, PR/head, old/new base and retained work. Use a clean
   planning worktree; do not modify the implementation checkout or require a
   WIP commit. Pin committed and dirty-work evidence separately. An unresolved
   dirty-work identity blocks consumption until the owner reconciles it.
2. Screen the actual delta and interactions, not just changed paths or an
   unchanged issue body. Proven non-overlapping drift keeps the existing
   screened-baseline path. An identical verified current contract is a no-op.
3. Use an amendment only when evidence proves unchanged requirements,
   acceptance, architecture, privacy/permission policy, qualification and
   authority, plus preservation of completed work. Identify concrete overlap,
   required integration, affected interfaces/risks and invalidated evidence.
   For example, reuse a newly canonical validator, carry forward newly required
   private-data exclusions, and refresh a control inventory only when these
   implement the same approved boundaries. A new privacy boundary is material.
4. Block unknown overlap or unsupported preservation pending evidence. Material
   requirement or architecture changes need a full reviewed replan; policy,
   permission, qualification or authority changes also need the existing
   stakeholder decision and authoritative source update where required. Do not
   turn an exhausted grant into an integration detail.
5. Require the retained delivery owner's verified integration request, exact
   source/plan/PR/head identities and current authority. For a Project claim,
   require the controller's authenticated request and existing claim/lease
   checks; a standalone request cannot take over that claim. Permit only this
   retained PR through the normal no-open-implementation-PR gate. Competing
   PRs, foreign requests or uncertain ownership block. This route does not
   require a full-replan report or a Todo/Ready round trip.

## Draft one bounded contract

Use `<!-- to-plan:integration-amendment:v1 -->` and the following fields. Use one
source manifest of canonical issue/spec/decision URLs and content digests;
reference requirements by stable identity instead of copying them. Include
material reasoning, not an implementation transcript.

```markdown
<!-- to-plan:integration-amendment:v1 -->

## Integration amendment

**Source:** <source manifest identities and digest>
**Full plan:** <permalink, revision and semantic payload digest>
**Sequence:** <positive contiguous number within this full-plan epoch>
**Previous effective contract:** <tip permalink and effective digest>
**Old base / new base:** <full SHAs>
**Retained candidate / expected PR head:** <full SHA / full SHA>
**Resulting candidate:** pending | <full SHA with integration provenance>
**Owner / worktree / branch / PR:** <verified retained identities>
**Publication authority:** <reviewed approval or existing autonomous grant>
**Independent review:** <record identity, exact draft digest and coverage>

### Integration decision

- Unchanged-contract rationale: <requirements, acceptance, architecture,
  privacy/permissions, qualification and authority evidence>
- Concrete overlap and affected behavior/interfaces/risks: <facts>
- Required integration: <bounded changes and any existing task IDs>
- Retained completed work: <commit/artifact identities and applicability>
- Invalidated evidence: <check/review IDs and why; do not silently discard>
- Renewed evidence required: <commands/seams, affected requirements and
  interactions, final-candidate coverage and failure/stop conditions>

**Payload digest:** <digest of the canonical semantic payload>
**Effective digest:** <composition digest defined below>
```


The v1 JSON keys are `source` (`url` of the selected issue and `digest` of its
source manifest), `plan` (`url`, `digest`), `sequence`, `previous` (`url`,
`digest` of the effective predecessor), `old_base`, `new_base`, `candidate`,
`expected_head`, `result_candidate` (SHA or JSON null), `owner`, `worktree`,
`branch`, `pr`, `classification` (`unchanged-scope`), `rationale`, `overlap`,
`integration`, `retained_work`, `invalidated_evidence` and `required_evidence`.
The last five are nonempty arrays of concrete statements or evidence references;
when no prior evidence is invalidated, record that fact and its reason explicitly.
Include the source manifest itself in the review packet with source URLs and
exact content digests; verify it against the pinned manifest digest. Review and
publication authority are separately authenticated metadata, never inferred from
`classification`. Consumers must reject unknown version semantics rather than
silently ignore them.

Do not predict a resulting SHA. A `pending` result authorizes the owner to
integrate from the pinned retained candidate into the new base; it cannot
support readiness. If integration already exists, pin its result and provenance.
Unexpected movement of base, source, branch/PR head or dirty work requires
reconciliation, not an automatic retry or silently refreshed hash.

## Verify identities and lineage

1. Enumerate all full-plan and amendment marker comments, including minimized
   history. Apply GitHub mode's existing v1/v2 plan-chain checks. Pin the current
   full-plan revision and semantic digest using its existing approved digest
   convention; do not retroactively rehash or rewrite a legacy plan.
2. Define the new amendment's canonical semantic payload as a JSON object with
   all fields in the template other than publication metadata, review record,
   and the two self-referential digests. Include source manifest, full-plan
   identity, sequence/predecessor, bases/candidates, owner/worktree/branch/PR,
   classification and integration/evidence decisions. Store the exact object
   in a fenced `json` block in the comment; prose must agree with it. Hash UTF-8
   JSON with lexically sorted keys, compact separators, unescaped Unicode,
   no trailing newline and no floats or duplicate keys. Arrays retain order.
   SHA-256 is lowercase hexadecimal. Preserve exact string contents; do not
   remove semantic text as presentation. The source manifest uses the same
   encoding with each source's exact UTF-8 content SHA-256 (no normalization).
3. Compute each effective digest as SHA-256 of canonical JSON
   `{"previous": <previous effective digest>, "amendment": <payload digest>}`.
   The initial tip is the full-plan permalink and its verified semantic digest.
   Require contiguous sequences from 1, exact predecessor tip/digest, one child
   per tip, and one current leaf. Each amendment pins the same source/full plan;
   its old base equals the preceding target base. Verify cumulative decisions
   remain compatible; a structurally valid chain cannot prove this judgment.
4. Verify every author's authenticated identity and permission, the exact body,
   metadata, payload/digests and independent review/approval against durable
   trusted observations. A hash supplied by an edited comment is not its own
   trust anchor. Retain approved/read-back body digests and expected identities
   outside the proposed payload. Foreign or subsequently edited comments,
   missing anchors, forks, gaps, stale predecessors/candidates or ambiguous
   reads block dependent work. Review applicability must cover these exact
   inputs and affected interactions; unchanged full-candidate coverage remains
   traceable rather than being relabelled as fresh evidence.
5. A full reviewed replan closes the prior amendment epoch. Its new plan revision
   must identify the preceding effective tip/digest and disposition of retained
   work/evidence. Verify both histories before starting the new epoch at sequence
   1. Never carry old amendments into a new full plan implicitly, append to a
   closed epoch, or pick whichever comment is newest. Existing plans with no
   amendments keep their existing publication and no-op behavior.

## Review, publish and reconcile

1. Independently review classification, integration, retained work and affected
   requirements/interactions under the existing review contract. Resolve
   findings and revalidate the exact draft before publication. Normal GitHub
   mode needs publication approval; `--auto` uses only already-verified
   authority and cannot extend it. Material changes return to the appropriate
   decision/replan route.
2. Immediately refresh readiness, native blockers and outcomes, source, complete
   marker history, ownership, permissions, old/new base, candidate/PR/dirty work
   and review/approval validity. Keep one publisher. A changed semantic input
   invalidates the draft approval/review; reconcile before proceeding.
3. Publish one new comment, never edit an active semantic payload. Refetch all
   markers; verify author, exact body, payload/effective digests, unique chain,
   base/candidate identities and timestamps. Keep supporting plans/amendments
   visible as components of the effective contract, not superseded payloads.
   Supersede the epoch only during full replanning under GitHub mode.
4. On timeout or ambiguous creation, preserve the exact draft and expected
   author/body/digests/sequence/predecessor. Reconcile complete fresh reads for
   that identity before retrying; reuse exactly one matching verified comment.
   Multiple matches, an unexpected child, partial reads or unresolved write
   outcome block dependent work. Retry only when absence is proved and the
   fresh preconditions still hold; do not use blanket retries.
5. An identical verified current amendment/effective contract is a no-op. Delete
   only its exact local draft after verified publication/no-op, preserving it
   on failures. Do not reset consumed repair budgets, qualification failures or
   external grants. Return `Published`, `No-op`, `Awaiting approval` or `Blocked`
   with exact contract and preserved artifact pointers as appropriate.

## Hand off to consumers

Return source manifest, full-plan identity, ordered amendment permalinks and
payload digests, effective tip/digest, verified publication/review/approval,
old/new base, retained candidate/PR head and owner/worktree/branch/PR. Include
retained work, evidence invalidation/renewal and pending result state. Both
consumers must revalidate current authority and identities; unsupported contract
versions or stale/ambiguous inputs block consumption rather than falling back
to the full plan alone.

- **`deliver-spec`:** Continue with the retained owner, work and PR from the exact
  verified starting candidate. Integrate and renew affected checks/review; retain
  unaffected evidence only with provenance and an explicit applicability reason.
  Record the resulting exact SHA/base, effective digest, PR/owner and combined
  evidence coverage in a durable result record. Verify old/new candidate linkage
  and full-candidate coverage at the final clean head. `pending` result/evidence
  blocks a ready claim, not authorized integration. A result record adds execution
  evidence; it cannot revise the immutable integration decision. New decisions
  require a new amendment or replan. Chain further amendments from the preceding
  verified result candidate, never an unexecuted guessed result.
- **`run-github-project`:** Verify that effective contract and the existing
  exclusive claim, current-column authority, native blockers/qualification,
  leases, base/head and retained owner/artifacts. Revalidate affected leases in
  place only within existing authority; do not renew external grants, claim
  different work or manufacture readiness. Keep implementation/evidence renewal
  with `deliver-spec`, without an unnecessary Todo/Ready lifecycle reset. The
  controller owns scheduling, capacity and lease mutation; this reference grants
  none of those powers to the planner.

## Finish gate and evidence limits

Hand off only one authenticated, reviewed, approved effective contract tied to
fresh identities. Preserve all artifacts and report the exact missing decision
or evidence on a blocker. Require new-head checks and combined independent review
coverage before delivery readiness; old SHA evidence is never current by default.

The offline evaluation validator checks normalized identity/digest/lineage
packets against evaluator-owned anchors. It is not a runtime publisher and cannot
prove live permissions, provider completeness, materiality, review quality or
consumer adoption. Keep those claims separate from deterministic test results.
