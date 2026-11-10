---
name: subagent-delegation
description: Use when the user invokes the subagent delegation playbook, or the user's instructions direct its use when delegating work or deciding whether to delegate.
---

# Subagent delegation

## Core principle

Match each bounded assignment to the capability and judgment it needs, while
keeping architecture, integration, authorization, and final acceptance with
the lead. Installed agent definitions are authoritative for pinned settings.

## Procedure

1. Apply this playbook when the user invokes it or the user's instructions
   direct its use for delegation; either covers delegation and reassignment
   throughout the current task. Without either, a generic request to implement
   work or use subagents does not apply it. Keep required constraints in agent
   briefs so they apply without child agents loading this skill. Loading the
   skill does not authorize implementation.
2. Prefer solo work for small or tightly coupled tasks; use delegation or
   worktrees when independent work or isolation justifies them. Leave task-graph
   execution, worktree lifecycle, integration sequencing, and implementation
   gates to the calling workflow, such as `implement-with-subagents`.
3. Choose the capability before the runtime role name: specific discovery,
   predetermined mechanical checking, implementation with self-review and
   repair ownership, or independent read-only analysis. For analysis, state
   the mode: review against requirements, or investigation of a concrete
   unresolved question. Establish concrete evidence before an investigation.
4. Load only the active runtime's reference:
   - [Codex](references/codex.md): exposed roles, installed TOML pins, model
     and effort routing, and fresh-context calls.
   - [Claude Code](references/claude-code.md): agent definitions, model and
     effort routing, invocation overrides, and owner/reviewer lifecycle.
   - Other runtimes: inspect their exposed capabilities and installed policy;
     preserve configured choices rather than translating either provider's
     model identifiers or effort values. Resolve missing required settings
     before dispatch.
5. Reassess capability and judgment for every new assignment, including
   reassignment, independently of the parent task's size or model. Keep the
   lead's model unchanged. File count, component count, or a sensitive area
   alone does not raise a tier; when judgment matters, prefer a stronger model
   at lower effort over a weaker model at higher effort. Preserve pinned
   settings and access restrictions. If required capability or settings
   are unavailable, report and resolve the mismatch before dispatch. Name the
   assignment category in the brief and justify departures from the default
   row. For investigations, name the unresolved question; for reviews,
   identify the correctness checks; for synthesis, identify the evidence or
   deliverable demands. At opus or fable (Claude Code), Sol (Codex), or an equivalent
   tier with high effort or above, make that question or those checks
   concrete; touching a risky area alone does not qualify. If work stalls,
   diagnose missing inputs, tool failures, or routine test repairs before
   considering a higher tier.
6. Give each agent a self-contained brief that fills every field of the
   [handoff brief](references/subagent-selection.md#handoff-brief). Tell
   workers they share the codebase, must preserve others' edits, and must
   accommodate concurrent changes. Further delegation
   requires the lead's explicit authority. Keep remote mutations with the
   root task holding the user's authorization, with one mutation owner.
7. Launch independent assignments in parallel. Queue work behind another agent
   only for a stated dependency, such as shared files, a contract, or ordering;
   name that dependency. Separate worktrees alone do not remove dependencies.
8. Choose independent audits proportionally to risk unless the calling
   workflow requires one. Use a fresh read-only
   reviewer without the implementation conversation. Supply original
   requirements, the plan when available, and exact review scope; require a
   `ship`, `fix-first`, or `rethink` verdict with evidence. Keep repairs with
   the original worker and context where possible; the lead may take ownership
   or explicitly reassign them.
9. Inspect delegated diffs and verification evidence before accepting the work.
   Repeat checks when evidence is incomplete or affected code changes, without
   duplicating adequate validation. Return failures to the owner for repair
   and reassess affected evidence.

## Finish gate

Finish when the lead has inspected the assigned result and its evidence,
resolved failures or reported the specific blocker, and made the acceptance
decision under the calling workflow. For advice-only requests, finish with the
assignment choices and their reasons; do not spawn agents or start execution.
