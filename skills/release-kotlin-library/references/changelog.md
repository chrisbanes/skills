# Changelog procedure

Resolve the previous applicable release from tag convention and ancestry. For a
final release, use the previous stable release as the baseline for the whole
cycle, not only the latest RC delta. Keep a repository's incremental baseline
for prereleases; for a first stable release, summarize history from the start.
Resolve ambiguity rather than choosing a lexically highest tag. Use supplied
release and next-development versions; propose and confirm every missing value
before mutation, and never silently increment a prerelease to a patch snapshot.

If `CHANGELOG.md` exists, compare `Unreleased` with complete baseline-to-HEAD
history, diffs, and relevant issue/PR evidence. Preserve curated wording; add
missing consumer-visible changes, correct inaccuracies, omit internal-only
changes, and resolve uncertain coverage before publication. A heading check
cannot prove semantic completeness; report reviewed scope and gaps.

For a final release, before editing make a temporary coverage ledger with one
row for **each** supplied or repository-discoverable change since the previous
stable release. Include changes after the latest prerelease even if the starting
changelog omits them. Record each row's source and whether it survives as final
consumer-visible behavior, was superseded, or is internal-only. For every
surviving row, identify where it appears in the final stable summary **outside**
prerelease history. After editing, compare the actual diff against every row;
do not report completion while a surviving row lacks stable-summary coverage.
Include relevant breaking changes and migration guidance. A preserved alpha,
beta, or RC note does not satisfy a stable-summary row. Deduplicate repeated
entries and describe final behavior without carrying forward superseded or
internal-only details.
Retain original prerelease notes in full and in their original order as the
changelog's source of truth; never replace them with release-page links.
Preserve formatting and prior stable entries outside the prerelease grouping.
If no changelog exists, skip this procedure without creating one.
Commit only authorized corrections before preparation so its clean-worktree gate
holds.
