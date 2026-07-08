# Installing Chris Banes Skills for OpenCode

## Prerequisites

- [OpenCode](https://opencode.ai) installed

## Installation

Add `chrisbanes-skills` to the `plugin` array in your `opencode.json` file, either globally or in a project:

```json
{
  "plugin": ["chrisbanes-skills@git+https://github.com/chrisbanes/skills.git"]
}
```

Restart OpenCode. The plugin installs through OpenCode's plugin manager, registers the repository's skills, and adds short routing guidance for Kotlin, Android, JVM, and Jetpack Compose tasks.

## Verify

Use OpenCode's native `skill` tool to list skills, or ask a routing question such as:

```text
Which Chris Banes skill should I use to review this Compose state model?
```

For broad Kotlin, Android, JVM, or Jetpack Compose tasks, the agent should start with `using-chrisbanes-skills` and then load the focused skill for the task.

OpenCode uses its own plugin install. If you also use Claude Code, Codex, or another harness, install this skills repo separately for each one.

## Updating

OpenCode installs git-backed plugin specs through its plugin manager. Some OpenCode and Bun versions pin resolved git dependencies in a lockfile or cache, so a restart may not pick up the newest commit. If updates do not appear, clear OpenCode's package cache or reinstall the plugin.

To pin a specific release tag:

```json
{
  "plugin": ["chrisbanes-skills@git+https://github.com/chrisbanes/skills.git#2026.7.6"]
}
```

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i chrisbanes-skills`
2. Verify the plugin line in your `opencode.json`
3. Make sure you are running a recent version of OpenCode

### Skills not found

1. Use the native `skill` tool to list discovered skills
2. Check that the plugin is loading
3. Restart OpenCode after changing plugin configuration

## Getting Help

- Report issues: https://github.com/chrisbanes/skills/issues
- Repository: https://github.com/chrisbanes/skills
