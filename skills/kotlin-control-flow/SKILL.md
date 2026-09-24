---
name: kotlin-control-flow
description: "Use when writing or reviewing Kotlin branching and control flow: when expressions, guard conditions, sealed type exhaustiveness, smart casts, nullable branching, early returns, or replacing complex if/else chains."
---

# Kotlin control flow

## Core principle

Make the classified value obvious, keep branch-local predicates on their
branch, and let the compiler prove closed-domain coverage.

## Procedure

1. Name the value being classified. If every branch tests it, use
   `when (subject)`; otherwise keep a subjectless `when` or `if` chain.
2. Choose the branch shape:

   | Code shape | Prefer |
   |---|---|
   | One classified value | `when (subject)` |
   | Unrelated boolean conditions | Subjectless `when` or `if`/`else` |
   | Primary case plus a branch-local predicate | Guard condition |
   | Invalid input before the main path | Early return, `require`, or `check` |
   | Closed value-returning domain | Exhaustive `when` expression |
   | Open input or deliberate fallback | Explicit `else` |

3. Use a guard only on a subject `when`, after a primary condition, when the
   extra predicate belongs to that branch and an unguarded branch still handles
   the primary condition. Put the guarded branch first. Split comma-separated
   conditions instead of guarding one of them.
4. For a closed enum, Boolean, sealed type, or nullable closed type, name every
   case and omit `else`. Match objects by value and class/data-class subtypes
   with `is`. When a data-bearing sealed case is collapsed by a catch-all, show
   the branch-level use in the review:

   ```kotlin
   is Outcome.Failed -> safeFailureLabel(outcome.reason)
   ```

   The `is` check smart-casts `outcome`, so the branch can use `reason` without
   a cast. The helper name is illustrative; choose a safe mapping for the
   caller contract. Do not replace this branch-level explanation with a note
   that unspecified callers can inspect the original result. If the input is
   an open server/platform value or needs real fallback/logging, keep `else`.
5. Use an early return only when it removes invalid or nullable state from the
   main path. Keep nesting that expresses cleanup, transaction, or error
   handling.
6. Verify smart casts still work without `as`, `!!`, mutable temporaries, or
   duplicate casts. If they do not, keep the original shape or take a smaller
   refactor.
7. Compile and test. On failure, return to the smallest applicable earlier step
   or retain the prior shape. In a review of a closed sealed mapping, when a
   data-bearing subtype affects the mapping or its safe handling, put the typed
   branch and member access in the finding itself, not only in analysis or as a
   general note to add explicit cases. Use this pseudocode template with the
   actual subtype and payload member substituted:

   ```kotlin
   is <DataSubtype> -> map(result.<payload>)
   ```

   This is a template, not literal Kotlin: the `is` test smart-casts `result`,
   and the member access shows how the branch uses its payload. If the public
   value stays generic, state how the branch handles the detail or why it is
   deliberately discarded. Naming cases alone or sending callers to inspect the
   original value is not complete branch guidance. Apply this only to closed,
   data-bearing cases; retain `else` for open-world values or real fallbacks.
   Finish when the subject, fallbacks, and relevant branch data are obvious to a
   reader and the resulting shape is easier to scan.

## Recipes

Use guarded branches to refine one case, rather than nesting an `if`:

```kotlin
return when (event) {
    is Event.Message if event.isUnread -> Row.Highlighted(event.message)
    is Event.Message -> Row.Normal(event.message)
    Event.Empty -> Row.Empty
}
```

Use a subject `when` when repeated conditions classify one value, and include
`null` as a branch when it is one case in a larger classification:

```kotlin
return when (val selected = selection) {
    null -> SelectionUi.None
    is Selection.Single if selected.item.isArchived -> SelectionUi.Archived(selected.item)
    is Selection.Single -> SelectionUi.Active(selected.item)
    is Selection.Multiple -> SelectionUi.Count(selected.items.size)
}
```

Do not introduce guards on unsupported Kotlin versions, force unrelated boolean
checks into a subject `when`, remove an open-world fallback, or flatten code
that obscures cleanup, transactions, or errors.

## Related

- [Kotlin concurrency and Flow](../kotlin-concurrency-and-flow/SKILL.md) — state/event primitives.
- [Kotlin API design](../kotlin-api-design/SKILL.md) — explicit common-code branching.
