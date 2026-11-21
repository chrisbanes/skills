# Antigravity and Gemini delegation

Use this reference when Antigravity is the active runtime or when routing
Gemini models. The table is the user's routing policy, not a claim that Gemini,
Claude, and Codex models are equivalent.

1. Inspect exposed delegation tools, installed agent definitions
   (`.agents/agents/*.md`, `~/.gemini/config/agents/*.md`), allowed tools,
   workspace mode, and model/effort controls. Antigravity exposes two
   model-selection surfaces:
   - **`invoke_subagent` (native subagents):** Accepts only abstract `Model`
     tiers (`inherit`, `flash_lite`, `flash`, `pro`) and no per-call effort
     parameter. Use built-in `research` (read-only, no network access) for
     bounded discovery or read-only analysis, `define_subagent` for custom
     read-only or restricted roles, and `self` (or a write-enabled custom type)
     for resumable implementation and repairs.
   - **Concrete-slug surfaces (`swarm`, `agy` CLI, ACP/host orchestration):**
     Expose concrete Gemini model slugs (`agy models` or `swarm` `models`)
     and/or `--model` with `--effort` (`low`, `medium`, `high`, `xhigh`, `max`).
2. Preserve installed agent pins by omitting pinned fields on dispatch;
   installed definitions take precedence over this table. For unpinned fields
   on concrete-slug surfaces, select the exact Gemini slug (or `--model` and
   `--effort`) from the table. On `invoke_subagent`, select the table's tier
   (`flash_lite`, `flash`, `pro`, or `inherit` when the lead's verified model
   matches the assignment); if the caller requires a concrete model or effort
   level that `invoke_subagent` cannot enforce, return the capability mismatch
   to the lead before dispatch rather than silently substituting. Never pass
   Codex (`fork_turns`, `reasoning_effort`, GPT model IDs) or Claude
   (`haiku`, `sonnet`, `opus`, `fable`, `run_in_background`) fields or aliases.
3. Route by the assignment's remaining judgment, including on reassignment. On
   concrete-slug surfaces, Hydrogen means `gemini-4-hydrogen-*`, Neon means
   `gemini-4-neon-*`, and Argon means `gemini-4-argon-*`. Verify availability
   (`agy models` or `swarm` `models`) rather than assuming entitlement.

| Assignment | Concrete slug (`agy` / `swarm`) | `invoke_subagent` tier |
|---|---|---|
| Purely mechanical: exact checks, simple extraction, no judgment | `gemini-4-hydrogen-low` | `flash_lite` |
| Computer use or visual interpretation with a defined outcome: navigating screens, matching images, interpreting screenshots or drawings | `gemini-4-hydrogen-medium` | `flash` |
| Concise drafting or editing from supplied material, with clear audience and factual requirements | `gemini-4-hydrogen-medium` | `flash` |
| Ordinary bounded implementation, fixes, refactoring, and UI fixes with settled requirements and interactions (default) | `gemini-4-neon-medium` | `flash` (or `inherit` if lead is Neon) |
| Substantial synthesis across several sources, clear constraints | `gemini-4-neon-high` | `pro` |
| Complex or ambiguous: judgment across interacting components | `gemini-4-neon-medium` | `pro` |
| Difficult correctness investigations or independent correctness reviews: competing paths, ownership, ordering, cancellation, security, data integrity | `gemini-4-neon-high` | `pro` |
| Conflicting evidence, or demanding deliverables needing cross-component polish | `gemini-4-neon-xhigh` | `pro` |

4. `gemini-4-neon-xhigh` (or `pro` on `invoke_subagent`) is the top routine
   row. Reserve `gemini-4-argon-*` and `max` effort for justified exceptions:
   explain why `gemini-4-neon-xhigh` is insufficient and confirm availability.
   Repository size, elapsed time, missing inputs, or routine tool failures do
   not justify them. If a required model or effort is unavailable or not
   entitled, report the mismatch to the lead; never downgrade silently.
5. Follow the [Antigravity handoff rules](subagent-selection.md#antigravity)
   for resuming owners via `send_message` (`conversationId`), reactive wakeup
   without polling, forbidding nesting on `self`, fresh read-only independent
   audits (`research` or read-only `define_subagent` without the implementation
   conversation), and landing or verifying commits and branch refs before
   killing a `share` or `branch` workspace. Recheck a resumed owner's model,
   tools, and workspace state before giving it a new assignment; start a fresh
   suitable agent if the existing owner cannot meet the requirements. Keep
   independent audits separate from repair owners.
6. Finish selection when the effective agent capability, model or tier
   settings, workspace isolation, and reactive delivery satisfy the assignment.
   Return unavailable capabilities or unresolvable setting mismatches to the
   lead before dispatch.
