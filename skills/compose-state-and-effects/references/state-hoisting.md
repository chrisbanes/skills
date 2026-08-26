# Compose state hoisting

## Core principle

Hoist state only as far as its logic needs it; screen wiring and plain rendering are separate owners.

## Procedure

1. List the state, operations, app dependencies, event streams, and effects that need coordination.
2. Choose the lowest owner from the table.
3. Extract a plain state holder only when coordinated UI behavior is a concept; keep a lone boolean or trivial text field local.
4. At a screen boundary, implement the three seams defined in the parent skill: small wiring owns app dependencies, durable data, and effects; composition or a plain UI state holder owns runtime UI objects; a plain composable receives immutable UI state and event callbacks.
5. Keep frame-clock operations such as scrolling or drawer animation in a composition-scoped coroutine, not `viewModelScope`.
6. Save serializable values with `rememberSaveable`/a `Saver`, never runtime objects or callbacks.
7. Finish by stating the concrete boundary for an ownership review, or make no change when the existing owner already matches the evidence.

| Situation | Owner |
|---|---|
| One composable owns simple UI state | Local `remember` / `rememberSaveable` |
| Siblings or a parent share it | Lowest common composable owner |
| Related UI mechanics need named operations or coordinated state | Plain state holder remembered in composition |
| Repository calls, persistence, business rules, or screen state production | Screen-level holder such as `ViewModel` or component |
| App wiring and layout are mixed | Small wiring composable plus plain UI composable |

```kotlin
@Composable
fun ProfileScreen(component: ProfileComponent, modifier: Modifier = Modifier) {
    val state by component.state.collectAsStateWithLifecycle()
    ProfileContent(
        state = state,
        onNameChange = component::onNameChange,
        onSaveClick = component::save,
        onBackClick = component::back,
        modifier = modifier,
    )
}
```

A plain state holder can retain `LazyListState`, `FocusRequester`, `PagerState`, drawer state, and other UI mechanics created in composition. Pass business-relevant derived values across the screen boundary, but do not expose those runtime objects to the screen holder. When a child must coordinate the holder, accept it deliberately; otherwise pass plain values and callbacks.

## Exceptions

- Do not split a tiny one-off composable that already receives plain values and callbacks.
- Do not create a state-holder/UI overload for structural symmetry or a design-system primitive; use slots and modifiers for those APIs.
- If UI input drives repository-backed data, keep that input with the screen holder that produces the data.

## Related

- [Local state](local-state.md) for correct `remember` and snapshot-state authoring.
- [Side effects](side-effects.md) for effect APIs, keys, and cleanup.
- [Compose UI testing patterns](../../compose-ui-testing-patterns/SKILL.md) for testing plain UI without the app graph.
