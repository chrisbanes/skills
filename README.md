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

### External skill providers

Most skills in this repository are self-contained. The workflows below compose
with skills from other repositories; installing `chrisbanes/skills` does not
install them, and the workflows never install them implicitly.

| Consumer | Requirement | Provider | Source and install |
|---|---|---|---|
| [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) implementation mode | — | not met | 66.7% |
| [`run-github-project`](skills/run-github-project/SKILL.md) execution lane | — | not met | 100.0% |
| `run-github-project` Backlog triage | — | not met | 100.0% |
| `run-github-project` Wayfinder lane | — | not met | 100.0% |
| `run-github-project` correctness review | — | not met | 100.0% |
| `run-github-project` reuse and clarity review | — | not met | 100.0% |
| `run-github-project` over-engineering review | — | not met | 100.0% |

Review mode in `implement-with-subagents`, and review or setup mode in
`run-github-project`, do not require these external skills. See the
[`run-github-project` provider matrix](skills/run-github-project/references/workflow-providers.md)
for its lane-specific fallback and blocking behavior.

## Skills

### Start here

- Working on Compose state or effects? Start with [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md).
- Investigating recomposition, stability, or jank? Start with [`compose-performance`](skills/compose-performance/SKILL.md).
- Comparing Android benchmark configurations or a measured Android default? Start with [`android-benchmark-comparison`](skills/android-benchmark-comparison/SKILL.md).
- Reviewing Flow or coroutine architecture? Start with [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md).

### Routing

- [`using-chrisbanes-skills`](skills/using-chrisbanes-skills/SKILL.md) — route Kotlin and Jetpack Compose work to focused skills, adding a second only for an independent decision in the same change.

### Benchmarking

- [`android-benchmark-comparison`](skills/android-benchmark-comparison/SKILL.md) — compare physical Android benchmark configurations with verified coverage, controlled conditions, trace-backed diagnosis of unstable rankings, and bounded conclusions.

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

- [`grounded-writing`](skills/grounded-writing/SKILL.md) — draft or review public developer documentation and other user-owned text, including internal report reviews, while preserving evidence, format, and material-edit restraint.

### Workflows

- [`release-kotlin-library`](skills/release-kotlin-library/SKILL.md) — assess readiness, prepare, and verify Kotlin library releases; check the `gradle-maven-publish-plugin` prerequisite, reconcile changelogs and Metalava API snapshots, and follow repository checks and publication gates.
- [`gradle-run`](skills/gradle-run/SKILL.md) — run every agent-initiated Gradle command through a compact-output wrapper; Gradle-centered workflows use one read-only diagnostic owner while parents retain edits.
- [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) — validate task dependencies, dispatch only safe ready work concurrently in isolated worktrees, integrate accepted commits in dependency order, and recheck affected evidence at the integrated head; preserves serial fallback, repair ownership, review mode, and the external `implement` prerequisite.
- [`to-plan`](skills/to-plan/SKILL.md) — turn one ready GitHub issue or an in-chat task into a repository-grounded, executor-ready recipe with stable task IDs, explicit acyclic dependencies, safe parallelism notes, concrete tests, and bounded repair rules.
- [`run-github-project`](skills/run-github-project/SKILL.md) — set up, review, or operate the repository's GitHub Project workflow; preserve live authority, human Planning work, unknown outcomes, epics, checkpoints, triage, and authorized execution boundaries, with mode-specific external providers disclosed above.
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

Release versions use CalVer: `YYYY.M.D`, `YYYY.M.D.N`, or `YYYY.M.D.NN`, without
zero-padded month or day values. For example, use `2026.6.17` for the first
release of the day and `2026.6.17.1` or `2026.6.17.01` for another release.
Single-digit daily release numbers are normalized to the padded form, so both
inputs produce `2026.6.17.01`.

Keep root `plugin.json`, `.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json`, and new Git release tags on the same version.
Existing zero-padded tags from before this policy map to the non-padded manifest
version, so `2026.06.16` maps to `2026.6.16`. Only bump versions when publishing
an installable release.

