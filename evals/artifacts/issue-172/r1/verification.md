# Issue 172 revision 1 verification

- [Issue](https://github.com/chrisbanes/skills/issues/172) and [accepted brief](https://github.com/chrisbanes/skills/issues/172#issuecomment-6979598114).
- [Active plan](https://github.com/chrisbanes/skills/issues/172#issuecomment-6983340206) payload SHA-256 `8edb14a32af252154fc632ec8d245ed1342289dd0d77f46048140d8e46b10cc0`.
- Branch `cb/issue-172-compose-recipes` created at the controller-pinned base `bafa65e7b78a422b8467482f1bf59e9671e478de`. The delta from planned base `3d9da4774f441854a8ff4c513487301b057053ca` touched no Compose or Gradle paths. The change has no path overlap with #171's merge `a90a4af6af1b5332354a584a4ea2bd15e27dc93c`.

## Offline recipe tests

The local probe used the exact changed Kotlin snippets from the six recipe
files, with only the imports, surrounding fixtures and assertions needed to
compile and exercise them. Both map snippets were identical. The shared
Compose JVM fixture uses Gradle 9.7.0, Kotlin 2.4.10, Java 21 and Compose
Desktop 1.11.1. In the scratch copy, the tests used the fixture's existing
Compose JUnit 4 dependency and the v2 rule.

The sandbox denied the wrapper lock at
`/Users/chris/.gradle/wrapper/dists/gradle-9.7.0-bin/d4tj7w02tcgubx9zk9hbippn6/gradle-9.7.0-bin.zip.lck`.
Scoped offline commands with access to the existing cache ran successfully.
All commands used standalone `gradle_run.py` workflow
`4b669b34628a39e7d846423d52a31fbe`, which supplied `--no-scan`.

| Workflow question | Nested task and observed result |
| --- | --- |
| Does the enum transition compile? | `testClasses`, exit 0. The plain enum drives both documented child animations on one transition. |
| Does the hover test detect hover handling? | `test --tests '*Hover*'`, one pass. Replacing only hover collection with `val hovered = false` gave exit 1 and one failure. The XML identified `changesTextOnHover` and the failed `isDisplayed` assertion for the missing `Hovered` node. After restoring the collector, an uncached rerun executed the test and passed. |
| Are child constraints bounded by the parent? | `test --tests '*Constraints*'`, exit 0, two passed. With incoming height 0–100, requested heights 200 and 60 reached the child as fixed heights 100 and 60, respectively. The measured heights matched. |
| Do the latest handler and observable map changes reach the UI? | `test --tests '*Remembered*'`, exit 0, two passed. The same item ID invoked only the replacement handler. The rendered map reflected overlay precedence, in-place changes, clearing the overlay and an immutable parent replacement. |
| Do all Compose fixture tests pass offline? | `test --no-build-cache --rerun`, exit 0, five executed, zero failures or skips. |

The initial compilation reported a deprecation for the local v1 rule.
The probe moved to the v2 rule before the hover fault test and final suite.
The first restored hover run reused cached results, so the restored result
above comes from the subsequent `--no-build-cache --rerun` execution.
The workflow was finished after collecting the bounded results and test XML.
Finish removed only wrapper-owned logs.

## Reproduce from a scratch copy

Assemble the scratch fixture from the repository root on macOS with the
pinned offline Gradle inputs available.

```sh
probe_scratch=$(mktemp -d)
probe_overlay=evals/artifacts/issue-172/r1/probe-overlay
cp -R evals/fixtures/compose-jvm "$probe_scratch/fixture"
cp -R "$probe_overlay/src/." "$probe_scratch/fixture/src"
sed -i '' '/testImplementation(kotlin("test"))/d; s/useJUnitPlatform()/useJUnit()/' "$probe_scratch/fixture/build.gradle.kts"
```

From the assembled fixture, use the repository's managed Gradle workflow
with the repository-absolute wrapper script path. Pass `./gradlew --offline
test --no-build-cache --rerun` to its `run` command. To repeat the hover fault
test, filter to `'*Hover*'`, make the one-line change described above only
in the scratch copy, and restore the probe before repeating the filtered run.
The assembled build script and probe have Git blob identities
`f5ba0c5571eac35ca91878845a4a13e042405cd1` and
`360c085b9bcc1f1ecea843f30dec245bb72a11d3`.

## Deterministic checks and scope

- `npm test` exited 0. Node reported seven passes. The Python checks ran 358 tests with one skip and 427 evaluation tests with zero skips.
- `npm run lint`, `npm run references:check`, `npm run evals:validate` and `git diff --check` exited 0. Corpus validation covered 295 cases.
- All 42 Compose case digests and staged no-skill Git trees matched the exact base. The existing direct, novel and no-change cases continue to exercise the skill corpus. The isolated probe and scratch runner configuration stay outside the shared fixtures, corpus and harness.
- Revision evidence consists of this record and `probe-overlay/src/test/kotlin/example/RecipeTest.kt`. The controller-retained baseline SHA-256 is `16626af90270774001f6ea70952dbe34f5895fbd380b84929d8d052bc5b35cc0`. The tracked artifact inventory outside this revision matched it.
- Independent review and provider actions remain controller gates. The checks used offline execution and deterministic validation.
