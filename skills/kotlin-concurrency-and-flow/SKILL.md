---
name: kotlin-concurrency-and-flow
description: Use when writing or reviewing Kotlin coroutine scope ownership, init launches, non-suspending launch APIs, runBlocking, cancellation, StateFlow, SharedFlow, Channel, stateIn, SharingStarted, state updates, or one-shot events.
---

# Kotlin concurrency and Flow

## Core principle

Give asynchronous work an explicit owner and lifetime, then model durable state
and transient events with primitives whose delivery and replay semantics match
the product contract.

## Procedure

1. Identify each coroutine owner, cancellation boundary, producer, consumer,
   durable state, and transient event.
2. Before changing an API, compare its existing caller-visible contract with
   the required owner and lifetime. If a suspend API already gives its caller
   cancellation, result, and failure ownership, finish with no change; do not
   add a scope, `launch`, callback, or deferred wrapper merely for convenience.
3. Select a scope whose lifecycle owns the work; do not retain arbitrary scopes
   or hide unstructured launches behind non-suspending APIs.
4. Model renderable, current data as state and imperative one-shot work as an
   event only when its loss and replay behavior are explicitly acceptable.
5. Choose Flow sharing and buffering semantics from the producer and consumer
   lifetimes rather than from a default.
6. Read the focused reference for the material concern below.
7. Finish when cancellation, restart, replay, and failure behavior are all
   observable from the public API and no caller must guess who owns the work.

## Topic router

| Signal | Read |
|---|---|
| Stored `CoroutineScope`, `init { launch }`, fire-and-forget API, `runBlocking`, broad catch, or cancellation boundary | [Structured concurrency](references/structured-concurrency.md) |
| `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, `SharingStarted`, `.value`, state updates, sentinel values, or one-shot events | [Flow state and events](references/flow-state-events.md) |
| Compose collection or UI effect handling | [Compose state and effects](../compose-state-and-effects/SKILL.md) |