To publish a release, run the **Release** workflow from GitHub Actions. Leave the
version input empty to use today's UTC `YYYY.M.D` version, or provide a specific
CalVer value, optionally with a one- or two-digit daily release number. Use the
dry-run option to validate without creating a commit, tag, or GitHub release.

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
[`gpt-6-luna`](https://developers.openai.com/api/docs/models/gpt-6-luna)
with high reasoning, judged by
[`gpt-6-sol`](https://developers.openai.com/api/docs/models/gpt-6-sol) with
high reasoning. Results are model- and reasoning-specific; other configurations
may perform differently. The human audit queue remains open. These are not merge
or release gates. See
[`evals/README.md`](evals/README.md) for evaluation setup and reproducibility.

Skill-revision compatibility checks compare old and revised instructions within
each model, separately from these benchmark scores. See the
[workflow compatibility record](evals/artifacts/2026-09-06-workflow-model-compatibility.md)
for Astra and 5.6 coverage and its current evidence limits.

| Skill | Baseline | Automatic | Restraint |
| --- | ---: | ---: | ---: |
| [`compose-animations`](skills/compose-animations/SKILL.md) | 75.0% | 100.0% | 100.0% |
| [`compose-component-design`](skills/compose-component-design/SKILL.md) | 86.7% | 100.0% | 100.0% |
| [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) | 33.3% | 100.0% | 100.0% |
| [`compose-performance`](skills/compose-performance/SKILL.md) | 83.3% | 100.0% | 100.0% |
| [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) | 83.3% | 95.8% | 100.0% |
| [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) | 55.6% | 100.0% | 100.0% |
| [`gradle-run`](skills/gradle-run/SKILL.md) | 41.7% | 91.7% | 100.0% |
| [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) | 58.3% | 66.7% | 100.0% |
| [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) | 44.4% | 88.9% | 100.0% |
| [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) | 33.3% | 72.2% | 100.0% |
| [`android-benchmark-comparison`](skills/android-benchmark-comparison/SKILL.md) | 33.3% | 50.0% | 100.0% |
| [`grounded-writing`](skills/grounded-writing/SKILL.md) | 0.0% | 100.0% | 100.0% |
| [`implement-with-subagents`](skills/implement-with-subagents/SKILL.md) | — | — | 100.0% |
| [`release-kotlin-library`](skills/release-kotlin-library/SKILL.md) | 0.0% | 100.0% | 100.0% |
| [`run-github-project`](skills/run-github-project/SKILL.md) | — | — | 100.0% |
| [`shepherd`](skills/shepherd/SKILL.md) | — | — | 100.0% |
| [`to-plan`](skills/to-plan/SKILL.md) | — | — | 100.0% |

The `compose-ui-testing-patterns`, `grounded-writing`, and
`release-kotlin-library` automatic cells, and the `to-plan` restraint cell,
use later focused evidence. Baseline and efficiency values use the complete
suite. See
the [improvement result record](evals/artifacts/2026-09-24-gpt6-improvement-results.md)
and [targeted probe record](evals/artifacts/2026-09-24-gpt6-targeted-100-probes.md)
for provenance and remaining failures.

### Skill efficiency

Values are per-run medians, baseline → automatic, followed by the automatic
percentage change. These subject-only measurements use the latest complete,
same-run evidence available for each suite and include failed runs and negative
controls. Baseline-to-automatic efficiency comparisons use only cases eligible
for automatic activation. Multi-skill scenarios contribute to every targeted
skill row. A turn is one completed Codex turn; time remains environment-sensitive.
Run provenance and local scorecard paths are in the
[GPT-6 improvement result record](evals/artifacts/2026-09-24-gpt6-improvement-results.md).

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| [`compose-animations`](skills/compose-animations/SKILL.md) | 58.6k → 85.4k (+46%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 28.2s → 34.8s (+23%) |
| [`compose-component-design`](skills/compose-component-design/SKILL.md) | 48.7k → 73.4k (+51%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 24.4s → 29.5s (+21%) |
| [`compose-focus-navigation`](skills/compose-focus-navigation/SKILL.md) | 59.1k → 84.9k (+44%) | 5 → 5 (+0%) | 1 → 1 (+0%) | 28.9s → 36.6s (+27%) |
| [`compose-performance`](skills/compose-performance/SKILL.md) | 49.1k → 85.0k (+73%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 26.4s → 31.8s (+21%) |
| [`compose-state-and-effects`](skills/compose-state-and-effects/SKILL.md) | 60.1k → 89.0k (+48%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 28.2s → 37.8s (+34%) |
| [`compose-ui-testing-patterns`](skills/compose-ui-testing-patterns/SKILL.md) | 60.2k → 84.2k (+40%) | 5.5 → 5 (-9%) | 1 → 1 (+0%) | 27.1s → 26.8s (-1%) |
| [`gradle-run`](skills/gradle-run/SKILL.md) | 59.8k → 104.3k (+75%) | 4 → 7 (+75%) | 1 → 1 (+0%) | 27.6s → 45.3s (+64%) |
| [`kotlin-api-design`](skills/kotlin-api-design/SKILL.md) | 60.1k → 83.9k (+40%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 32.8s → 38.8s (+18%) |
| [`kotlin-concurrency-and-flow`](skills/kotlin-concurrency-and-flow/SKILL.md) | 60.0k → 74.0k (+23%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 26.5s → 28.0s (+6%) |
| [`kotlin-control-flow`](skills/kotlin-control-flow/SKILL.md) | 60.9k → 83.9k (+38%) | 5 → 5 (+0%) | 1 → 1 (+0%) | 26.2s → 38.5s (+47%) |
| [`android-benchmark-comparison`](skills/android-benchmark-comparison/SKILL.md) | 46.9k → 53.8k (+15%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 23.2s → 35.0s (+51%) |
| [`grounded-writing`](skills/grounded-writing/SKILL.md) | 35.6k → 56.9k (+60%) | 2 → 4 (+100%) | 1 → 1 (+0%) | 23.2s → 22.1s (-5%) |
| [`release-kotlin-library`](skills/release-kotlin-library/SKILL.md) | 70.2k → 88.3k (+26%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 42.1s → 43.9s (+4%) |

## License

[Apache 2.0](LICENSE)
