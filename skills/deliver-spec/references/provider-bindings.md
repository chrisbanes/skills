# Delivery bindings

## Core principle

Select tracker and code host independently; their bindings supply operations,
not authority. A code-host merge and a tracker closure are separate facts.

## Procedure

1. Resolve the source's tracker and repository's code host from the invocation,
   trusted configuration and fresh identity reads. Record both bindings and
   exact item/repository identities. A local source needs no tracker. For either
   GitHub role, read the applicable operations in the bundled
   [GitHub binding](github-binding.md#delivery-operations). A GitHub repository
   does not imply a GitHub tracker. For another provider, require its trusted
   operation contract; do not invent a binding or substitute GitHub commands.
2. Verify the capabilities needed by the next operation. The tracker supplies
   source/readiness, durable marker reads/writes/supersession and item linking,
   closure and readback. The code host supplies change-request open/update,
   exact head/base, checks/reviews/feedback, draft/readiness, merge policy,
   merge and readback. Missing capabilities block only dependent work; continue
   safe independent validation and preserve artifacts. Required external review
   remains separate from code-host review transport and local independent review.
3. Before planning, use tracker source/readiness and marker operations through
   `to-plan`. Preserve the tracker's human approval gate; GitHub requires
   `ready-for-agent` and its existing triage route. A different tracker must
   explicitly define its readiness gate. A controller handoff retains the
   controller's bindings, claim and authority; a ticket owner cannot replace them.
   Keep `ready-for-agent` throughout active GitHub work. Recheck it before
   material writes and recovery; removal invokes the binding's label-stop gate,
   quiescing writers and releasing capacity while preserving assignment and
   every artifact. Neither owner nor controller adds or restores the label.
4. After local qualification and independent review, use code-host open/update
   to create one draft change request or reuse the existing one, verifying exact
   repository, base and reviewed head. Link the exact tracker item through the
   bindings and refetch both sides where supported. Record the intended closure
   set and whether the change fully satisfies each item. For partial delivery or
   a local source without a tracker item, use non-closing source links only.
5. Use closing keywords only when the selected code-host/tracker pair explicitly
   supports native closure for this exact item and target base, the configured
   policy selects it, and the change fully satisfies the item. Otherwise use a
   non-closing link and record `close-after-merge`. Verify the host's complete
   effective closing-reference set after every create/body edit and before
   merge; it must equal the intended native closure set, or be empty for
   controller closure/partial delivery. Unknown or unintended references block
   acceptance and merge until corrected and read back. Never translate a tracker
   key into a host issue number.
6. Have `shepherd` coordinate check, review, feedback and change-request operations
   through the selected code-host binding, applying [PR review timing](pr-review-timing.md)
   to the provider's change request. Preserve exact-head evidence and merge
   authority; host readiness is distinct from delivery `ready`. Return unsupported
   operations precisely rather than falling back to a different host.
7. Immediately before authorized merge, refresh head/base, gates, authority,
   closure intent and linkage. Merge through the code-host binding and verify
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

## Finish gate

Report change-request merge and tracker closure separately, with exact identities,
head, merge evidence, closure policy and readbacks. Delivery `merged` requires
verified authorized merge; ticket completion/Done additionally requires verified
intended closure and controller reconciliation. A merged change with open or
unknown tracker state is not a completed ticket. Keep precise pending operations
and artifacts available for resume.
