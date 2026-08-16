# Skills

A set of skills for Kotlin, Jetpack Compose, and Android development.

## Install

With the [skills CLI](https://skills.sh):

```
npx skills add chrisbanes/skills
```

Or install as a Claude Code plugin:

```
/plugin marketplace add chrisbanes/skills
/plugin install chrisbanes-skills@chrisbanes-skills
```

Or install as a Codex plugin:

```
codex plugin marketplace add chrisbanes/skills --ref main
codex plugin add chrisbanes-skills@chrisbanes-skills
```

Or install as an OpenCode plugin:

```json
{
  "plugin": ["chrisbanes-skills@git+https://github.com/chrisbanes/skills.git"]
}
```

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md) for details.

## Skills

### Start here

- Working on Compose state or effects? Start with [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md), [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md), or [`compose-side-effects`](skills/compose-side-effects/SKILL.md).
- Investigating recomposition, stability, or jank? Start with [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md).
- Reviewing Flow or coroutine architecture? Start with [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) or [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md).

### Routing

- [`using-chrisbanes-skills`](skills/using-chrisbanes-skills/SKILL.md) — route Kotlin and Jetpack Compose work to the focused skills; current Claude Code versions also activate it when working with `.kt` or `.kts` files.

### Jetpack Compose

#### State and side effects

- [`compose-state-authoring`](skills/compose-state-authoring/SKILL.md) — author Compose local mutable state and read-only composable accessors correctly.
- [`compose-state-hoisting`](skills/compose-state-hoisting/SKILL.md) — decide whether Compose UI state belongs locally, in hoisted parameters, a plain state holder, or a screen state holder, and split screen wiring from previewable, state-driven UI.
- [`compose-side-effects`](skills/compose-side-effects/SKILL.md) — choose and key Compose effect APIs for event Flow collection, callbacks, cleanup, navigation, snackbar, analytics, and other side effects.

#### Performance

- [`compose-recomposition-performance`](skills/compose-recomposition-performance/SKILL.md) — route stability, deferred reads, and cross-phase back-writing.
- [`compose-stability-diagnostics`](skills/compose-stability-diagnostics/SKILL.md) — diagnose Compose compiler reports, strong skipping behavior, unstable parameters, and stability fixes.
- [`compose-state-deferred-reads`](skills/compose-state-deferred-reads/SKILL.md) — move frame-rate reads out of composition; avoid back-writing snapshot state across phases and cross-row measurement reads in composition.

#### UI API design and layout

- [`compose-modifier-and-layout-style`](skills/compose-modifier-and-layout-style/SKILL.md) — keep Compose layout APIs caller-placeable and modifier chains readable.
- [`compose-slot-api-pattern`](skills/compose-slot-api-pattern/SKILL.md) — design reusable Compose components whose variable visual regions are caller-provided slots.
- [`compose-animations`](skills/compose-animations/SKILL.md) — choose Compose animation APIs for visibility, value targets, coordinated transitions, and content swaps; align with official quick guide and decision tree.
- [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) — design and test keyboard, TV, D-pad, and focus-first Compose navigation behavior.

#### Testing

- [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) — choose between plain UI tests, semantics assertions, key/focus tests, interaction state tests with MutableInteractionSource, screenshot tests, and integration tests.

### Kotlin

- [`kotlin-coroutines-structured-concurrency`](skills/kotlin-coroutines-structured-concurrency/SKILL.md) — review coroutine scope ownership, init and fire-and-forget boundaries, cancellation handling, and blocking boundaries.
- [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) — write and review Kotlin branching with subject `when`, guard conditions, sealed exhaustiveness, smart casts, nullable branching, and early returns.
- [`kotlin-flow-state-event-modeling`](skills/kotlin-flow-state-event-modeling/SKILL.md) — model `StateFlow`, `SharedFlow`, `Channel`, `stateIn`, sharing policy, and one-shot events without lossy defaults.
- [`kotlin-functions`](skills/kotlin-functions/SKILL.md) - choose the correct owner for member, top-level, extension, factory, and service functions; avoid extensions on primitive and common types by default.
- [`kotlin-multiplatform-expect-actual`](skills/kotlin-multiplatform-expect-actual/SKILL.md) — design semantic expect/actual and interface boundaries for Kotlin Multiplatform platform interop.
- [`kotlin-types-value-class`](skills/kotlin-types-value-class/SKILL.md) — choose `@JvmInline value class` over data class for single-field domain types, including Compose stability implications.

### Workflows

- [`to-plan`](skills/to-plan/SKILL.md) — create a repository-aware implementation plan from one ready GitHub issue or a confirmed conversation specification, with a provider-neutral implementation handoff.
- [`run-github-project`](skills/run-github-project/SKILL.md) — set up or repair the repository's GitHub Project binding without running work, reconcile epics, surface resumable human checkpoints, triage unblocked Backlog work, and plan and execute authorized issues through one planning lane and a two-slot-by-default parallel pipeline. Requires `tdd` for implementation and preserves human Planning and triage approval gates.
- [`shepherd`](skills/shepherd/SKILL.md) — autonomously poll open PRs and MRs, triage review comments, detect and fix CI failures, and keep PRs moving forward.

## Contributing

Skills live at `skills/<skill-name>/SKILL.md`, flat (no language nesting). The `name:` in the SKILL.md frontmatter must match the directory name.

Frontmatter is validated against [`skills.schema.json`](skills.schema.json) — `name` and `description` are required, `name` must be kebab-case. The router also uses Claude Code's optional `paths` extension. Clients that do not support this extension must ignore the `paths` field rather than rejecting the skill.

### Releases

Release versions use SemVer-compatible CalVer: `YYYY.M.D` without zero-padded month or day values, for example `2026.6.17`.

Keep `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and new Git release tags on the same version. Existing zero-padded tags from before this policy map to the non-padded manifest version, so `2026.06.16` maps to `2026.6.16`. Only bump versions when publishing an installable release.

To publish a release, run the **Release** workflow from GitHub Actions. Leave the version input empty to use today's UTC `YYYY.M.D` version, or provide a specific non-zero-padded CalVer value. Use the dry-run option to validate without creating a commit, tag, or GitHub release.

Before pushing, lint skills (frontmatter schema + markdown):

```
npm install
npm run lint
```

This also runs on CI for all PRs.

## Evaluating Compose skills

The repository contains a Codex-first advisory evaluator for the 11 Compose
skills and their router. It compares a no-plugin baseline, explicit skill
invocation, and automatic activation across 38 synthetic and provenance-bearing
cases. Deterministic checks run in CI; authenticated model calls and their
scores never gate merges or releases.

Validate the harness and preview the full call matrix:

```shell
npm run evals:validate
python3 evals/run.py plan \
  --model gpt-5.6-sol --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high
```

See [`evals/README.md`](evals/README.md) for experiment controls, live execution,
score formulas, resumability, and human auditing.

## License

[Apache 2.0](LICENSE)
