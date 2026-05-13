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

## Skills

### Start here

- Working on Compose state or effects? Start with [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md), [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md), [`compose-state-holder-ui-split`](skills/compose-state-holder-ui-split/SKILL.md), or [`compose-side-effects`](skills/compose-side-effects/SKILL.md).
- Investigating recomposition, stability, or jank? Start with [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md).
- Reviewing Flow or coroutine architecture? Start with [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) or [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md).

### Jetpack Compose

#### State and side effects

- [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md) — author Compose local mutable state and read-only composable accessors correctly.
- [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md) — decide whether Compose UI element state belongs in local remember state, hoisted parameters, a plain state holder class, or a screen-level state holder.
- [`compose-state-holder-ui-split`](skills/compose-state-holder-ui-split/SKILL.md) — split Compose state-holder wiring from plain-state UI for previewable and testable screens.
- [`compose-side-effects`](skills/compose-side-effects/SKILL.md) — choose and key Compose effect APIs for event Flow collection, callbacks, cleanup, navigation, snackbar, analytics, and other side effects.

#### Performance

- [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md) — choose between the two recomposition investigation paths: stability/equality or deferred state reads.
- [`compose-stability-diagnostics`](skills/compose-stability-diagnostics/SKILL.md) — diagnose Compose compiler reports, strong skipping behavior, unstable parameters, and stability fixes.
- [`compose-state-deferred-reads`](skills/compose-state-deferred-reads/SKILL.md) — move frame-rate scroll, animation, and gesture reads out of composition into layout or draw.

#### UI API design and layout

- [`compose-modifier-and-layout-style`](skills/compose-modifier-and-layout-style/SKILL.md) — keep Compose layout APIs caller-placeable and modifier chains readable.
- [`compose-slot-api-pattern`](skills/compose-slot-api-pattern/SKILL.md) — design reusable Compose components whose variable visual regions are caller-provided slots.
- [`compose-animations`](skills/compose-animations/SKILL.md) — choose Compose animation APIs for visibility, value targets, coordinated transitions, and content swaps; align with official quick guide and decision tree.
- [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) — design and test keyboard, TV, D-pad, and focus-first Compose navigation behavior.

#### Testing

- [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) — choose between plain UI tests, semantics assertions, key/focus tests, screenshot tests, and integration tests.

### Kotlin

- [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md) — review coroutine scope ownership, init and fire-and-forget boundaries, cancellation handling, and blocking boundaries.
- [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) — model `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, sharing policy, and one-shot events without lossy defaults.
- [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/SKILL.md) — design semantic expect/actual and interface boundaries for Kotlin Multiplatform platform interop.
- [`kotlin-types-value-class`](skills/kotlin-types-value-class/SKILL.md) — choose `@JvmInline value class` over data class for single-field domain types, including Compose stability implications.

## Contributing

Skills live at `skills/<skill-name>/SKILL.md`, flat (no language nesting). The `name:` in the SKILL.md frontmatter must match the directory name.

## License

[Apache 2.0](LICENSE)

[plugins]: https://docs.claude.com/en/docs/claude-code/plugins
