# Kotlin value class vs data class

## Core principle

Prefer `@JvmInline value class` for a single-field domain distinction. Use a
data class for multiple fields or different equality.

## Review procedure

1. Find a single-property wrapper, primitive-heavy API, or `@Immutable` UI
   wrapper.
2. Keep the primitive or use a typealias unless the value is a real domain
   distinction.
3. Check equality, serialization, Java interop, and hot-path boxing.
4. Choose the type below, then compile and test. For a Compose performance
   change, re-check compiler or recomposition evidence. On contract drift, keep
   the existing type.

## Decision flow

| Situation | Prefer |
|---|---|
| Single field + domain-meaningful (`UserId`, `EmailAddress`, `Percentage`) | `@JvmInline value class` |
| Single field + no domain meaning (just grouping) | Type alias or keep the primitive |
| Multiple fields | Data class |
| Needs custom `equals`/`hashCode` beyond the wrapped value | Data class (value classes delegate to the underlying type) |
| Used as a generic type argument or nullable in a proven hot path | Data class or primitive |

```kotlin
// GOOD: domain-meaningful single field
@JvmInline value class UserId(val value: String)
@JvmInline value class EmailAddress(val value: String)
@JvmInline value class Percentage(val value: Float)

// BAD: data class wrapping a single domain field
data class UserId(val value: String)

// BAD: value class with no domain meaning
@JvmInline value class Wrapper(val value: String) // just use the String, or a type alias

// BAD: value class needing custom equality
@JvmInline value class CaseInsensitiveString(val value: String)
// value class equals delegates to String equals, which IS case-sensitive
// Use a data class if you need different equality semantics
```

For a Compose stability report, first confirm a stable underlying type. Prefer a
value class over an `@Immutable` wrapper used only for type distinction; never
change public serialization or API contracts merely to silence a report.

```kotlin
// Before: primitive value can be mixed up with other strings
data class UiState(val userId: String)

// After: domain type is stable at the Compose boundary
@JvmInline value class UserId(val value: String)
data class UiState(val userId: UserId)
```

## Contract checks

| Check | Action |
|---|---|
| JSON/API format matters | Verify serialization. `@Serializable data class A(val value: String)` encodes as an object; a value class encodes as the wrapped value. |
| Custom equality or hashing is required | Keep a data class. Value-class equality follows the wrapped value. |
| Callers use `copy()` or destructuring | Keep a data class or update callers deliberately. Value classes do not provide data-class conveniences. |
| Java or reflection-heavy framework boundary | Verify interop. Java callers see the underlying type; generic/`Any` use boxes. |
| Nullable/generic/vararg hot path | Measure before converting; those uses box. |
| Constructor body, `lateinit`, delegated properties, backing fields | Keep a data class or redesign; value classes only store the constructor value. |

## Packed values

Do not replace a clear multi-field data class with bit-packing unless profiling
shows hot-path allocation cost. If needed, Compose provides `packFloats`,
`packInts`, and matching `unpack*` functions:

```kotlin
@JvmInline value class Offset(val packedValue: Long)

fun Offset(x: Float, y: Float): Offset = Offset(packFloats(x, y))
val Offset.x: Float get() = unpackFloat1(packedValue)
val Offset.y: Float get() = unpackFloat2(packedValue)
```

## Do not apply

Use a data class for multiple fields or custom equality. Measure before changing
a nullable, generic, or vararg hot path. Keep a primitive/typealias when no
type distinction is needed, and do not silently change JSON, Java, reflection,
or framework behavior.

## Related

- [Compose performance](../../compose-performance/SKILL.md) — diagnose unstable Compose parameters; value classes are one fix
