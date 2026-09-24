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
   Confirm published modules apply `com.vanniktech.maven.publish` directly or
   via a convention plugin; declaration alone is insufficient. If absent
   or unverified, report it and stop before release mutations; do not install
   or migrate publishing plugins.
   Distinguish readiness review, preparation and explicit release authorization;
   select the matching finish path before proceeding.
   For recovery or recovery review, select and read the
   [recovery answer form](references/recovery-output.md) before analysis. For
   changelog-related review, also read [the changelog procedure](references/changelog.md).
   For preparation or changelog-only work, read the
   [preparation answer form](references/preparation-output.md) alone in a
   standalone command before analysis. Check that the returned output contains
   the complete form, from its heading through its final sentence; if not,
   stop and recover that read before proceeding.
   Keep reviews read-only, including credentials. Follow the existing local or
   CI publishing mechanism; do not migrate it. Read the
   [helper contract](references/helper.md) before configuring the bundled script.
   Stop before mutation on unsupported layouts or ambiguous destinations.
2. Before preparation, read [the changelog procedure](references/changelog.md)
   completely; resolve baseline, version and coverage ambiguity. Do not guess
   or create a changelog.
3. Identify repository release checks, including tests and Metalava API
   generation and compatibility checks where configured. Confirm that API files
   are current before snapshotting; the helper copies them without running
   Metalava. Do not treat other API dump formats as Metalava snapshots.
   Require passing evidence for the release code; a green
   parent commit is insufficient after relevant changes. For Gradle execution,
   use [gradle-run](../gradle-run/SKILL.md), with `--no-scan` unless a scan is
   explicitly authorized. Fix failed checks within authorized scope; otherwise
   stop with the failing gate and next action.
4. Configure and preflight the helper with explicit versions, paths, heading
   style, API snapshot applicability, branch, remote, tag and command arguments.
   Keep configuration and evidence outside tracked release files. Check the
   index, snapshot collisions and local/remote destinations before writes. Load
   `~/.env` for local publication as data, never by shell sourcing or printing it.
   Preserve explicit process environment values. Missing required credentials
   block local publication; do not request or log their values. For tag-triggered
   CI, use existing Git authentication and CI-managed publishing secrets without
   loading or requiring local dotenv values.
5. Prepare the release: update the version, finalize the changelog heading and
   applicable published-module API snapshots, run configured checks, and commit
   only release files. When finalizing a stable release entry, group that cycle's
   original prerelease entries beneath its summary in a `<details>` block with
   `<summary>Prerelease history</summary>`. Preserve their headings, anchors,
   dates and text, with blank lines around the enclosed Markdown. Leave older
   stable releases outside the block. If the renderer lacks collapsible HTML,
   retain expanded entries. Before handing off, compare the actual stable
   summary against every surviving row in the coverage ledger; confirm each
   appears outside prerelease history and add any missing surviving change to
   the stable summary. Inspect the resulting commit. Bind validation to this
   state and invalidate it if relevant code changes. The helper must not
   publish during preparation.
6. Present the prepared release for explicit user approval before publication:
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
7. Once the prepared release is approved and all gates pass, publish from that
   commit via the repository's selected mechanism. Local publication and
   tag-triggered CI are alternatives; do not run both. Do not publish artifacts,
   push a release tag or trigger publishing CI before approval.
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

## Finish paths

- **Preparation, including changelog-only:** Fill the selected preparation
  answer form. Show actual reviewable notes or diff, remaining checks, and the
  explicit later publication-approval gate; do not request approval now.
- **Recovery/recovery review:** Fill the selected recovery answer form; check
  every applicable disposition before replying.
- **Completed release:** Report release version, commit/tag, validation,
  artifact readback, next development commit, and conditional GitHub Release
  URL. Claim completion only when every applicable check passes.

For a readiness review or blocker, state that narrower outcome and remaining
gate. Do not expose credential contents or raw sensitive command output.
