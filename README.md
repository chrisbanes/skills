![Abstract illustration of a modular Kotlin and Jetpack Compose toolkit](docs/assets/skills-header.webp)

# Skills

A set of skills for Kotlin, Jetpack Compose, Android development, and grounded
writing.

The repository is also a portable [Agent Plugins](https://agent-plugins.org/)
v1.0.0 package. Conforming clients discover the root [`plugin.json`](plugin.json)
and the immediate skill directories under [`skills/`](skills/).

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

- [`using-chrisbanes-skills`](skills/using-chrisbanes-skills/SKILL.md) — route Kotlin and Jetpack Compose work to the focused skills.

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

- [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) — review coroutine, raw `Thread`, and `Executor` ownership, cancellation, Flow state/event modeling, sharing, replay, and one-shot delivery.
- [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) — write and review Kotlin branching with subject `when`, guard conditions, sealed exhaustiveness, smart casts, nullable branching, and early returns.
- [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) — choose function owners, semantic domain types, and Kotlin Multiplatform platform boundaries.

### Writing

- [`grounded-writing`](skills/grounded-writing/SKILL.md) — draft or revise clear, evidence-led writing of any length, including review comments and replies, without inventing personal claims.

### Workflows

- [`gradle-run`](skills/gradle-run/SKILL.md) — run every agent-initiated Gradle command through a compact-output wrapper; Gradle-centered workflows use one read-only diagnostic owner while parents retain edits.
- [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) — implement or review supplied-task orchestration through separate implementation owners, preserving atomic work, task-scoped acceptance, repair ownership, and the installed `implement` dependency.
- [`to-plan`](skills/to-plan/SKILL.md) — create a repository-aware implementation plan from one ready GitHub issue or an in-chat task, with a provider-neutral implementation handoff.
- [`run-github-project`](skills/run-github-project/SKILL.md) — set up, review, or operate the repository's GitHub Project workflow; preserve live authority, human Planning work, unknown outcomes, epics, checkpoints, triage, and authorized execution boundaries.
- [`shepherd`](skills/shepherd/SKILL.md) — autonomously poll open PRs and MRs, triage review comments, and switch CI failures into a full local verification-and-repair cycle.

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

Frontmatter is validated against [`skills.schema.json`](skills.schema.json), which
tracks the core [Agent Skills specification](https://agentskills.io/specification)
and permits `disable-model-invocation` for Claude Code compatibility.
`name` and `description` are required; portable optional fields are `license`,
`compatibility`, `metadata`, and `allowed-tools`. Explicit-only workflow skills
also mirror that policy in Codex's `agents/openai.yaml`.

### Releases

Release versions use SemVer-compatible CalVer: `YYYY.M.D` without zero-padded month or day values, for example `2026.6.17`.

Keep root `plugin.json`, `.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json`, and new Git release tags on the same version.
Existing zero-padded tags from before this policy map to the non-padded manifest
version, so `2026.06.16` maps to `2026.6.16`. Only bump versions when publishing
an installable release.

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
forced-skill, and automatic-routing runs. **Baseline** and **automatic** use
the cases eligible for automatic activation; **restraint** checks that a skill
does not make an unnecessary change. Scorecards also compare subject-side tokens,
tool calls, completed turns, elapsed time, and total attempted work per
successful outcome. The
table reports the latest available result for each skill and correctness metric.
These scores were produced using
[`gpt-5.6-terra`](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
with medium reasoning, judged by
[`gpt-5.6-sol`](https://developers.openai.com/api/docs/models/gpt-5.6-sol) with
high reasoning. Results are model- and reasoning-specific; other configurations
may perform differently. These are not merge or release gates. See
[`evals/README.md`](evals/README.md) for evaluation setup and reproducibility.

| Skill | Baseline | Automatic | Restraint |
| --- | ---: | ---: | ---: |
| [`compose-animations`](skills/compose-animations/SKILL.md) | 75.0% | 100.0% | 100.0% |
| [`compose-component-design`](skills/compose-component-design/SKILL.md) | 86.7% | 100.0% | 100.0% |
| [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) | 66.7% | 100.0% | 100.0% |
| [`compose-performance`](skills/compose-performance/SKILL.md) | 91.7% | 100.0% | 100.0% |
| [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) | 77.8% | 100.0% | 100.0% |
| [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) | 55.6% | 100.0% | 100.0% |
| [`gradle-run`](skills/gradle-run/SKILL.md) | 33.3% | 100.0% | 100.0% |
| [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) | 66.7% | 100.0% | 100.0% |
| [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) | 33.3% | 100.0% | 100.0% |
| [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) | 27.8% | 100.0% | 100.0% |
| [`grounded-writing`](skills/grounded-writing/SKILL.md) | — | 100.0% | 100.0% |
| [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) | — | — | 100.0% |
| [`run-github-project`](skills/run-github-project/SKILL.md) | — | — | 100.0% |
| [`shepherd`](skills/shepherd/SKILL.md) | — | — | 100.0% |
| [`to-plan`](skills/to-plan/SKILL.md) | — | — | — |

### Skill efficiency

Values are per-run medians, baseline → automatic, followed by the automatic
percentage change. These subject-only measurements use the latest complete,
same-run evidence available for each suite and include failed runs and negative
controls. Baseline-to-automatic efficiency comparisons use only cases eligible
for automatic activation. Multi-skill scenarios contribute to every targeted
skill row. A turn is one completed Codex turn; time remains environment-sensitive.
The source runs, selection rules, and detailed scorecards are in the
[evaluation change record](evals/artifacts/2026-08-27-skill-eval-efficiency.md).

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| [`compose-animations`](skills/compose-animations/SKILL.md) | 41.7k → 81.9k (+96%) | 2 → 5 (+150%) | 1 → 1 (+0%) | 26.3s → 42.3s (+60%) |
| [`compose-component-design`](skills/compose-component-design/SKILL.md) | 56.3k → 66.9k (+19%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 32.6s → 29.1s (-11%) |
| [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) | 56.2k → 77.1k (+37%) | 3 → 6 (+100%) | 1 → 1 (+0%) | 32.4s → 44.1s (+36%) |
| [`compose-performance`](skills/compose-performance/SKILL.md) | 56.2k → 83.0k (+48%) | 3 → 4 (+33%) | 1 → 1 (+0%) | 32.5s → 40.1s (+24%) |
| [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) | 56.2k → 83.3k (+48%) | 3 → 5 (+67%) | 1 → 1 (+0%) | 28.5s → 41.6s (+46%) |
| [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) | 56.7k → 69.0k (+22%) | 3 → 4 (+33%) | 1 → 1 (+0%) | 32.9s → 34.1s (+4%) |
| [`gradle-run`](skills/gradle-run/SKILL.md) | 70.7k → 83.3k (+18%) | 4 → 3 (-25%) | 1 → 1 (+0%) | 30.2s → 32.9s (+9%) |
| [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) | 57.4k → 145.8k (+154%) | 3 → 7 (+133%) | 1 → 1 (+0%) | 30.0s → 53.0s (+77%) |
| [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) | 72.7k → 119.2k (+64%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 46.0s → 64.2s (+40%) |
| [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) | 71.8k → 109.6k (+53%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 39.1s → 53.7s (+37%) |
| [`grounded-writing`](skills/grounded-writing/SKILL.md) | 41.3k → 65.4k (+59%) | 2 → 3 (+50%) | 1 → 1 (+0%) | 16.2s → 26.9s (+66%) |

## License

[Apache 2.0](LICENSE)
