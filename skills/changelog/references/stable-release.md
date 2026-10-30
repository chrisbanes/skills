# Stable-release notes

1. Before editing, make a temporary coverage ledger with one row for **each**
   supplied or repository-discoverable change since the previous stable release.
   Include changes after the latest prerelease even if the starting changelog
   omits them. Record each row's source and whether it survives as final
   consumer-visible behavior, was superseded, or is internal-only. Keep the
   ledger outside tracked release files.
2. Draft the stable summary from every surviving row in final-behavior wording.
   Identify where each surviving row appears in the summary **outside**
   prerelease history. Deduplicate repeated entries, include relevant breaking
   changes and migration guidance, and omit superseded or internal-only details.
   A preserved alpha, beta or RC note does not satisfy stable-summary coverage.
3. Group that cycle's original prerelease entries beneath the stable summary in
   a `<details>` block with `<summary>Prerelease history</summary>` when the
   renderer supports collapsible HTML. Move the entries as one block without
   reordering them. Preserve their headings, anchors, dates and full text, with
   blank lines around the enclosed Markdown. Leave older stable releases
   outside the block. If collapsible HTML is unsupported, retain expanded
   entries. Never replace the changelog's original prerelease notes with
   release-page links.
4. Compare the actual edited stable summary against every ledger row and the
   grouped history against its original order and contents. Resolve missing
   surviving rows before reporting completeness; otherwise report the precise
   gap. Preserve repository formatting and prior stable entries.
