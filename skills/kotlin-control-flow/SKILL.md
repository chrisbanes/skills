---
name: kotlin-control-flow
description: "Use when writing or reviewing Kotlin branching and control flow: when expressions, guard conditions, sealed type exhaustiveness, smart casts, nullable branching, early returns, or replacing complex if/else chains."
---

# Kotlin control flow

## Purpose

Use this skill to write or review the shape of Kotlin branching code. Treat it as a refactoring procedure, not as a style preference.

The target state is simple: the classified value is obvious, branch-local predicates stay with their branch, smart casts remain usable, and the compiler proves exhaustiveness for closed domains.

## Procedure

Apply these checks in order.

### 1. Name the subject

Find the value the code is classifying. If every branch asks a question about the same value, make that value the `when` subject.

```kotlin
// Replace repeated checks against `state` with a subject `when`.
val action = when (state) {
    State.SignedOut -> Action.ShowSignIn
    is State.SignedIn -> Action.ShowHome(state.user)
}
```

If there is no single subject, keep a subjectless `when` or an `if` chain.

### 2. Pick the branch primitive

Use this decision table before editing:

| If the code has... | Use... |
|---|---|
| One value being classified | `when (subject)` |
| Unrelated boolean conditions | Subjectless `when` or `if`/`else` |
| A primary match plus an extra branch-local predicate | Guard condition |
| Invalid input before the main path | Early return, `require`, or `check` |
| A closed enum, Boolean, sealed type, or nullable closed type returning a value | Exhaustive `when` expression |
| Open external input or a real fallback | Explicit `else` |

### 3. Move branch-local predicates into guard conditions

When a branch first matches a type/value and then checks an extra predicate, use a guard condition:

```kotlin
return when (event) {
    is Event.Message if event.isUnread -> Row.Highlighted(event.message)
    is Event.Message -> Row.Normal(event.message)
    Event.Empty -> Row.Empty
}
```

Apply guards only when all of these are true:

- The `when` has a subject.
- The branch has a primary condition (`is Type`, enum entry, object, value, range, etc.).
- The extra condition belongs only to that branch.
- A later branch still handles the same primary condition, or the expression remains exhaustive some other way.

Put guarded branches before their unguarded fallback for the same primary condition.

### 4. Preserve exhaustiveness

For a `when` expression over a closed domain, handle every case explicitly. Do not add `else` only to quiet the compiler.

```kotlin
val action = when (state) {
    SessionState.SignedOut -> Action.ShowSignIn
    is SessionState.SignedIn -> Action.ShowHome(state.user)
    is SessionState.Expired if state.canRefresh -> Action.Refresh
    is SessionState.Expired -> Action.ShowSignIn
}
```

Use `else` when the domain is open: strings from a server, integer status codes, unknown platform values, or a deliberate fallback/logging path.

### 5. Split unsupported guarded branches

Guard conditions do not apply to comma-separated branch conditions. If only one case needs an extra predicate, split the branch:

```kotlin
when (status) {
    Status.Pending if canRetry -> retry()
    Status.Pending -> showPending()
    Status.Queued -> showQueued()
}
```

### 6. Flatten invalid preconditions

Use early returns when they remove nullable or invalid state from the main path:

```kotlin
fun render(user: User?): UiModel {
    user ?: return UiModel.SignedOut

    return UiModel.SignedIn(
        name = user.name,
        avatar = user.avatar,
    )
}
```

Do not flatten if nesting is carrying cleanup, transaction, or error-handling structure.

### 7. Check smart casts

After reshaping, verify that every branch still has the narrowed type available where it is used. If the rewrite forces `as`, `!!`, temporary mutable vars, or duplicated casts, keep the original shape or choose a smaller refactor.

## Rewrite recipes

### Nested branch inside `when`

When the nested branch only refines one primary case, convert it to guarded branches:

```kotlin
// Before
return when (event) {
    is Event.Message -> {
        if (event.isUnread) Row.Highlighted(event.message) else Row.Normal(event.message)
    }
    Event.Empty -> Row.Empty
}

// After
return when (event) {
    is Event.Message if event.isUnread -> Row.Highlighted(event.message)
    is Event.Message -> Row.Normal(event.message)
    Event.Empty -> Row.Empty
}
```

### Repeated checks against one value

When every condition classifies the same value, make it the subject:

```kotlin
// Before
return when {
    result is Result.Success -> Ui.Success(result.value)
    result is Result.Failure && result.canRetry -> Ui.Retry(result.error)
    result is Result.Failure -> Ui.Error(result.error)
    else -> Ui.Loading
}

// After
return when (result) {
    is Result.Success -> Ui.Success(result.value)
    is Result.Failure if result.canRetry -> Ui.Retry(result.error)
    is Result.Failure -> Ui.Error(result.error)
    Result.Loading -> Ui.Loading
}
```

### Null as one case among several

Use `when (value)` when null is one branch in a larger classification:

```kotlin
return when (val selected = selection) {
    null -> SelectionUi.None
    is Selection.Single if selected.item.isArchived -> SelectionUi.Archived(selected.item)
    is Selection.Single -> SelectionUi.Active(selected.item)
    is Selection.Multiple -> SelectionUi.Count(selected.items.size)
}
```

## Review checklist

Before finishing a control-flow change, verify:

- The code has one obvious subject, or intentionally has none.
- Guarded branches come before the matching unguarded branch.
- Comma-separated branches do not use guard conditions.
- Closed-domain `when` expressions remain exhaustive without unnecessary `else`.
- Open-domain fallbacks are still explicit.
- Smart casts still work without `as`, `!!`, or duplicated casts.
- The new shape is easier to scan than the old shape.

## When NOT to apply

- Do not introduce guard conditions if the project Kotlin version does not support them.
- Do not turn unrelated boolean checks into an awkward subject `when`.
- Do not remove a deliberate `else` for open-world external input.
- Do not flatten code if it makes cleanup, transaction boundaries, or error handling less obvious.

## Related

- [`kotlin-flow-state-event-modeling`](../kotlin-flow-state-event-modeling/SKILL.md) - flow state and event primitive choices.
- [`kotlin-multiplatform-expect-actual`](../kotlin-multiplatform-expect-actual/SKILL.md) - keeping business branching in common code and platform actuals thin.
