# Kotlin Flow: state and event modeling

## Core principle

Choose the primitive from its replay, fan-out, buffer, and synchronous-read
contract. Do not use fake domain data to satisfy a primitive's initialization.

## Choose the contract

| Need | Primitive |
|---|---|
| Current, renderable state with synchronous `.value` | `StateFlow` for the state it owns. |
| Hot broadcast without synchronous `.value` | Deliberately configured `SharedFlow`. |
| Best-effort handoff to one consumer across a collector gap | Bounded `Channel` exposed with `receiveAsFlow()`. |
| Work that must remain available until handled | Pending state with an identity and acknowledgement. |
| Independent stream per collector | Cold `Flow`. |

Before choosing `SharedFlow`, ask whether an absent collector may lose an event
and whether every observer must receive it. A channel distributes each event to
at most one collector. Its buffer can hold events while no collector is active.
Bounded `send` can suspend and `trySend` can fail, so handle failed sends.
Cancellation after receipt can remove the event before the collector handles it,
and a replacement collector cannot recover it from the channel. Choose
deliberate broadcast semantics when every active observer must see the event.

```kotlin
private val navigation = Channel<Navigation>(Channel.BUFFERED)
val navigationEvents: Flow<Navigation> = navigation.receiveAsFlow()
```

For work that must survive collector cancellation, expose pending state from
the owner and acknowledge the observed ID only after handling succeeds. This
example has one pending slot. When every request must be kept, hold a queue
instead of replacing an unacknowledged item.

```kotlin
data class PendingNavigation(val id: Long, val destination: String)

private val pending = MutableStateFlow<PendingNavigation?>(null)
val pendingNavigation = pending.asStateFlow()

fun acknowledge(id: Long) {
    pending.update { current -> current.takeUnless { it?.id == id } }
}
```

Use a unique ID for each item so an old acknowledgement cannot clear newer
work. Pending state survives collector cancellation for the owner's lifetime.
If handling succeeds just before cancellation prevents acknowledgement, the
next collector may retry it. Use idempotent handling when retries must avoid
duplicate effects and persistence when requests must survive process death.

## State initialization and updates

`StateFlow` needs an initial value. If absence, loading, or error is real, model
it explicitly (`User?`, sealed UI state, `Result`). Otherwise phase the API so
observers first see a real value; do not leak a fake `NoUser` or placeholder ID
as domain data.

Use `update` for a concurrent state transform and keep it pure and fast. The
lambda may retry, so capture I/O, logging inputs, random IDs, and time before
it unless they depend on current state.

```kotlin
val details = Details.from(response)
_state.update { current -> current.copy(details = details) }
```

## Sharing and derived state

Expose `stateIn` as one shared property. Use `SharingStarted.Eagerly` when the
cache should keep updating without active subscribers and callers can tolerate
lag. Sharing runs in a separate coroutine, so reading its `.value` immediately
after an upstream write can still return the previous cached value.
`WhileSubscribed` can also retain a stale value while collection is stopped.

For an immediate read after a write, project the current upstream snapshot
directly. Keep that projection fast and pure. Use a mapped `Flow` separately if
callers also need to observe changes.

```kotlin
val cachedName: StateFlow<String> = userState
    .map { it.name }
    .stateIn(viewModelScope, SharingStarted.Eagerly, userState.value.name)

val currentName: String
    get() = userState.value.name
```

Finish by stating the consumer count, absent-collector behavior, replay, buffer,
and `.value` requirements. If any is unknown, do not choose a primitive yet.

## Related

- [Kotlin control flow](../../kotlin-control-flow/SKILL.md) — state and event branching.
- [Structured concurrency](structured-concurrency.md) — scope and cancellation ownership.
- [Compose state and effects](../../compose-state-and-effects/SKILL.md) — UI collection.
