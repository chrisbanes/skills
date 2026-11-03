# Codex delegation

Use this reference after explicit invocation of `subagent-delegation` when
Codex is the active runtime.

1. Map the assignment to roles the runtime actually exposes. Use `explorer`
   for specific codebase discovery and `worker` for implementation and repairs
   when available. Use a suitable general agent for predetermined checks or
   independent analysis, with the required mode and permissions in its brief.
   This skill requires no custom `checker` or `investigator` definition;
   do not invent an unavailable role or install one implicitly.
2. Inspect the role's exposed settings and applicable installed agent TOML.
   Installed pins take precedence over this table. Recheck when the role or
   configuration changes. Use `fork_turns="none"` for a fresh assignment and
   explicitly set each unpinned `model` and `reasoning_effort`.
3. Choose the row by the judgment still required, including on reassignment.
   Luna means `gpt-6-luna`; Sol means `gpt-6.1-sol`; Terra means
   `gpt-6.1-terra`; Astra means `gpt-6-astra`.

| Assignment | Model / effort |
|---|---|
| Purely mechanical: exact checks, simple extraction, no judgment | Luna / low |
| Computer use or visual interpretation with a defined outcome: navigating screens, matching images, interpreting screenshots or drawings | Terra / medium |
| Concise drafting or editing from supplied material, with clear audience and factual requirements | Terra / medium |
| Ordinary bounded implementation, fixes, refactoring, and UI fixes with settled requirements and interactions (default) | Terra / high |
| Substantial synthesis across several sources, clear constraints | Luna / xhigh |
| Complex or ambiguous: judgment across interacting components | Sol / medium |
| Difficult correctness investigations or independent correctness reviews: competing paths, ownership, ordering, cancellation, security, data integrity | Sol / high |
| Conflicting evidence, or demanding deliverables needing cross-component polish | Sol / xhigh |

4. Reserve Astra, max, and ultra for justified exceptions: explain why
   Sol / xhigh is insufficient. Repository size or elapsed time alone does
   not justify them.
5. Use a fresh suitable agent with `fork_turns="none"` for an independent
   audit. Give it an explicit read-only review brief and apply read-only tool
   or sandbox restrictions where supported. Resume the original worker for
   repairs when possible; recheck capability and pinned settings before giving
   it a new assignment.
6. Finish selection when the exposed role, effective settings, and brief
   satisfy the assignment; return a capability or settings mismatch to the
   lead before dispatch.

When evaluating changes to this policy, consult the
[OpenAI model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
alongside representative-task evidence.
