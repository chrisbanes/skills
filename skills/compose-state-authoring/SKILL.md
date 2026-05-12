---
name: compose-state-authoring
description: Use when writing or reviewing Jetpack Compose code with bare local var in a @Composable, remember { mutableStateOf(...) }, mutableStateListOf/mutableStateMapOf, or @ReadOnlyComposable.
---

# Compose state authoring

Not every `remember { … }` belongs here. This skill covers **local UI state** (`remember { mutableStateOf(…) }`, `mutableStateListOf` / `mutableStateMapOf`) and **`@ReadOnlyComposable`**. Other remembered APIs live in focused skills:

- **`rememberCoroutineScope` / `rememberUpdatedState`** → [`compose-side-effects`](../compose-side-effects/SKILL.md)
- **`rememberLazyListState` / `rememberScrollState`** used for frame-rate reads → [`compose-state-deferred-reads`](../compose-state-deferred-reads/SKILL.md)
- **Focus navigation, focus state, `FocusRequester` ownership, behavior** → [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md)

## Core principle

A `@Composable` is a function the runtime re-runs whenever its inputs change. Writing local state correctly comes down to two questions:

1. **Mutable local state** — does my `var` survive recomposition *and* trigger it? If not, it silently resets on every recompose and writes are invisible.
2. **What kind of composable is this?** — do I *mutate* composition (place layout nodes, allocate slots, `remember`) or only *read* it? If only read, `@ReadOnlyComposable` lets the runtime skip work.

Get either wrong and the symptoms are subtle: state that vanishes or optimizations that don't apply.

## When to use this skill

You're writing or reviewing Compose code and you see any of these:

- `var x = …` inside a `@Composable fun` or any composable lambda (`Column { var x = … }`)
- A `@Composable fun` (or `@Composable get()` property accessor) whose body never lays anything out
- `@ReadOnlyComposable` on a function that calls `Text`, `Box`, `Column`, `remember`, …
- A composable whose visible state mysteriously resets on rotation, theme change, or recomposition

## 1. `var` in a composable must be State-backed

Recomposition re-executes the composable from the top. A local `var` is *re-initialized* on every pass — last recompose's value is gone, and writing to it doesn't tell the runtime to recompose.

```kotlin
// ❌ BAD — counter resets on every recomposition; clicks never update the UI
@Composable
fun Counter() {
    var count = 0
    Button(onClick = { count++ }) { Text("$count") }
}

// ❌ ALSO BAD — same rule applies inside composable content lambdas
@Composable
fun Wrapper() {
    Row {
        var count = 0         // Row's content lambda is @Composable too
        // …
    }
}
```

```kotlin
// ✅ GOOD — `remember` survives recomposition, `mutableStateOf` triggers it
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) { Text("$count") }
}
```

Two pieces and both matter:

- `remember { … }` — *survives recomposition*. Without it the value is re-created each time.
- `mutableStateOf(…)` — *triggers recomposition*. Without it, mutations are invisible to the runtime.

For collections, prefer `mutableStateListOf` / `mutableStateMapOf` (also `remember`-ed). They emit Snapshot reads on every read and Snapshot writes on every mutation. A `remember { mutableStateOf(mutableListOf<X>()) }` followed by `list.add(x)` will *not* recompose, because `MutableList.add` doesn't go through the State setter — you'd have to replace the value (`state = state + x`).

### When this rule does NOT apply

- **Inside `remember { … }`'s producer block.** That runs once per key change, not on every recompose. A local `var` there is fine: `val builder = remember { mutableListOf<X>().apply { var n = 0; … } }`.
- **In non-`@Composable` lambdas passed *out* of a composable.** `onClick = { var a = 0; … }` is a plain `() -> Unit`. Local vars there are normal Kotlin.
- **In plain (non-`@Composable`) helper functions.** Only composable scopes are affected.

## 2. The `@ReadOnlyComposable` contract

`@ReadOnlyComposable` declares that a composable *only reads* composition state — no `Text`, no `Box`, no `remember`, no layout nodes, no positional slots. The runtime can then skip allocating a group for the call, which matters for fast accessor-style composables (`MaterialTheme.colorScheme`, `LocalDensity.current`, design-system token accessors).

The contract is **bidirectional**:

- **Add `@ReadOnlyComposable`** when every composable call your body makes is itself `@ReadOnlyComposable` (or there are no composable calls at all — for example a function that only reads `LocalFoo.current` and returns a value).
- **Don't add it** if you call any non-read-only composable. The optimization assumes you don't participate in composition; violating that produces incorrect recomposition behaviour for callers.

