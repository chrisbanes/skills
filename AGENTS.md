# AGENTS.md

Instructions for AI agents (Claude Code, etc.) working in this repo.

## When adding, renaming, or removing a skill

1. **Update `README.md`** — keep the "Skills" list in sync. Each entry links to the skill's `SKILL.md` and summarises what it covers. If you add a skill and don't update the README, the change is incomplete.
2. **Do not update plugin or skill versions unless explicitly asked.** If the user asks for a release/version bump, use semver in `.claude-plugin/plugin.json`: patch for fixes/wording, minor for a new skill or new triggers, major for removals or breaking renames.

## Skill layout

- Skills live at `skills/<skill-name>/SKILL.md`. **Flat** — never nest by language or topic. Encode the topic in the directory name instead (e.g. `kotlin-structured-concurrency`, not `kotlin/structured-concurrency`).
- The `name:` in the SKILL.md frontmatter **must match the directory name** exactly.
- Use lowercase kebab-case for directory and `name:` values.

## Manifests

- `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` are both JSON (not JSONC). Validate with `jq . <file>` before committing.
- The plugin `name` field in both manifests must stay `chrisbanes-skills`.

## What not to do

- Don't add CI, build tooling, or scripts unless asked — this is a content repo.
- Don't reorganise existing skills "for consistency" without a concrete reason; renames break user references.
