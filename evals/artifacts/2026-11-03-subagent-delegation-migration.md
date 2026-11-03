# Subagent delegation migration

The source was the local `~/.codex/AGENTS.md`, SHA-256
`b97a406434b047f93c409350bdd552b7666a5fc97a49f3ec64401e26b7b1a182`. All eight Codex assignment/model/effort rows were
preserved exactly in `skills/subagent-delegation/references/codex.md`.
The user subsequently requested removal of the custom Codex agent definitions.
The installed checker and investigator TOMLs and their bundled preview copies
were removed. Built-in roles remain available; the skill now uses exposed roles
and explicit briefs without requiring custom definitions. The direct Codex
case covers that configuration, while the novel case retains synthetic
custom-pin coverage for machines that choose to define their own agents.

## Confirmed design

The user subsequently selected a provider-neutral core with separate Codex and
Claude Code references, explicit invocation covering the current task, and an
explicit Claude routing table. They confirmed the complete design before edits.
The approved Claude defaults use Haiku/low for mechanical work, Sonnet/medium
for visual work, Sonnet/low for concise supplied-material drafting,
Sonnet/medium for ordinary implementation, Sonnet/high for constrained synthesis,
Opus/medium for ambiguous judgment, Opus/high for difficult correctness work,
and Opus/xhigh for conflicting evidence or demanding polish. Fable and max are
justified exceptions. This is policy, not measured cross-provider equivalence.

Claude runtime guidance was checked against the installed 2.1.317 CLI and
[official subagent documentation](https://code.claude.com/docs/en/sub-agents),
[model configuration](https://code.claude.com/docs/en/model-config), and
[skill invocation controls](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill).
Shared Claude nested-result guidance now distinguishes interactive waiting
from headless non-fork background delivery. Existing synthetic nested-result
cases explicitly state their headless runtime. Implementation orchestration
and acceptance gates were preserved.

## Local plugin verification

Using Codex CLI 0.166.0, the skill directory was staged into the existing enabled
`chrisbanes-skills` plugin cache as an unpublished local preview. No manifest
versions or marketplace configuration changed.

The app-server `skills/list` API with `forceReload: true` returned
`chrisbanes-skills:subagent-delegation`, plugin ID
`chrisbanes-skills@chrisbanes-skills`, enabled, with no loading errors.
The app-server `fs/readFile` API loaded the returned entrypoint, both provider
references, and `agents/openai.yaml`; all matched the repository byte-for-byte.
The entrypoint SHA-256 was
`192cf5fadbe8932ecd0fe238fce5bb4feefa53e6982623a2ac58c8140d01ecba`.

Both explicit-only controls were verified: `disable-model-invocation: true`
for Claude Code and `policy.allow_implicit_invocation: false` for Codex.
Only after verification was the root automatic trigger replaced with the
confirmed task-wide opt-in boundary. Other root instructions were preserved.

This verifies installed Codex discovery and readable contents, not live model
behavior or a Claude plugin installation. A plugin refresh can replace the
local preview until a containing revision is published and installed.
Publication and second-machine setup remain manual; see the README's
Delegation on another machine instructions.

## Evaluation scope

Separate Codex and Claude direct, novel, and no-change triads are read-only
synthetic assessments with fixture checks and semantic rubrics. Existing
metadata tests enforce explicit-only invocation in both clients. The skill's
cases run in baseline and forced arms only. No live model evaluations were run.
Other skills' published result metrics remain unchanged.

The generic Skill Creator validator rejects the Claude-specific
`disable-model-invocation` field; the repository schema explicitly supports
that extension, and Codex plugin discovery accepted it without errors.

## Validation

- `npm run lint`: passed.
- `npm run build`: bundled shared references in sync.
- `npm run evals:validate`: 243 cases validated.
- `npm test`: passed (7 Node tests, 274 script tests with one skip, and
  416 evaluation-harness tests).
- All six delegation fixture validators passed independently.
- Codex routing rows match the original root table exactly.
- `git diff --check`: passed.

## Custom-agent removal validation

The custom-definition removal changes role availability and setup guidance;
the model/effort tables and explicit-invocation controls are unchanged.

After removal, lint, reference synchronization, the 243-case corpus validator,
and all 46 workflow-matrix tests passed. Filesystem checks confirmed no custom
TOMLs remain in `~/.codex/agents/`, no bundled or cached definition assets
remain, and the installed Codex reference matches the repository. Recovery
copies of the two removed local files are under
`/tmp/codex-custom-agents-before-removal-20261103/`.
