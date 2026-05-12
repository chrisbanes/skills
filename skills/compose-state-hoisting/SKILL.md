---
name: compose-state-hoisting
description: Use when deciding where Jetpack Compose UI element state or UI logic should live: local remember state, hoisted composable parameters, a plain state holder class, or a screen-level ViewModel/component.
---

# Compose state hoisting

## Core principle

Hoist state only as far as the logic needs it. Keep simple UI element state local, move shared UI element state to the lowest common composable owner, extract a plain state holder when UI-only behavior becomes a concept, and use a screen state holder when business logic or app data is involved.

## Decision guide

| Situation | Owner |
|---|---|
| One composable reads/writes simple state | Keep local with `remember` / `rememberSaveable` |
| Sibling or parent composables need to read/write it | Hoist state and events to their lowest common composable ancestor |
| Related UI element state plus UI logic is making a composable hard to read, preview, or test | Extract a plain state holder class remembered in composition |
| Repository calls, persistence, business rules, or screen UI state production are involved | Use a screen-level state holder such as a `ViewModel` or component |

UI element state includes things like expansion, sheet visibility, scroll position, focus, text field editing state, selection, and animation/interaction state. Screen UI state is app data prepared for display.

If UI element state is an input to business logic, it may need to live in the screen state holder too. For example, text used to query repository-backed suggestions belongs with the state holder that produces those suggestions.

## Plain state holder trigger

Extract a plain state holder when several of these are true:

- Multiple related `remember` values are coordinated by the same callbacks.
- Scroll, focus, text, selection, or sheet state needs named operations such as `clear`, `submit`, `jumpToTop`, or `openFilters`.
- Derived UI flags are scattered through the composable.
- Child composables receive mechanics they do not conceptually own.
- Previews or tests must drive a long sequence of UI details to check one behavior.
- Helper functions need many state parameters just to keep the composable readable.

Do not extract for one boolean, one text field, or trivial show/hide logic. Ceremony is not separation of concerns.

## Pattern

Use a plain class for UI element state and UI logic, plus a `remember...State` function for composition-owned objects:

```kotlin
@Stable
class ProductSearchState(
    query: String,
    private val listState: LazyListState,
    private val focusRequester: FocusRequester,
) {
    var query by mutableStateOf(query)
        private set

    var filtersOpen by mutableStateOf(false)
        private set

    val canClear: Boolean
        get() = query.isNotEmpty()

    fun updateQuery(value: String) {
        query = value
    }

    fun clear() {
        query = ""
        focusRequester.requestFocus()
    }

    suspend fun jumpToTop() {
        listState.animateScrollToItem(0)
    }
}

@Composable
fun rememberProductSearchState(
    initialQuery: String = "",
    listState: LazyListState = rememberLazyListState(),
    focusRequester: FocusRequester = remember { FocusRequester() },
): ProductSearchState {
    return remember(listState, focusRequester) {
        ProductSearchState(initialQuery, listState, focusRequester)
    }
}
```

The composable renders from the state holder and calls intent-style methods. If a parent needs to coordinate the same UI behavior, accept the state holder as a parameter with a default:

```kotlin
@Composable
fun ProductSearchPanel(
    state: ProductSearchState = rememberProductSearchState(),
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()

    SearchField(
        query = state.query,
        onQueryChange = state::updateQuery,
        onClear = state::clear,
    )

    JumpToTopButton(onClick = {
        scope.launch { state.jumpToTop() }
    })
}
```

## Composition ownership

Plain state holders created with `remember` follow the composable lifecycle. This makes them a good home for Compose UI objects such as `LazyListState`, `FocusRequester`, `PagerState`, `DrawerState`, and `TextFieldState`.

Keep suspend UI operations that require a frame clock, such as scroll or drawer animations, in a composition-scoped coroutine (`rememberCoroutineScope`, `LaunchedEffect`, or another composition-owned scope). Do not move those calls to `viewModelScope`.

## Saving state

Use `rememberSaveable` or a custom `Saver` only for values that should survive Activity or process recreation, such as a query string, selected filter IDs, or a current tab key.

Do not try to save runtime objects like `LazyListState`, `FocusRequester`, coroutine scopes, or callbacks directly. Save the minimal serializable values needed to rebuild behavior.

## Common mistakes

| Mistake | Fix |
|---|---|
| Hoisting every local state value to a parent "just in case" | Hoist to the lowest owner that actually reads or writes it |
| Extracting a plain state holder for one boolean | Keep simple private UI state local |
| Putting repository calls or product rules in a Compose state holder | Move that logic to a screen state holder such as a `ViewModel` or component |
| Keeping text or selection local when it drives repository-backed screen state | Move that input to the screen state holder with the business logic |
| Passing a state holder deep into unrelated children | Pass plain values and callbacks unless the child truly coordinates the holder's behavior |
| Treating the holder as a dumping ground for a whole screen | Split by cohesive UI behavior, such as search input, sheet coordination, or list controls |
| Calling animation suspend functions from `viewModelScope` | Use a composition-scoped coroutine |

## Related

- [`compose-state-authoring`](../compose-state-authoring/SKILL.md) — correct local `remember` and mutable state authoring.
- [`compose-state-holder-ui-split`](../compose-state-holder-ui-split/SKILL.md) — split screen state-holder wiring from plain state-driven UI rendering.
- [`compose-side-effects`](../compose-side-effects/SKILL.md) — choose effect APIs and composition-scoped coroutine boundaries.
- [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md) — focus state, requesters, and keyboard/D-pad behavior.
