---
name: kotlin-api-design
description: Use when designing or reviewing Kotlin function ownership, member or extension functions, factories, single-field domain types, value classes, data classes, Kotlin Multiplatform expect/actual declarations, or platform service boundaries.
---

# Kotlin API design

## Core principle

Place behavior, types, and platform seams where their meaning is clearest to
callers; use the smallest public abstraction that preserves domain language and
platform independence.

## Procedure

1. Name the domain concept, its owning type or module, and the callers that
   need to depend on it.
2. Choose function ownership before adding an extension, factory, helper, or
   service layer.
3. When reviewing a public mapping over a sealed result, name every
   caller-visible outcome. Flag a catch-all `else` that hides a subtype and
   recommend explicit subtype branches so the contract stays exhaustive and
   preserves smart casts.
4. Represent a single-field domain concept with the smallest type that preserves
   its semantic and interop contract.
5. Keep shared code semantic; put native SDK and platform details behind an
   interface or a narrowly justified expect/actual boundary.
6. Read the focused reference for every material API decision below.
7. Finish when the public surface states domain intent, platform details remain
   at leaves, and callers do not depend on convenience abstractions with no
   clear owner.

## Topic router

| Signal | Read |
|---|---|
| Member vs top-level, extension, factory, service, or receiver choice | [Function ownership](references/functions.md) |
| Primitive obsession, one-field domain type, `@JvmInline value class`, data class, interop, or Compose stability | [Value classes](references/value-classes.md) |
| Source sets, platform services, native SDKs, files, sensors, permissions, Compose Multiplatform interop, or expect/actual | [Multiplatform boundaries](references/multiplatform-boundaries.md) |
| Branching, guard-condition shape, sealed-result mapping, or a catch-all `else` | [Kotlin control flow](../kotlin-control-flow/SKILL.md) |

## RED/GREEN agent scenarios

1. RED adds an extension on `String` to hide repository behavior. GREEN gives
   the behavior a domain owner or service with a meaningful dependency boundary.
2. Novel case: shared UI needs a platform permission service. GREEN preserves a
   semantic shared contract and places platform SDK calls at the native leaf.
3. Counterexample: an internal helper has one obvious owning class. GREEN keeps
   it a member instead of extracting a factory or value type for ceremony.
4. Routing case: a public `String` extension performs a repository lookup and
   a sealed result mapping collapses outcomes with `else`. GREEN gives the
   lookup a semantic owner and calls for explicit subtype branches that retain
   caller-visible distinctions.