```kotlin
// ✅ GOOD — only reads composition locals, no layout, no remember
@Composable
@ReadOnlyComposable
fun appSpacing(): Dp = LocalDimensions.current.spacing

// ✅ GOOD — composable property getter; same rule
val accent: Color
    @Composable @ReadOnlyComposable
    get() = MaterialTheme.colorScheme.tertiary
```

```kotlin
// ❌ BAD — annotated read-only but lays out a Box; contract violated
@Composable
@ReadOnlyComposable
fun Header(): Int {
    Box {}                  // ← non-read-only composable call
    return 42
}

// ❌ BAD — calls a normal composable from a read-only one
@Composable
@ReadOnlyComposable
fun computed(): Int = nonReadOnlyHelper()
```

### Heuristic for "should I add it"

If the body contains any of these, **do not** add `@ReadOnlyComposable`:

- A layout call: `Box`, `Column`, `Row`, `LazyColumn`, `Text`, anything from `androidx.compose.foundation.layout` or `androidx.compose.material*`.
- A side-effect call: `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `produceState`.
- `remember { … }` — positional memoization is composition state.
- A `@Composable` lambda invocation (`content()`).
- An invocation of a non-`@ReadOnlyComposable` composable function.

If the body is only reading `Local*.current`, calling other `@ReadOnlyComposable` functions, or doing pure computation, **add** it.

### When this rule does NOT apply

- **`override fun` declarations.** The annotation is part of the contract; if the base isn't `@ReadOnlyComposable`, you can't make an override one. Refactor the base, or accept the override pays the group-creation cost.
- **Abstract declarations.** No body to check.

## Related: side effects live in their own skill

If a composable needs `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope`, `rememberUpdatedState`, `snapshotFlow`, snackbar/navigation handling, analytics, or Flow collection, use [`compose-side-effects`](../compose-side-effects/SKILL.md).

Focus splits by question: **navigation, focus state, `FocusRequester` ownership, behavior** → [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md); **when** to call imperative `requestFocus` (effect timing, lifecycle, keys, API choice) → [`compose-side-effects`](../compose-side-effects/SKILL.md).

This skill is about authoring Compose state correctly. `rememberUpdatedState` is effect capture state, not a general replacement for `remember { mutableStateOf(...) }`. Side effects have separate lifecycle and keying rules, and keeping them in one focused skill avoids two sources of truth.

## Quick reference

| Symptom | Diagnosis | Fix |
|---|---|---|
| `var x = …` inside `@Composable fun` body | Not recomposition-safe (§1) | `var x by remember { mutableStateOf(…) }` |
| `var x = …` inside `Column { … }` / `Row { … }` content lambda | Same — content lambdas are `@Composable` (§1) | Same fix |
| `remember { mutableStateOf(list) }` then `.add(x)` not recomposing | Mutation bypasses State setter | Use `mutableStateListOf`, or replace the value: `state = state + x` |
| `@Composable fun` with no `Text`/`Box`/`remember`/effect calls | Could be `@ReadOnlyComposable` (§2) | Add `@ReadOnlyComposable` above `@Composable` |
| `@ReadOnlyComposable` function that calls `Box {}` / `Column {}` / a normal composable | Contract violation (§2) | Remove `@ReadOnlyComposable` |

## When NOT to apply

- **Tests** with `composeTestRule.setContent { … }` follow the same rules — they're production composables.
- **`produceState`** has its own producer block that runs in a coroutine; you don't need `LaunchedEffect` *inside* it.
- **`derivedStateOf`** has its own concerns around stability and equality — out of scope here; it's about *preventing* recomposition, not authoring state.
- **`override`s** of read-only-composable declarations: the annotation is fixed by the base; you can't add or remove it locally.

## Red flags during review

| Thought | Reality |
|---|---|
| "It's a small composable, the bare `var` is fine" | Recomposition can fire at any time. The reset is non-deterministic by design — and a single bug report later. |
| "I'll add `@ReadOnlyComposable` because the function looks simple" | "Simple" isn't the criterion. "Makes only read-only calls" is. |
| "I always reach for `LaunchedEffect` because it's the one I know" | Use `compose-side-effects`; effect API choice depends on lifecycle and keys. |
| "I'll just `.add()` to the remembered list" | A `mutableStateOf(List)` doesn't observe internal mutation — use `mutableStateListOf` or replace the value. |
| "The override needs `@ReadOnlyComposable` to match what it does" | If the base isn't `@ReadOnlyComposable`, you can't add it to an override. Refactor the base instead. |
