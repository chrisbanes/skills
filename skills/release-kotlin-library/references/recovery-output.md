# Recovery answer form

For recovery or recovery review, populate each disposition separately in the
final answer. Use ordinary prose or the existing `summary` and `evidence`
fields when a response schema is imposed; add no schema fields. Explain a
genuinely inapplicable item. Keep unknown evidence unknown, and never claim an
inspection or mutation that did not occur.

1. **Next action and authority:** State the next safe action and what remains
   unauthorized, including the publication/tag boundary.
2. **Artifact and tag state:** Classify each outcome as verified, failed, or
   unknown; identify remaining read-only reconciliation before any retry.
3. **Candidate and notes:** State release-commit validation, unresolved release
   note coverage, and the gate each creates. Parent-commit CI is not enough.
4. **Next development version:** Report a confirmed value with its evidence.
   If missing, mark it pending and ask the user to choose or confirm it; do not
   guess or silently increment. A choice now does not authorize editing version
   files, committing, tagging, or publishing: keep those actions blocked until
   recovery, validation, and approval gates permit them.
5. **Changelog baseline:** Give the applicable history range and why it applies.
   Keep the repository's incremental prerelease baseline; a final release uses
   the previous stable release for the completed cycle.
6. **Changelog presentation:** Separately state that active prerelease entries
   remain visible, while only a completed stable cycle may be grouped under
   its final summary. State whether the actual layout was verified. If no
   changelog was available in a read-only review, give the expected rule and
   mark the layout unverified. A baseline answer does not fill this disposition.
7. **Approval:** Fill both answer slots independently:
   - **7a — unchanged-exact rule:** State that prior explicit approval remains
     valid only for the unchanged exact prepared release. This rule must be
     stated even when the current candidate changed.
   - **7b — current candidate:** Classify this candidate as unchanged, changed,
     or unknown from the evidence. For changed code, notes, version, or
     publishing scope, require candidate-specific validation and fresh explicit
     approval before any remaining publication or tag action. Unknown evidence
     never authorizes mutation; do not blindly republish or push.

Before sending, check the substance of all seven dispositions, not just their
labels. Check 7a and 7b separately: 7a must state the unchanged-exact rule,
not merely this candidate's changed status; 7b must give an evidence-based
current-candidate disposition and the applicable changed-release rule. An empty
slot or a heading without its rule does not count.
For a missing next version, check for an actual user decision request, not only
the word `pending`; keep that request separate from blocked release mutations.
Keep review requests read-only and do not solicit publication approval when
the user asked only for review.
