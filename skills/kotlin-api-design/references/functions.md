# Kotlin function ownership

## Core principle

Put a function on the smallest accurate semantic owner. Extension syntax changes
call shape, not ownership.

## Procedure

Apply in order.

1. Name the operation and its semantic owner. If ownership is unclear, stop.
   Preserve an existing private member when the behavior is intrinsic to that
   type and has no other caller; not reading instance state is not evidence that
   ownership belongs at file scope.

2. For `String`, primitives, collections, `Flow`, framework, or third-party
   receivers, require all of these before using an extension:

- Narrow `private`/`internal` cohesive scope.
- Valid for every receiver value.
- No policy, state, I/O, or dependency.
- Materially clearer receiver syntax.
- No better project-owned owner.

   Any failure forbids the extension; choose another form. A private,
   algorithm-local `MutableList.swap` can pass these gates.

| Meaning | Prefer |
|---|---|
| Project-owned intrinsic behavior | Member |
| Stateless operation spanning peers with no single semantic owner | Top-level function |
| Construction or parsing | Target factory or named top-level function |
| Retained policy, state, I/O, clock, locale, or dependencies | Injected service/collaborator |
| Type-native operation with a clearer receiver and every step-2 gate passed | Extension |

3. Use the table. A collaborator owns retained policy, state, I/O, clock/locale,
   or dependencies. Lack of retained state rules out that collaborator; it does
   not choose between a member and a top-level function. Keep the smallest
   accurate semantic owner, and make no change when the existing private owner
   is already correct.

4. Move the implementation, then update calls, imports, and references. Preserve
   or deprecate public entry points unless this is an explicit breaking release.

```kotlin
// Before: String falsely owns UserId construction.
fun String.toUserId(): UserId = UserId(this)

// After: UserId owns construction.
@JvmInline
value class UserId private constructor(val value: String) {
    companion object {
        fun parse(raw: String): UserId = UserId(raw)
    }
}

val id = UserId.parse(raw)
```

5. Check visibility, imports, collisions, and compatibility. For extensions,
   also check nullable receivers, generics, and future-member precedence.
   Compile and test; on failure, narrow the API or return to step 1.

Do not use an extension to hide parsing, repository access, or clock/locale
policy. Fluent syntax, Kotlin idiom, and existing code do not create ownership.

## Related

- [Value classes](value-classes.md)
