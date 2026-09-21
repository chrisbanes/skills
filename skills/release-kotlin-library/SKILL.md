---
name: release-kotlin-library
description: Use when preparing, publishing, or checking readiness for a new Kotlin library version in a repository using gradle-maven-publish-plugin, including release changelog reconciliation, API snapshots, and publication verification.
---

# Release Kotlin library

## Core principle

Publish the prepared, validated, user-approved release commit and call the release complete
only after verifying its artifacts and Git state.

## Prerequisite

This skill relies on `gradle-maven-publish-plugin` (`com.vanniktech.maven.publish`)
for library publication, whether run locally or through tag-triggered CI.
API snapshot support assumes Metalava-generated `api/api.txt` files; disable
snapshots when the repository does not maintain them.

## Procedure

1. Establish scope and inspect repository instructions, Git state, release
   history, version properties, publishing configuration and required checks.
   Confirm that published modules apply `com.vanniktech.maven.publish`, directly
   or through a convention plugin. A declaration without application is not
   sufficient. If absent or unverified, report the unmet prerequisite and stop
   before release mutations; do not install or migrate publishing plugins.
   Distinguish a readiness review, preparation request and explicit release
   authorization. Keep review requests read-only, including credentials. Follow
   the existing local or CI publishing mechanism; do not migrate it. Read the
   [helper contract](references/helper.md) before configuring the bundled script.
   Stop before mutation on unsupported layouts or ambiguous destinations.
2. Resolve the previous applicable release using tag conventions and ancestry.
   For a final release, use the previous stable release as the changelog
   baseline, covering the entire release cycle rather than only the latest RC
   delta (for example, 1.x to 2.0.0, not 2.0.0-rc00 to 2.0.0). For prereleases,
   retain the repository's incremental baseline convention. If this is the first
   stable release, summarize the release history from the project's beginning.
   An ambiguous baseline needs resolution, not a lexically highest tag guess.
   Use supplied release and next development versions. Propose and confirm each
   missing value before mutation; do not silently increment a prerelease to the
   next patch snapshot.
3. If `CHANGELOG.md` exists, compare its `Unreleased` section against the complete
   changes since the baseline: inspect history, diffs and relevant issue or PR
   evidence. Preserve curated wording, add missing consumer-visible changes,
   correct inaccurate entries, and omit internal-only changes with no consumer
   impact. Resolve uncertain coverage before publication. Report reviewed scope
   and unresolved gaps; a heading check cannot prove semantic completeness.
   For final releases, consolidate consumer-visible changes from alpha, beta
   and RC entries with Unreleased into a coherent summary of the full release,
   including breaking changes and migration guidance. Deduplicate repeated
   entries and describe the final behavior; omit superseded prerelease behavior
   from the summary only. Keep the changelog as the source of truth: retain
   original prerelease notes in full, never replace them with release-page links.
   Preserve existing formatting and prior release entries. If the file is
   absent, skip this step without creating it. Commit only authorized changelog
   corrections before invoking preparation, so its clean-worktree gate holds.
4. Identify repository release checks, including tests and Metalava API
   generation and compatibility checks where configured. Confirm that API files
   are current before snapshotting; the helper copies them without running
   Metalava. Do not treat other API dump formats as Metalava snapshots.
   Require passing evidence for the release code; a green
   parent commit is insufficient after relevant changes. For Gradle execution,
   use [gradle-run](../gradle-run/SKILL.md), with `--no-scan` unless a scan is
   explicitly authorized. Fix failed checks within authorized scope; otherwise
   stop with the failing gate and next action.
5. Configure and preflight the helper with explicit versions, paths, heading
   style, API snapshot applicability, branch, remote, tag and command arguments.
   Keep configuration and evidence outside tracked release files. Check the
   index, snapshot collisions and local/remote destinations before writes. Load
   `~/.env` for local publication as data, never by shell sourcing or printing it.
   Preserve explicit process environment values. Missing required credentials
   block local publication; do not request or log their values. For tag-triggered
   CI, use existing Git authentication and CI-managed publishing secrets without
   loading or requiring local dotenv values.
6. Prepare the release: update the version, finalize the changelog heading and
   applicable published-module API snapshots, run configured checks, and commit
   only release files. When finalizing a stable release entry, group that cycle's
   original prerelease entries beneath its summary in a `<details>` block with
   `<summary>Prerelease history</summary>`. Preserve their headings, anchors,
   dates and text, with blank lines around the enclosed Markdown. Leave older
   stable releases outside the block and active prerelease cycles expanded. If
   the changelog renderer does not support collapsible HTML, retain the entries
   expanded. Inspect the resulting commit. Bind validation evidence to
   this state and invalidate it if relevant code changes. The helper must not
   publish during preparation.
7. Present the prepared release for explicit user approval before publication:
   release version and tag, finalized changelog (or its absence), next development
   version, release commit, artifact coordinates and destination, publishing
   mechanism, and validation results. Provide the actual notes or a directly
   reviewable diff, not just a claim that they are ready. Explain that this
   approval gate is required by this skill and wait for the user's decision;
   a general request to release does not approve unseen release details.
   Reuse approval already given for this exact prepared release. If the code,
   versions, notes or publishing scope change, prepare and validate the revised
   release and obtain approval again. Preparation-only and readiness requests
   stop at their requested scope without soliciting publication approval.
8. Once the prepared release is approved and all gates pass, publish from that
   commit via the repository's selected mechanism. Local publication and
   tag-triggered CI are alternatives; do not run both. Do not publish artifacts,
   push a release tag or trigger publishing CI before approval.
9. Verify all expected artifact coordinates and versions at the configured
   destination, along with CI completion when applicable. Verify the remote tag
   resolves to the prepared commit. A successful command or tag alone is not
   artifact evidence. Only then advance, commit, push and verify the agreed
   next development version. Create and read back a GitHub Release only when
   repository conventions call for it, using the finalized release notes.
10. On partial or uncertain success, stop dependent mutations and report verified,
   failed and unknown stages without secrets. Inspect live artifact, workflow,
   tag and branch state before recovery; never blindly repeat publication,
   overwrite remote tags, delete published artifacts or claim rollback. Resume
   only a proven remaining action within existing authorization.

## Finish gate

Report the release version, release commit/tag, validation evidence, artifact
readback, next development commit and conditional GitHub Release URL. Claim
completion only when every applicable check passes. For review, preparation or
blocked work, state that narrower outcome and the remaining gate explicitly.
Do not expose credential contents or raw sensitive command output.
