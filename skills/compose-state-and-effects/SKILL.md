---
name: compose-state-and-effects
description: Use when writing or reviewing Jetpack Compose state ownership, remember state, state hoisting, screen state holders, LaunchedEffect, DisposableEffect, SideEffect, Flow collection, navigation, snackbar, analytics, or focus requests.
---

# Compose state and effects

## Core principle

Give every piece of UI state one lowest responsible owner, then run imperative
work through the effect whose lifecycle follows that owner. Composition renders;
state and effects make rendering change safely.

A screen-ownership review is incomplete until it names the plain, previewable
content composable that receives immutable state and event callbacks separately
from app wiring and composition-owned runtime objects.

## Procedure

1. Establish the requested scope and visible behavioral requirements. Treat an
   ownership change as a finding only when code or task evidence shows a
   lifecycle, testability, business, or coordination need.
2. Inventory mutable UI state, app state, event streams, app dependencies, and
   imperative work in the affected screen or component.
3. Place each state value at its lowest necessary owner: local UI state,
   hoisted state, a plain UI state holder, or a screen state holder.
4. For a screen boundary, keep durable data and intents in the wiring owner,
   Compose runtime objects in composition or a plain UI state holder, and
   rendering in a previewable content composable that takes immutable state
   and callbacks. Read [State hoisting](references/state-hoisting.md) for the
   implementation shape; naming only state and intents is not that boundary.
5. Choose an effect API whose lifecycle matches the work, and key it by the
   semantic input that should restart or dispose it.
6. Load the focused reference for every material concern below. Do not use a
   reference merely because its topic is adjacent.
7. Route frame-rate reads, cross-phase back-writing, and
   `@ReadOnlyComposable` contracts to [Compose performance](../compose-performance/SKILL.md).
8. Before responding to a screen-ownership review, verify all three screen
   seams in step 4 when visible code needs them.
9. Finish when every state value has one owner, every effect has a justified
   lifecycle and key, and the UI can be previewed and tested without app
   dependencies. For review-only work, report no change when no evidence-backed
   issue remains; do not invent product requirements.

## Topic router

| Signal | Read |
|---|---|
| Bare local `var`, `remember { mutableStateOf(...) }`, state lists/maps, or reset state | [Local state](references/local-state.md) |
| State shared by siblings, UI state holders, ViewModel/component wiring, or previewable screen boundaries | [State hoisting](references/state-hoisting.md) |
| `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `snapshotFlow`, `rememberCoroutineScope`, `rememberUpdatedState`, `produceState`, imperative `requestFocus`, callbacks, event Flow collection, snackbar, navigation, or analytics | [Side effects](references/side-effects.md) |
| Focus ownership and keyboard/TV/D-pad behavior | [Compose focus navigation](../compose-focus-navigation/SKILL.md) |
| Tests or previews for the resulting UI contract | [Compose UI testing patterns](../compose-ui-testing-patterns/SKILL.md) |
