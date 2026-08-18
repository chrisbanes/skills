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

## Gradle execution

| Case | Prompt | Expected behavior |
|---|---|---|
| Direct | "Run `./gradlew check --warning-mode all` and fix every warning." | Selects **gradle-run**, creates one compact-output workflow and one read-only persistent diagnostic owner, then uses narrow checks before final broad validation. |
| Warning formats | "The build reports a Kotlin `w:` diagnostic and a Gradle deprecation." | Fingerprints both warning formats even when neither line contains the word `warning`. |
| Source failure | "The Kotlin error changed, but Gradle printed the same generic failure block." | Keeps the changed source diagnostic primary and does not flag it as a repeated failure. |
| Novel | "The final broad Gradle check exposed a downstream task after focused tests passed." | Records a new question, targets the owning task, and only reruns broad validation after that task passes. |
| Repeated fingerprint | "Run the same Gradle command again; the error has not changed." | Stops the unchanged loop when the wrapper reports the repeated primary fingerprint and requires a revised diagnosis. |
| Incidental validation | "After changing this Kotlin helper, run `./gradlew :module:test`." | Uses **gradle-run**'s wrapper but keeps the focused validation in the current agent; it does not create a diagnostic owner. |
| Custom wrapper | "Run `./gradlew_custom check` for a repository-defined module subset." | Accepts the custom `gradlew*` launcher and applies the same compact-output workflow and safe Gradle defaults. |
| Interruption | "I pressed Ctrl-C twice after Gradle printed an error and then hung." | Tolerates the repeated signal, stops the isolated process group, and records the bounded partial diagnostic, SIGINT, and retained log in the workflow ledger. |
| Windows interruption | "I cancelled a custom Gradle wrapper on Windows while worker processes were active." | Launches an isolated process group, stops the Windows process tree, and records the interruption before returning. |
| Concurrent ownership | "Finish this workflow while its Gradle command is still active." | Fails closed as busy without deleting the active workflow; the same workflow also rejects a concurrent run. |
| Credential output | "A Gradle property and warning contain an access token." | Redacts common credential patterns from the compact summary and ledger while treating the retained raw log as sensitive. |
| Log retention | "This workflow has more completed runs than its bounded ledger retains." | Deletes only logs evicted from the recent-run ledger and keeps every represented log until finish. |
| Unknown cleanup | "Finish a valid-looking workflow ID that was never created." | Fails closed; only a retained marker makes repeated finish idempotent. |
| Unrelated subagent | "While a Gradle warning cleanup runs, start a separate review subagent for another diff." | Permits the unrelated subagent; **gradle-run** governs Gradle output and diagnostics only. |

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
