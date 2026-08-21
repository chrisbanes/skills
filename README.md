![Abstract illustration of a modular Kotlin and Jetpack Compose toolkit](docs/assets/skills-header.webp)

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

- Working on Compose state or effects? Start with [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md).
- Investigating recomposition, stability, or jank? Start with [`compose-performance`](skills/compose-performance/SKILL.md).
- Reviewing Flow or coroutine architecture? Start with [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md).

### Routing

- [`using-chrisbanes-skills`](skills/using-chrisbanes-skills/SKILL.md) — route Kotlin and Jetpack Compose work to the focused skills; current Claude Code versions also activate it when working with `.kt` or `.kts` files.

### Jetpack Compose

#### State and side effects

- [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) — decide state ownership and effect lifecycle for local UI state, screen state holders, Flow collection, callbacks, cleanup, navigation, snackbar, analytics, and focus requests.

#### Performance

- [`compose-performance`](skills/compose-performance/SKILL.md) — diagnose stability, deferred reads, composition contracts, and cross-phase back-writing from concrete runtime evidence.

#### UI API design and layout

- [`compose-component-design`](skills/compose-component-design/SKILL.md) — design caller-placeable Compose APIs whose variable visual regions are caller-provided slots.
- [`compose-animations`](skills/compose-animations/SKILL.md) — choose Compose animation APIs for visibility, value targets, coordinated transitions, and content swaps; align with official quick guide and decision tree.
- [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) — design and test keyboard, TV, D-pad, and focus-first Compose navigation behavior.

#### Testing

- [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) — choose between plain UI tests, semantics assertions, key/focus tests, interaction state tests with MutableInteractionSource, screenshot tests, and integration tests.

### Kotlin

- [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) — review coroutine ownership, cancellation, Flow state/event modeling, sharing, replay, and one-shot delivery.
- [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) — write and review Kotlin branching with subject `when`, guard conditions, sealed exhaustiveness, smart casts, nullable branching, and early returns.
- [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) — choose function owners, semantic domain types, and Kotlin Multiplatform platform boundaries.

### Workflows

- [`gradle-run`](skills/gradle-run/SKILL.md) — run every agent-initiated Gradle command through a compact-output wrapper; Gradle-centered workflows use one read-only diagnostic owner while parents retain edits.
- [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) — implement supplied tickets or plan tasks sequentially through separate implementation subagents, requiring the installed `implement` skill and prohibiting controller fallback.
- [`to-plan`](skills/to-plan/SKILL.md) — create a repository-aware implementation plan from one ready GitHub issue or an in-chat task, with a provider-neutral implementation handoff.
- [`run-github-project`](skills/run-github-project/SKILL.md) — set up or repair the repository's GitHub Project binding without running work, reconcile epics, surface resumable human checkpoints, triage unblocked Backlog work, and plan and execute authorized issues through one planning lane and a two-slot-by-default parallel pipeline. Optionally routes authorized Wayfinder decision tickets through that planning lane while preserving their map and HITL gates. Requires `tdd` for implementation and preserves human Planning and triage approval gates.
- [`shepherd`](skills/shepherd/SKILL.md) — autonomously poll open PRs and MRs, triage review comments, detect and fix CI failures, and keep PRs moving forward.

### Migration from pre-cluster skills

This is a breaking taxonomy change. Replace the removed entrypoints as follows:

| Removed skills | Replacement |
|---|---|
| `compose-state-authoring`, `compose-state-hoisting`, `compose-side-effects` | [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) |
| `compose-recomposition-performance`, `compose-stability-diagnostics`, `compose-state-deferred-reads` | [`compose-performance`](skills/compose-performance/SKILL.md) |
| `compose-modifier-and-layout-style`, `compose-slot-api-pattern` | [`compose-component-design`](skills/compose-component-design/SKILL.md) |
| `kotlin-coroutines-structured-concurrency`, `kotlin-flow-state-event-modeling` | [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) |
| `kotlin-functions`, `kotlin-types-value-class`, `kotlin-multiplatform-expect-actual` | [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) |

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

For a taxonomy change, also run the durable
[cluster behavior evaluation](tests/cluster-behavior.md). It checks routing,
required references, safeguards, exceptions, and finish gates at the public
agent-facing seam.

## Evaluating skills

The advisory evaluator tests concrete scenarios modelled on real-world coding
work, with expected outcomes and no-change controls. It compares no-skill,
forced-skill, and automatic-routing runs. **Baseline** is the no-skill result,
**automatic** is the headline result, and **restraint** checks that a skill does
not make an unnecessary change. The table reports complete-scenario-suite
results. Focused repair rechecks remain separate so they do not replace a
full-suite measurement. These are not merge or release gates. See
[`evals/README.md`](evals/README.md) for evaluation setup and reproducibility.

| Skill | Baseline | Automatic (full suite) | Restraint (full suite) |
| --- | ---: | ---: | ---: |
| [`compose-animations`](skills/compose-animations/SKILL.md) | 75.0% | 100.0% | 100.0% |
| [`compose-component-design`](skills/compose-component-design/SKILL.md) | 86.7% | 100.0% | 100.0% |
| [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) | 66.7% | 100.0% | 100.0% |
| [`compose-performance`](skills/compose-performance/SKILL.md) | 91.7% | 100.0% | 100.0% |
| [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) | 77.8% | 100.0% | 100.0% |
| [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) | 55.6% | 100.0% | 100.0% |
| [`gradle-run`](skills/gradle-run/SKILL.md) | 33.3% | 75.0% | 100.0% |
| [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) | 66.7% | 91.7% | 100.0% |
| [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) | 33.3% | 100.0% | 66.7% |
| [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) | 27.8% | 77.8% | 100.0% |

## License

[Apache 2.0](LICENSE)
