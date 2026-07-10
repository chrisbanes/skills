# Skills

A set of skills for Kotlin, Jetpack Compose, and Android development.

## Install

With the [skills CLI](https://skills.sh):

```
npx skills add chrisbanes/skills
```

Or install as a Claude Code plugin:

```
/plugin marketplace add chrisbanes/skills
/plugin install chrisbanes-skills@chrisbanes-skills
```

Or install as a Codex plugin:

```
codex plugin marketplace add chrisbanes/skills --ref main
codex plugin add chrisbanes-skills@chrisbanes-skills
```

Or install as an OpenCode plugin:

```json
{
  "plugin": ["chrisbanes-skills@git+https://github.com/chrisbanes/skills.git"]
}
```

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md) for details.

## Skills

### Start here

- Working on Compose state or effects? Start with [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md), [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md), [`compose-state-holder-ui-split`](skills/compose-state-holder-ui-split/SKILL.md), or [`compose-side-effects`](skills/compose-side-effects/SKILL.md).
- Investigating recomposition, stability, or jank? Start with [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md).
- Reviewing Flow or coroutine architecture? Start with [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) or [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md).

### Routing

- [`using-chrisbanes-skills`](skills/using-chrisbanes-skills/SKILL.md) — route broad Kotlin, Android, and Jetpack Compose tasks to the focused skills.

### Jetpack Compose

#### State and side effects

- [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md) — author Compose local mutable state and read-only composable accessors correctly.
- [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md) — decide whether Compose UI element state belongs in local remember state, hoisted parameters, a plain state holder class, or a screen-level state holder.
- [`compose-state-holder-ui-split`](skills/compose-state-holder-ui-split/SKILL.md) — split Compose state-holder wiring from plain-state UI for previewable and testable screens.
- [`compose-side-effects`](skills/compose-side-effects/SKILL.md) — choose and key Compose effect APIs for event Flow collection, callbacks, cleanup, navigation, snackbar, analytics, and other side effects.

#### Performance

- [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md) — route stability, deferred reads, and cross-phase back-writing.
- [`compose-stability-diagnostics`](skills/compose-stability-diagnostics/SKILL.md) — diagnose Compose compiler reports, strong skipping behavior, unstable parameters, and stability fixes.
- [`compose-state-deferred-reads`](skills/compose-state-deferred-reads/SKILL.md) — move frame-rate reads out of composition; avoid back-writing snapshot state across phases and cross-row measurement reads in composition.

#### UI API design and layout

- [`compose-modifier-and-layout-style`](skills/compose-modifier-and-layout-style/SKILL.md) — keep Compose layout APIs caller-placeable and modifier chains readable.
- [`compose-slot-api-pattern`](skills/compose-slot-api-pattern/SKILL.md) — design reusable Compose components whose variable visual regions are caller-provided slots.
- [`compose-animations`](skills/compose-animations/SKILL.md) — choose Compose animation APIs for visibility, value targets, coordinated transitions, and content swaps; align with official quick guide and decision tree.
- [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) — design and test keyboard, TV, D-pad, and focus-first Compose navigation behavior.

#### Testing

- [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) — choose between plain UI tests, semantics assertions, key/focus tests, interaction state tests with MutableInteractionSource, screenshot tests, and integration tests.

### Kotlin

- [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md) — review coroutine scope ownership, init and fire-and-forget boundaries, cancellation handling, and blocking boundaries.
- [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) — write and review Kotlin branching with subject `when`, guard conditions, sealed exhaustiveness, smart casts, nullable branching, and early returns.
- [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) — model `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, sharing policy, and one-shot events without lossy defaults.
- [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/SKILL.md) — design semantic expect/actual and interface boundaries for Kotlin Multiplatform platform interop.
- [`kotlin-types-value-class`](skills/kotlin-types-value-class/SKILL.md) — choose `@JvmInline value class` over data class for single-field domain types, including Compose stability implications.

### Workflows

- [`implement-issue`](skills/implement-issue/SKILL.md) — review and implement a specific GitHub or GitLab issue through safe forge detection, planning, implementation, review, verification, and branch completion.
- [`shepherd`](skills/shepherd/SKILL.md) — autonomously poll open PRs and MRs, triage review comments, detect and fix CI failures, and keep PRs moving forward.

## Contributing

Skills live at `skills/<skill-name>/SKILL.md`, flat (no language nesting). The `name:` in the SKILL.md frontmatter must match the directory name.

Frontmatter is validated against [`skills.schema.json`](skills.schema.json) — `name` and `description` are required, `name` must be kebab-case.

### Releases

Release versions use SemVer-compatible CalVer: `YYYY.M.D` without zero-padded month or day values, for example `2026.6.17`.

Keep `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and new Git release tags on the same version. Existing zero-padded tags from before this policy map to the non-padded manifest version, so `2026.06.16` maps to `2026.6.16`. Only bump versions when publishing an installable release.

To publish a release, run the **Release** workflow from GitHub Actions. Leave the version input empty to use today's UTC `YYYY.M.D` version, or provide a specific non-zero-padded CalVer value. Use the dry-run option to validate without creating a commit, tag, or GitHub release.

Before pushing, lint skills (frontmatter schema + markdown):

```
npm install
npm run lint
```

This also runs on CI for all PRs.

## License

[Apache 2.0](LICENSE)

[plugins]: https://docs.claude.com/en/docs/claude-code/plugins
