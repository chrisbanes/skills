---
name: compose-animations
description: "Use when writing or reviewing Jetpack Compose motion: visibility enter/exit, animating one property toward a target, color or size transitions, multiple properties from one state, switching composable content, or choosing between AnimatedVisibility, animate*AsState, rememberTransition, AnimatedContent, and Crossfade."
---

# Compose: animations

## Core principle

Pick the smallest API that expresses the motion and its lifecycle.

## Procedure

1. Identify the job: show or hide a subtree, animate one value, coordinate values from one state, resize content, swap content, or handle user-driven motion.
2. Choose the matching API from the table. Prefer target-state APIs; use `Animatable` only when gestures, interruption, or imperative control require it.
3. Check lifecycle: an alpha animation keeps content composed; `AnimatedVisibility` removes it after exit. Do not use a fade when unmounting is required.
4. For `AnimatedContent`, render from the content lambda target and choose a `contentKey` only when visual identity differs from payload equality. Read [AnimatedContent identity](references/animated-content.md) for state-holder details.
5. Keep animated `State` in layout or draw block modifiers when it changes at frame rate; route deeper diagnosis to [Compose performance](../compose-performance/SKILL.md).
6. Use Navigation Compose transitions for destination swaps it owns, and dedicated libraries for art-based motion.
7. Finish when the API, lifecycle, and content identity match the UI, no simpler API fits, and the relevant behavior is verified.

## API choice

| Need | Prefer |
|---|---|
| Show/hide a subtree with enter/exit semantics | [`AnimatedVisibility`](https://developer.android.com/develop/ui/compose/animation/composables-modifiers#animatedvisibility) |
| One value follows state | `animate*AsState` |
| Several values follow one boolean, enum, or sealed state | `rememberTransition` plus child animations |
| Child size changes | `Modifier.animateContentSize()` |
| Different composable trees fill one region | `AnimatedContent`, or `Crossfade` for the simple case |
| Drag, fling, interruption, or imperative control | [`Animatable`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/Animatable) |

Use an `AnimationSpec` when the default motion is wrong and a distinct `label` when multiple animations need tooling visibility.

```kotlin
val width by animateDpAsState(
    targetValue = if (expanded) 200.dp else 56.dp,
    animationSpec = spring(dampingRatio = 0.7f),
    label = "fabWidth",
)
```

For values that must remain synchronized, define them on one transition rather than several independent `animate*AsState` calls:

```kotlin
val transition = rememberTransition(targetState = phase, label = "phase")
val alpha by transition.animateFloat(label = "alpha") { target ->
    if (target == Phase.Visible) 1f else 0f
}
val offset by transition.animateDp(label = "offset") { target ->
    if (target == Phase.Visible) 0.dp else 24.dp
}
```

For animated fills, prefer `drawBehind { drawRect(color.value) }` over a value-form background when the color updates every frame. For an API ambiguity, start with the official [Choose an animation API](https://developer.android.com/develop/ui/compose/animation/choose-api) guide; use [`rememberInfiniteTransition`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/rememberInfiniteTransition) for repeating cycles and [`SeekableTransitionState`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/SeekableTransitionState) for seekable or test-controlled progress.

## When not to use this skill

- For side-effect timing or click-launched work, use [Compose state and effects](../compose-state-and-effects/SKILL.md).
- For deep state-read or recomposition diagnosis, use [Compose performance](../compose-performance/SKILL.md).
