---
name: changelog
description: Use when updating or reviewing Unreleased changelog entries, reconciling a changelog against Git history and issue or PR evidence, or preparing changelog notes for a specified release.
---

# Changelog

## Core principle

Keep consumer-visible notes complete and grounded in verified changes while
preserving curated wording and released history.

## Procedure

1. Establish the requested scope, repository conventions, changelog path and
   Git state. Choose **Unreleased maintenance** or **specified-release notes**;
   keep reviews read-only. If the user limits work to supplied state, run no
   discovery commands and mark unsupplied facts unknown. This skill applies
   across languages and publishing systems; it requires no Kotlin plugin,
   credentials, API snapshots or release approval.
   If no changelog exists and creation was not explicitly requested, report
   that it was skipped and finish. For explicitly requested creation, resolve
   its format and history scope first.
2. Establish the comparison range from repository tag conventions and ancestry,
   or supplied evidence. For Unreleased maintenance, compare against the latest
   applicable release, preserving the repository's incremental prerelease
   baseline. For specified-release notes, use the supplied target version;
   resolve a missing or ambiguous target before editing. For a specified
   prerelease, retain the repository's incremental baseline from the preceding
   applicable release. Keep an active prerelease cycle expanded. A final release uses
   the previous stable release as the baseline for the whole cycle, not only
   the latest RC delta; a first stable release covers history from the start.
   Resolve ambiguous tags rather than choosing the lexically highest one.
   Unreleased maintenance needs no next development version.
3. Compare existing notes with complete in-scope history, diffs and relevant
   issue/PR evidence. Preserve accurate curated wording; add missing
   consumer-visible changes, correct inaccuracies and omit internal-only
   changes. Attach each citation and credit only to an entry describing that
   change; give an uncovered change its own entry. Include relevant breaking
   changes and migration guidance. Resolve uncertain coverage or report the
   specific gap rather than inventing a claim or declaring completeness.
   For a final stable release, read [stable-release notes](references/stable-release.md)
   completely before editing and follow its coverage and history procedure.
4. Verify links and attribution. For each PR-supported change, link its number
   directly to the canonical pull URL, for example
   `[#123](https://github.com/OWNER/REPO/pull/123)`. Link matching issues where
   appropriate using explicit Markdown URLs; bare numbers are insufficient.
   For a verified non-maintainer PR author, include their verified name or
   username linked to their GitHub profile. Establish authorship from the PR
   and maintainer status from repository evidence. Supplied facts count as
   evidence; query a provider only when facts are missing and access is
   authorized. Report unverifiable URLs, authorship or maintainer status, and
   missing profile URLs for verified non-maintainers. Maintainers need no
   profile credit. Preserve accurate curated text apart from requested links
   and credit; never invent identities or classifications.
5. Apply only authorized changelog edits. Keep Unreleased maintenance under its
   existing heading. For specified-release notes, preserve repository heading,
   date and anchor conventions; finalize the heading only when requested.
   When called by `release-kotlin-library`, leave heading finalization to its
   release helper unless the caller explicitly requests changelog-only
   finalization. Leave Git mutations (including pulls and commits), version
   files, snapshots and publication to the caller. A reviewable changelog does
   not authorize those actions.
6. Inspect the actual diff against the reviewed changes, verify citation
   placement and preserved released history, and run `git diff --check` when
   command execution is permitted. Use repository documentation validation
   when required by its instructions or the changed formatting; report any
   unavailable validation. A heading check alone cannot establish semantic
   completeness.

## Finish gate

Show the actual notes or a directly reviewable diff, the comparison baseline and
reviewed scope, validation performed and unresolved evidence or coverage gaps.
For a read-only review, show findings or proposed notes without claiming edits.
For a missing changelog, report the skip without claiming reconciliation.
For a final release, verify every surviving coverage-ledger row appears in the
stable summary and the original prerelease history remains intact before
claiming the notes complete. Hand these results to the calling release workflow
when applicable; that caller owns remaining release gates and approval.
