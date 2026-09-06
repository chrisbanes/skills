---
name: release-kotlin-library
description: Use when preparing, publishing, or checking readiness for a new Kotlin library version in a repository using gradle-maven-publish-plugin, including release changelog reconciliation, API snapshots, and publication verification.
---

# Release Kotlin library

## Core principle

Publish the prepared, validated release commit and call the release complete
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
   only release files. Inspect the resulting commit. Bind validation evidence to
   this state and invalidate it if relevant code changes. The helper must not
   publish during preparation.
7. When release is authorized and all gates pass, publish from that commit via
   the repository's selected mechanism. Local publication and tag-triggered CI
   are alternatives; do not run both. An explicit release request needs no
   redundant final approval. Preparation-only requests stop at prepared state.
8. Verify all expected artifact coordinates and versions at the configured
   destination, along with CI completion when applicable. Verify the remote tag
   resolves to the prepared commit. A successful command or tag alone is not
   artifact evidence. Only then advance, commit, push and verify the agreed
   next development version. Create and read back a GitHub Release only when
   repository conventions call for it, using the finalized release notes.
9. On partial or uncertain success, stop dependent mutations and report verified,
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
