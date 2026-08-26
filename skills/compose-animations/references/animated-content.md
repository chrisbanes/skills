# AnimatedContent identity

`AnimatedContent` keeps outgoing and incoming content composed together. Render from its content-lambda target rather than captured outer state, so each branch keeps the identity assigned to it.

```kotlin
// Wrong: both branches can read the newest selectedId.
AnimatedContent(targetState = selectedId) {
    Destination(selectedId)
}

// Right: each branch receives its own target.
AnimatedContent(targetState = selectedId) { targetId ->
    Destination(targetId)
}
```

For a state holder such as `AsyncResult<T>` or a sealed `UiState`, key the transition by the visual shape when payload refreshes should update in place:

```kotlin
AnimatedContent(
    targetState = result,
    contentKey = { state ->
        when (state) {
            AsyncResult.Loading -> "loading"
            is AsyncResult.Success -> "content"
            is AsyncResult.Error -> "error"
        }
    },
    label = "profile-content",
) { state ->
    when (state) {
        AsyncResult.Loading -> Loading()
        is AsyncResult.Success -> Profile(state.value)
        is AsyncResult.Error -> ErrorMessage(state.throwable)
    }
}
```

| Change | Typical key |
|---|---|
| Loading, content, and error have different shapes | A branch key |
| Different items should crossfade | Stable item id |
| A data refresh stays in the same shape | One key for that branch |

Without `contentKey`, unequal payloads can animate as new content. Keep that default only when the payload change itself is the desired transition.
