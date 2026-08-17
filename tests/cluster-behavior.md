# Cluster behavior evaluation

This matrix tests the repository's public agent-facing seam:

> task prompt → selected skill entrypoint and focused references → material
> decisions, safeguards, exceptions, and finish gate

Run every case in a clean agent context with the installed skill set. A case
passes when the selected entrypoint, required reference routing, and expected
behavior all match. Do not require wording or example-level equivalence.

## Manual evaluation procedure

1. Record the candidate commit, client and model, and the client-specific
   command or link used to install this worktree as the active skill set.
2. Start a fresh context for each case, provide only the prompt in the matrix,
   and let normal skill discovery run.
3. Record the selected entrypoint, every loaded reference, the material advice,
   and PASS or FAIL. For a failure, name the missing safeguard or extra route.
4. Apply one correction, reinstall the same candidate, and rerun the affected
   case in another fresh context.

Use this result shape in the implementation issue or pull request:

| Commit | Client/model | Case | Entrypoint | References | Result | Notes |
|---|---|---|---|---|---|---|
| `<sha>` | `<client/model>` | `<section: case>` | `<skill>` | `<paths>` | PASS/FAIL | `<missing safeguard or extra route>` |

## Global routing

| Case | Prompt | Expected behavior |
|---|---|---|
| Broad screen | "Review this Compose screen: it collects state, shows a snackbar, and owns most layout." | Selects **compose-state-and-effects**; routes to state hoisting and side effects. |
| Mixed concern | "This reusable card has an animated height and hardcodes fillMaxWidth." | Selects **compose-component-design** and **compose-animations**; does not load state guidance by default. |
| Narrow Kotlin | "Replace this nested if with guard conditions." | Selects **kotlin-control-flow** only. |

## Compose state and effects

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "A composable uses LaunchedEffect(Unit) to collect events for a changing user ID." | Requires an effect key that follows the user ID unless the lifecycle deliberately stays stable. |
| Effect only | "A long-lived Compose effect calls a callback that can change after recomposition." | Routes to the side-effects reference and uses `rememberUpdatedState` only when the effect should not restart. |
| Novel | "A search query drives repository suggestions while list and focus runtime objects coordinate the UI." | Keeps query and suggestions with screen state; keeps Compose runtime objects in plain UI state. |
| Counterexample | "Add a private expansion Boolean to a one-off badge." | Keeps simple state local; does not introduce a state holder or effect. |

## Compose performance

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "Unchanged lazy rows recompose when focus moves." | Checks cross-phase back-writing before prescribing stability wrappers. |
| Novel | "A scroll-driven animation value only affects drawing." | Defers the State read to draw or layout rather than passing it through composition. |
| Counterexample | "The displayed model changed and its row recomposed." | Does not suppress legitimate recomposition with caches or stability ceremony. |

## Compose component design

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "This reusable row takes a title, icon, Boolean flags, and a trailing action." | Replaces caller-controlled visual variants with appropriate slots and preserves caller placement with a root modifier. |
| Novel | "A component needs caller-supplied trailing content and a root modifier." | Applies the modifier at the root without leaking internal layout. |
| Counterexample | "A private helper has one fixed child and no reuse." | Avoids speculative slots and public API ceremony. |

## Kotlin concurrency and Flow

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "A service stores a CoroutineScope and launches from non-suspending methods." | Requires an explicit lifecycle owner and cancellation boundary. |
| Novel | "A screen needs replayable loading state and non-replayable navigation." | Separates state and event contracts, including delivery and replay behavior. |
| Counterexample | "A suspend function is called from an existing caller-owned scope." | Does not create an internal scope just to make the API look asynchronous. |

## Kotlin API design

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "Add a String extension that fetches a repository record." | Places repository behavior behind a domain owner or service rather than a primitive extension. |
| Novel | "Shared UI needs a platform permission service." | Preserves a semantic shared contract and puts native SDK work at the platform leaf. |
| Counterexample | "A helper belongs only to one class." | Keeps it a member instead of introducing a factory or value type for ceremony. |

## Release gate

Before publishing the breaking taxonomy:

1. Run this full matrix.
2. Record every failure, selected entrypoint, missing safeguard, and correction.
3. Re-run affected cases after each correction.
4. Publish only when every case passes and npm run lint, release validation,
   and the repository's existing test suite are green.
