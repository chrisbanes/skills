# Kotlin coroutines: structured concurrency

## Core principle

Make asynchronous work a unit with a visible entry, exit, owner, and lifetime.
Most repositories, managers, use cases, and data sources should expose
`suspend` APIs rather than retain a `CoroutineScope`.

## Review procedure

1. Name the caller that owns cancellation, completion, and failure. If none is
   visible, do not add or retain a launch.
2. Replace a stored, injected, lazily created, or function-local `CoroutineScope`
   on a non-UI class with suspending APIs. A cancelled stored scope can make
   future launches silently do nothing.
3. Move construction-time and initializer launches to an explicit suspending
   bootstrap or named launch site. A constructor or `Initializer.initialize()`
   may register, but must not launch.
4. Keep a non-suspending launch only at the UI/state-holder boundary described
   below. Otherwise make the API suspend.
5. Re-throw `CancellationException` from any broad catch around suspension.
   A narrow timeout converted close to its own `withTimeout` is the exception;
   catches of non-cancellation subtypes are also safe.
6. Replace application `runBlocking` with suspension or a lifecycle-bound
   boundary. Use `runTest` in tests; use `runBlocking` only at a true blocking
   edge and keep it small.
7. Compile and test the changed call chain. Finish when a reader can locate the
   owner, start point, cancellation path, and failure behavior without guessing.

## Scope and launch choices

| Situation | Action |
|---|---|
| Repository, manager, use case, or data source needs async work | Expose `suspend`; let the caller choose scope and error handling. |
| UI callback reaches a UI state holder | The state holder may launch on its lifecycle scope. |
| A background reaction has an observable coroutine-owning consumer | Put the suspension at that consumer's mutation or collection site. |
| Work is periodic or deferred | Enqueue scheduled work from a suspending orchestrator. |
| A synchronous external API has no observable lifecycle | Use one explicit named launch site, never a class `init`. |
| Lifecycle infrastructure explicitly owns cancellation, errors, and restart | It may own a scope, but still exposes visible start/stop behavior. |

The UI exception requires all three: the class owns UI state, its scope is
cancelled with that UI surface (`viewModelScope`, component scope, or remembered
Compose scope), and the caller is an actual UI event or lifecycle hook. Its
lower layers remain suspending.

```kotlin
class FavouritesViewModel(private val repository: FavouritesRepository) : ViewModel() {
    fun onToggle(item: Item) {
        viewModelScope.launch { repository.toggle(item) }
    }
}
```

An application singleton is not a loophole for hidden launches. Prefer, in
order: invert the observation into a known consumer; schedule genuinely
periodic work; or launch a suspending observer from one named orchestrator.
If no reader can find who starts, observes, stops, or restarts the work, return
to step 1.

## Cancellation

Broad `catch` and `runCatching` match `CancellationException`. Preserve it:

```kotlin
try {
    api.load()
} catch (error: CancellationException) {
    throw error
} catch (error: Exception) {
    logger.warn("load failed", error)
}
```

`currentCoroutineContext().ensureActive()` is suitable when ordinary failure is
handled locally. `runCatching` needs the same guard, or a terminal
`getOrThrow()`. Do not turn arbitrary cancellation into success.

## Blocking boundaries

Make suspend-capable application code suspend. Use an existing lifecycle scope
at a non-suspending UI callback, and `runTest` for tests. Legitimate
`runBlocking` boundaries include CLI `main`, required synchronous Java/framework
bridges, and migration shims. Android `ContentProvider` member methods are one
such framework boundary; a companion/helper is not. Keep the body to the direct
suspending call.

## Incremental refactor

1. Start at the leaf class farthest from UI.
2. Convert one public function to `suspend` and follow compiler-reported callers.
3. At each caller, select its lifecycle scope deliberately.
4. Remove the unused scope parameter and binding.

Do not apply this to an already-suspending API, a UI state holder handling its
own UI event, or a lifecycle owner with explicit cancellation/error/restart
policy. Do not repair every layer in one change.
