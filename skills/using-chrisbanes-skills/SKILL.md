---
name: using-chrisbanes-skills
description: Use when a Kotlin, Android, or Jetpack Compose task is too broad for any single focused skill to obviously apply, especially for general review, refactor, architecture, state, performance, testing, or UI API design work.
---

# Using chrisbanes skills

Router only. Use this skill to choose the focused skill or skills for the task, then load those focused skills before giving detailed advice or editing code.

If a request already clearly matches a focused skill, use that skill directly. If several areas affect the work, load each relevant focused skill before acting on that area.

## Common routes

| Task signal | Start with |
|---|---|
| Broad Compose screen review or refactor | [`compose-state-holder-ui-split`](../compose-state-holder-ui-split/SKILL.md), then add state, effects, layout, testing, or performance skills as needed |
| Local Compose state, bare local `var`, `remember { mutableStateOf(...) }`, `mutableStateListOf`, or `@ReadOnlyComposable` | [`compose-state-authoring`](../compose-state-authoring/SKILL.md) |
| Deciding whether state belongs locally, hoisted, in a plain state holder, or in a screen state holder | [`compose-state-hoisting`](../compose-state-hoisting/SKILL.md) |
| ViewModel, component, controller, navigation, Flow collection, or dependency wiring mixed with UI layout | [`compose-state-holder-ui-split`](../compose-state-holder-ui-split/SKILL.md) |
| `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope`, `rememberUpdatedState`, navigation, snackbar, analytics, focus requests, or event Flow collection | [`compose-side-effects`](../compose-side-effects/SKILL.md) |
| Recomposition, jank, compiler reports, Layout Inspector counts, unstable params, scroll reads, animation reads, or back-writing state across phases | [`compose-recomposition-performance`](../compose-recomposition-performance/SKILL.md) |
| Known Compose stability or skippability question, compiler `classes.txt` / `composables.txt`, collection parameters, or strong skipping | [`compose-stability-diagnostics`](../compose-stability-diagnostics/SKILL.md) |
| Frame-rate state reads from scroll, animation, gestures, layout, or draw; value-form layout/draw modifiers; measurement state back-writing | [`compose-state-deferred-reads`](../compose-state-deferred-reads/SKILL.md) |
| Modifier parameters, root layout placement, hardcoded layout decisions, or modifier chain style | [`compose-modifier-and-layout-style`](../compose-modifier-and-layout-style/SKILL.md) |
| Reusable Compose component API with variable visual content, primitive content params, optional content params, or boolean shape flags | [`compose-slot-api-pattern`](../compose-slot-api-pattern/SKILL.md) |
| Compose visibility, value, color, size, transition, content swap, or choosing an animation API | [`compose-animations`](../compose-animations/SKILL.md) |
| Keyboard, TV, desktop, D-pad, `FocusRequester`, `focusProperties`, key events, or initial focus behavior | [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md) |
| Compose UI tests, screenshot tests, previews, semantics, fake image loading, keyboard input, focus assertions, or interaction state tests | [`compose-ui-testing-patterns`](../compose-ui-testing-patterns/SKILL.md) |
| Coroutine scope ownership, `init { launch }`, non-suspending APIs that launch work, `runBlocking`, or cancellation handling | [`kotlin-coroutines-structured-concurrency`](../kotlin-coroutines-structured-concurrency/SKILL.md) |
| `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, `SharingStarted`, `.value`, one-shot events, sentinel initial values, or expensive `update` blocks | [`kotlin-flow-state-event-modeling`](../kotlin-flow-state-event-modeling/SKILL.md) |
| Kotlin Multiplatform platform APIs, source set boundaries, `expect`/`actual`, interfaces for platform services, permissions, files, sensors, native SDKs, or Compose Multiplatform interop | [`kotlin-multiplatform-expect-actual`](../kotlin-multiplatform-expect-actual/SKILL.md) |
| Single-field domain types, primitive obsession, or choosing `@JvmInline value class` vs `data class` | [`kotlin-types-value-class`](../kotlin-types-value-class/SKILL.md) |
| Polling or shepherding PRs/MRs, triaging review comments, fixing CI failures, or keeping reviews moving | [`shepherd`](../shepherd/SKILL.md) |

## Combining skills

- For Compose event handling from a ViewModel or component, use [`compose-state-holder-ui-split`](../compose-state-holder-ui-split/SKILL.md), [`compose-side-effects`](../compose-side-effects/SKILL.md), and, if the event primitive matters, [`kotlin-flow-state-event-modeling`](../kotlin-flow-state-event-modeling/SKILL.md).
- For performance work, start with [`compose-recomposition-performance`](../compose-recomposition-performance/SKILL.md). It routes deeper to stability or deferred-read fixes.
- For animations triggered by state, use [`compose-animations`](../compose-animations/SKILL.md) together with [`compose-state-holder-ui-split`](../compose-state-holder-ui-split/SKILL.md); for frame-rate-driven animation values, also load [`compose-state-deferred-reads`](../compose-state-deferred-reads/SKILL.md).
- For reusable UI components, pair [`compose-modifier-and-layout-style`](../compose-modifier-and-layout-style/SKILL.md) with [`compose-slot-api-pattern`](../compose-slot-api-pattern/SKILL.md) when both placement and content flexibility are in play.
- For tests around focus behavior, use [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md) first, then [`compose-ui-testing-patterns`](../compose-ui-testing-patterns/SKILL.md) for test shape.
