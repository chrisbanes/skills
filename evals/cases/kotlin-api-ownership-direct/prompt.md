Refactor the profile-loading API so repository behavior is placed on an accurate
semantic owner. Preserve behavior and keep the dependency visible to callers.
Retain the existing public `String.loadProfile` API as a deprecated forwarding
shim for source compatibility; it must delegate to the store-owned API rather
than perform repository access itself.
