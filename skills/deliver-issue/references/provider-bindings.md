# Delivery bindings

## Core principle

Select tracker and code host independently; their bindings supply operations,
not authority. A code-host merge and a tracker closure are separate facts.

## Local sources

For a spec without a tracker item, skip tracker lookup and issue creation.
From `deliver-issue` or `run-project`, return the route and stop. The route
starts with `to-plan` in conversation mode, then uses `implement-with-subagents`.
When already in `to-plan`, stay in conversation mode and hand off one validated
plan to `implement-with-subagents`. The caller opens one MR from the executor's
verified integration branch when authorized.

## Shared repository configuration

For tracker planning and delivery, resolve the [trusted delivery overrides](#trusted-delivery-overrides)
before comparing shared settings. For verified board handoffs, reuse the
controller's validated settings.

1. Read the closest trusted repository instructions on the verified base.
   Use `docs/agents/issue-tracker.md` for the tracker provider and repository,
   and `docs/agents/triage-labels.md` for the tracker labels mapped to
   `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`,
   and `wontfix`, when those instructions reference the exact files. Use only
   applicable files and their committed contents. A referenced file that is
   missing, invalid or has uncommitted edits blocks dependent work. A file
   without a trusted reference supplies no settings. These docs are optional
   for existing bindings and repositories without Matt Pocock's setup.
2. Read the declared tracker provider and explicit tracker repository from
   the tracker guide and the actual tracker label strings from the triage
   table's local-label column. Resolve only fields the current operation
   uses. Bind the labels to the resolved tracker repository or project.
   Leave code host, provider-specific IDs and credentials, board scope,
   Status, Priority, epic, claim and merge policy to the existing delivery
   binding. A shared guide's prose supplies no operation grant or alternate
   provider implementation.
3. Compare shared values with explicitly configured delivery values for the
   same tracker or role. Accept matching declarations as one setting and
   retain any delivery ID pins. Use a lone declaration when the other source
   omits it, and existing defaults when neither declares it. Resolve tracker
   repository names to the same provider-qualified identity. If a declared
   value is ambiguous, unsupported or conflicts, name the affected field
   and both sources and stop before dependent work. Never choose one source
   or fall back to defaults to bypass a conflict.
4. Verify the resolved tracker and role identities through the selected
   provider binding. Compare effective values and IDs on refresh and
   recovery as usual. Keep the existing delivery digest when its file and
   effective binding are unchanged. Include shared values used for delivery
   in the existing fields of the resolved snapshot or fingerprint, without
   hashing the shared Markdown or recording its path as a new identity input.
   A prose-only edit that leaves these values unchanged does not
   invalidate a claim. Use the existing binding drift and lease rules for
   any effective change.

Use the delivery binding's normal blocked result for affected operations.
Finish configuration validation only after the sources agree and live
identity checks pass. Board handoffs reuse the controller's validated
settings. Standalone tracker planning uses the selected issue and applicable
holds. It requires no board role mapping or agent-work label. Direct issue
delivery retains its scoped readiness rules.

## Trusted delivery overrides

1. On the verified base, inspect `docs/agents/deliver-tasks.md` and any
   override path explicitly referenced by the closest trusted repository
   instructions. If both exist and select different files, report a
   configuration conflict with both paths before dependent work. An existing
   override requires an exact trusted reference and committed instructions
   and contents. A missing referenced file, uncommitted edit or invalid
   configuration blocks dependent work. If no override exists or is
   referenced, use the selected provider's defaults.
2. For board bindings, treat `docs/agents/run-github-project.md` as a legacy
   file that requires migration. During execution, report conflicts or a
   required migration without editing configuration. Board setup follows the
   [legacy migration gate](../../run-project/references/github-binding.md#approval-gated-legacy-migration).
3. Read applicable fields in `Tracker`, `Triage` and `Work Roles` for tracker
   identity and role names or pins. Compare them with the shared guides above
   before applying defaults. Standalone planning resolves only source and
   hold fields. For delivery, also read `Code host`, `Repository` and
   `Merge Policy` under the selected provider's binding. Board controllers
   resolve board-specific fields through their own binding.

## Procedure

1. Resolve the source's tracker and repository's code host from the invocation,
   [shared repository configuration](#shared-repository-configuration),
   the resulting trusted overrides and fresh identity reads. Record both
   bindings and exact item/repository identities. For either GitHub role, read
   the applicable operations in the bundled
   [GitHub binding](github-delivery.md#delivery-operations). When GitHub is the
   code host, verify its [target branch](github-delivery.md#resolve-code-host-target).
   Read check policy when qualifying CI deferral and resolve the full
   [merge policy](github-delivery.md#resolve-code-host-policy) at the
   applicable merge preflight and recovery gates. For a Jira Cloud tracker
   use the bundled [Jira binding](jira-binding.md). For GitLab read the
   selected [tracker](gitlab-binding.md#tracker-operations) or
   [code-host](gitlab-binding.md#code-host-operations) operations, or both when
   selected. Verify the GitLab target through code-host operation 1.
   A repository on either
   host does not imply a tracker on it. When the tracker repository differs
   from the checkout origin, take it from the resolved tracker configuration;
   resolve a bare `#N` only against that tracker repository, never against the
   code host, and without it accept only canonical item URLs or
   repository-qualified references. For another provider, require
   its trusted operation contract; do not invent a binding or substitute
   GitHub commands.
2. Verify the capabilities needed by the next operation. The tracker supplies
   source/readiness, durable marker reads/writes/supersession and item linking,
   closure and readback. The code host supplies change-request open/update,
   exact head/base, checks/reviews/feedback, draft/readiness, merge policy,
   merge and readback. Missing capabilities block only dependent work; continue
   safe independent validation and preserve artifacts. Required external review
   remains separate from code-host review transport and local independent review.
3. Before planning, verify the invocation mode under the binding. A direct-issue
   controller uses the [issue lifecycle](issue-lifecycle.md) and the selected
   tracker readiness branch ([GitHub](github-delivery.md#direct-issue-planning-readiness)
   [Jira](jira-binding.md#scope-and-readiness), or
   [GitLab](gitlab-binding.md#scope-and-readiness)); a board handoff retains its
   controller's bindings, claim, role authority and grants. Ordinary standalone
   to-plan keeps its own readiness gate. Recheck the applicable operation grant
   and explicit holds/stops before material writes and recovery. Never add or
   restore readiness labels to obtain permission; preserve recorded human stops.
4. Before opening a change request, route an already satisfied outcome through
   [verified no-change closure](#verified-no-change-closure).
   For changes, after local qualification and independent review, use code-host open/update
   to create one draft change request or reuse the existing one, verifying exact
   repository, base and reviewed head. Link the exact tracker item through the
   bindings and refetch both sides where supported. Record the intended closure
   set and whether the change fully satisfies each item. For partial delivery or
   missing closure authority, use non-closing source links only.
5. Use closing keywords only when the selected code-host/tracker pair explicitly
   supports native closure for this exact item and target base, explicit closure
   authority covers every intended item, the configured
   policy selects it, and the change fully satisfies the item. For GitLab,
   check [exact project and default-base eligibility](gitlab-binding.md#link-and-close).
   Otherwise use a
   non-closing link and record `close-after-merge`. Verify the host's complete
   effective closing-reference set after every create/body edit and before
   merge; it must equal the intended native closure set, or be empty for
   controller closure/partial delivery. Unknown or unintended references block
   acceptance and merge until corrected and read back. Never translate a tracker
   key into a host issue number.
6. Have `shepherd` coordinate check, review, feedback and change-request operations
   through the selected code-host binding, applying [PR review timing](../../shepherd/references/pr-review-timing.md)
   to the provider's change request. Preserve exact-head evidence and merge
   authority; host readiness is distinct from delivery `ready`. Return unsupported
   operations precisely rather than falling back to a different host.
7. Immediately before authorized merge, refresh head/base, gates, authority,
   closure intent and linkage. Fingerprint the verified host merge policy and
   selected tracker's Done automation independently, including verified absence
   where applicable. A board records both fingerprints at startup. A standalone
   run records both at merge preflight. Compare retained fingerprints before
   merge, on relevant policy changes and before resuming parked work. Unknown required inputs or
   policy drift stop and preserve all work. Merge through the code-host binding and verify
   merged state, merged head/commit and target base before any controller close.
   For native closure, read back the exact tracker item's terminal state. For
   `close-after-merge`, the authorized standalone lead or owning controller
   revalidates the full item contract and remaining work, then closes through
   the tracker binding and verifies terminal state. Partial changes never close
   the item. A delegated ticket owner returns evidence to the controller instead
   of merging or closing. Merge authority alone grants no tracker-write authority.
8. Reconcile ambiguous writes from authoritative resulting state before retry;
   reuse a verified existing result and retry only proven absence under fresh
   preconditions. An unknown merge blocks closure. If merge succeeded but closure
   failed or is unknown, preserve the merged change and record closure as pending
   or blocked; resume reconciliation without merging again. Compare actual and
   intended closures and use the selected binding's authorized recovery route for
   unintended closure, preserving human changes; uncertainty blocks reconciliation.

## Verified no-change closure

Use this route before PR creation. Step 7 applies to the merge route.

1. Verify full acceptance against the current integrated code or other
   authoritative outcome evidence under the active plan. Record the
   verification and its applicability. An empty diff, partial delivery or stale
   evidence alone cannot qualify. Reconcile any retained change request and
   unknown merge before choosing this route. Keep outstanding delivery work open.
2. The owning controller or authorized standalone lead refreshes the exact
   tracker identity, ownership, stops, current closure grant, full acceptance
   evidence and complete required descendant and blocker states before writing.
   Require every required outcome to be satisfied. A delegated owner returns
   evidence to the controller. Missing or unknown prerequisites leave closure
   pending or blocked with the exact reason.
3. Use the selected tracker's verified close and terminal-readback operation
   ([GitHub](github-delivery.md#delivery-operations),
   [Jira](jira-binding.md#link-and-close) or [GitLab](gitlab-binding.md#link-and-close)).
   This route needs no change request, native closing reference, merge or merge
   grant. If the tracker lacks
   verified capability for this route, preserve evidence and report the gap.
   Reconcile ambiguous writes under step 8 before any retry. Report
   closure as verified only after authoritative readback of the intended
   terminal state and any required transition attribution.

## Finish gate

Report change-request merge and tracker closure separately, with exact identities,
head, merge evidence, closure policy and readbacks. Delivery `merged` requires
verified authorized merge; ticket completion/Done additionally requires verified
intended closure and controller reconciliation. A merged change with open or
unknown tracker state is not a completed ticket. For verified `no-change`,
report acceptance evidence and tracker closure separately, with host merge
inapplicable. Keep precise pending operations and artifacts available for resume.
