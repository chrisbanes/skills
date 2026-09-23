# Preparation answer form

For preparation or changelog-only work, use three separate parts in ordinary
prose or the existing `summary` and `evidence` fields. Give verified values or
`pending`; never invent release state or claim publication. Keep this a
preparation handoff, not a request for publication approval now.

1. **Prepared work and reviewable notes:** State the completed scope and show
   the actual release notes or a directly reviewable diff in the answer. A path,
   a claim that notes are ready, or a packet inventory alone is insufficient.
2. **Remaining checks:** Fill both subfields independently:
   - **Candidate validation:** State which candidate-specific checks still need
     passing evidence. A green parent commit does not validate changed release
     code.
   - **Snapshot prerequisite and order:** State that Metalava API generation
     **and** compatibility must both pass **before** generated API snapshots
     are copied. If either check is pending, keep the snapshots uncopied. Merely
     naming the checks or an "order" heading without that relationship is
     incomplete.
3. **Later publication approval:** Explicitly say that publication requires
   the user's approval of the prepared, visible release details *later*, after
   the remaining checks. Enumerate the release version/tag, actual notes or
   diff, next development version, prepared commit, artifact coordinates and
   destination, publishing mechanism, and candidate-specific validation, with
   known values or `pending` for each. Do not replace the list with "full
   approval packet" or solicit publication approval during preparation.

Before sending, check that all three parts contain substance, not just their
labels. Do not advance version files, tag, publish, or claim a completed release
merely because a changelog-only preparation is reviewable.
