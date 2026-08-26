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
   with `is`; retain the smart-cast payload when the mapping needs it. If the
   input is an open server/platform value or needs real fallback/logging, keep
   `else`.
5. Use an early return only when it removes invalid or nullable state from the
   main path. Keep nesting that expresses cleanup, transaction, or error
   handling.
6. Verify smart casts still work without `as`, `!!`, mutable temporaries, or
   duplicate casts. If they do not, keep the original shape or take a smaller
   refactor.
7. Compile and test. On failure, return to the smallest applicable earlier step
   or retain the prior shape. Finish when the subject, fallbacks, and branch
   data are obvious to a reader and the resulting shape is easier to scan.

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
