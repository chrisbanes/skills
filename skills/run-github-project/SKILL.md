---
name: run-github-project
description: Use when asked to set up, review, or operate a repository's GitHub Project workflow, including next-issue execution or an authorized drain.
compatibility: "Requires deliver-tasks; execution providers are mode-specific."
disable-model-invocation: true
---

# Run GitHub Project

## Core principle

Use the shared delivery controller with the GitHub Project binding.

## Procedure

1. Read [GitHub binding](references/github-binding.md) and select it for this
   invocation. Preserve the configured Status schema, trusted configuration
   path, role labels, marker formats and Project Watcher.
2. Load [deliver-tasks](../deliver-tasks/SKILL.md) and follow its complete
   procedure for `review`, `setup`, `next` or explicitly authorized `drain`.
   Loading that procedure is part of this explicit invocation; it grants no
   additional authority. Pass the invocation, supplied state and limits unchanged.
3. Finish only through the controller's mode-specific finish gate and report.
