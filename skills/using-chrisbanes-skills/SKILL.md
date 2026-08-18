---
name: using-chrisbanes-skills
description: Use when debugging, benchmarking, or profiling leads into Kotlin or Jetpack Compose source before the cause is known, or when a broad Kotlin or Compose review spans multiple design concerns.
paths:
  - "**/*.kt"
  - "**/*.kts"
---

# Using chrisbanes skills

## Core principle

Route by the decision the code needs, not by the number of APIs mentioned in
the prompt. Load one cluster when its shared procedure owns the concern; add a
specialist only when its independent behavior changes the same work.

## Routing procedure

1. Read the task and the Kotlin source that makes the code-design concern concrete.
2. If one focused skill clearly matches, load it directly and stop routing.
3. Otherwise, match each observed code signal to the table below and load the smallest skill set that covers the work.
4. Combine skills only when separate concerns affect the same change; do not load adjacent skills speculatively.
5. Finish routing when every material concern has one focused owner and those skills are loaded before advice or edits.

## Common routes

| Task signal | Start with |
|---|---|
| Broad Compose screen review, local or hoisted UI state, screen state holders, effect APIs, navigation, snackbar, analytics, focus requests, or event Flow collection | [`compose-state-and-effects`](../compose-state-and-effects/SKILL.md) |
| Recomposition, jank, compiler reports, skippability, unstable parameters, frame-rate State reads, back-writing, or `@ReadOnlyComposable` | [`compose-performance`](../compose-performance/SKILL.md) |
| Modifier parameters, root layout placement, variable visual content, primitive content parameters, optional content, or Boolean shape flags | [`compose-component-design`](../compose-component-design/SKILL.md) |
| Compose visibility, value, color, size, transition, content swap, or choosing an animation API | [`compose-animations`](../compose-animations/SKILL.md) |
| Keyboard, TV, desktop, D-pad, `FocusRequester`, `focusProperties`, key events, or initial focus behavior | [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md) |
| Compose UI tests, screenshot tests, previews, semantics, fake image loading, keyboard input, focus assertions, or interaction state tests | [`compose-ui-testing-patterns`](../compose-ui-testing-patterns/SKILL.md) |
| Coroutine scope ownership, `init { launch }`, non-suspending launch APIs, `runBlocking`, cancellation, `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, or one-shot events | [`kotlin-concurrency-and-flow`](../kotlin-concurrency-and-flow/SKILL.md) |
| Kotlin branching, `when` expressions, guard conditions, sealed type exhaustiveness, smart casts, nullable branching, or complex `if`/`else` chains | [`kotlin-control-flow`](../kotlin-control-flow/SKILL.md) |
| Kotlin function placement, member versus top-level or extension functions, factories, single-field domain types, value classes, Kotlin Multiplatform source sets, expect/actual, or platform services | [`kotlin-api-design`](../kotlin-api-design/SKILL.md) |
| Planned Gradle execution, or a Gradle-centered build, check, warning-cleanup, or failure workflow | [`gradle-run`](../gradle-run/SKILL.md) |
| One ready GitHub issue or in-chat task needs repository-aware planning before a separate implementation session | [`to-plan`](../to-plan/SKILL.md) |
| Polling or shepherding PRs/MRs, triaging review comments, fixing CI failures, or keeping reviews moving | [`shepherd`](../shepherd/SKILL.md) |

## Combining skills

- For Compose event handling from a component, use [`compose-state-and-effects`](../compose-state-and-effects/SKILL.md), then add [`kotlin-concurrency-and-flow`](../kotlin-concurrency-and-flow/SKILL.md) when event delivery semantics matter.
- For performance work, start with [`compose-performance`](../compose-performance/SKILL.md).
- For animations triggered by state, use [`compose-animations`](../compose-animations/SKILL.md); add [`compose-state-and-effects`](../compose-state-and-effects/SKILL.md) for ownership changes and [`compose-performance`](../compose-performance/SKILL.md) for frame-rate values.
- For reusable UI components, use [`compose-component-design`](../compose-component-design/SKILL.md).
- For tests around focus behavior, use [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md) first, then [`compose-ui-testing-patterns`](../compose-ui-testing-patterns/SKILL.md) for test shape.
- For Kotlin state, concurrency, or platform-boundary work that also changes branching shape, combine the cluster with [`kotlin-control-flow`](../kotlin-control-flow/SKILL.md).
- Kotlin or Compose advice that performs no Gradle execution does not load [`gradle-run`](../gradle-run/SKILL.md).

## RED/GREEN agent scenarios

1. RED loads every Compose skill for a screen with local state and a snackbar.
   GREEN loads [`compose-state-and-effects`](../compose-state-and-effects/SKILL.md) first and adds another skill only for an evidenced concern.
2. Novel case: a reusable card has a modifier problem and animated height.
   GREEN uses [`compose-component-design`](../compose-component-design/SKILL.md) plus [`compose-animations`](../compose-animations/SKILL.md), not the state cluster by default.
3. Counterexample: a request only changes a guard condition in common Kotlin.
   GREEN loads [`kotlin-control-flow`](../kotlin-control-flow/SKILL.md) and does not route through API design.
