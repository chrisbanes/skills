# Kotlin Flow: state and event modeling

## Core principle

Choose the primitive from its replay, fan-out, buffer, and synchronous-read
contract. Do not use fake domain data to satisfy a primitive's initialization.

## Choose the contract

| Need | Primitive |
|---|---|
| Current, renderable state with synchronous `.value` | `StateFlow`; often eager when `.value` matters. |
| Hot broadcast without synchronous `.value` | Deliberately configured `SharedFlow`. |
| Exactly-once handoff to one consumer | Buffered `Channel` exposed with `receiveAsFlow()`. |
| Independent stream per collector | Cold `Flow`. |

Before choosing `SharedFlow`, ask whether an absent collector may lose an event
and whether every observer must receive it. A channel is fan-out, not broadcast:
each event reaches one collector; its bounded sends can suspend and `trySend`
can fail. Use durable state or deliberate broadcast semantics when every
observer must see the event.

```kotlin
private val navigation = Channel<Navigation>(Channel.BUFFERED)
val navigationEvents: Flow<Navigation> = navigation.receiveAsFlow()
```

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

Expose `stateIn` as one shared property, not a function that creates another
sharing coroutine per call. If `.value` must be fresh or initialized with no
active collector, use `SharingStarted.Eagerly` or explicit initialization.
`WhileSubscribed` is only for acceptable stale/cached values and primarily
asynchronous collection.

`map` turns a `StateFlow` into a plain `Flow`. When callers need synchronous
`.value`, terminate the derived stream with `stateIn`. Utilities that transform
on each `.value` read are only suitable for fast, idempotent work.

```kotlin
val name: StateFlow<String> = userState
    .map { it.name }
    .stateIn(viewModelScope, SharingStarted.Eagerly, userState.value.name)
```

Finish by stating the consumer count, absent-collector behavior, replay, buffer,
and `.value` requirements. If any is unknown, do not choose a primitive yet.

## Related

- [Kotlin control flow](../../kotlin-control-flow/SKILL.md) — state and event branching.
- [Structured concurrency](structured-concurrency.md) — scope and cancellation ownership.
- [Compose state and effects](../../compose-state-and-effects/SKILL.md) — UI collection.
