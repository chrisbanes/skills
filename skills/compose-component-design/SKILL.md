---
name: compose-component-design
description: Use when designing or reviewing reusable Jetpack Compose component APIs with modifier parameters, root layout placement, caller-provided variable content, primitive content parameters, optional content, or boolean shape flags.
---

# Compose component design

## Core principle

Make reusable components caller-placeable and caller-composable: the component
owns its invariant structure while callers retain placement, content, and
policy choices that vary by use.

## Procedure

1. State the requested API concern and keep the edit within it. A focused slot
   review does not authorize unrelated modifier, naming, or cleanup changes.
2. State the component's invariant visual structure and identify every varying
   region, placement concern, and policy choice. When the request names more
   than one of those concerns, report each one; do not stop after the first
   valid modifier or slot finding.
3. When root placement is part of the requested work or a broad component API
   design, accept and apply a caller modifier at the component root unless a
   concrete API boundary makes another placement correct.
4. Represent caller-controlled, unconstrained visual regions with slots rather
   than proliferating primitive content parameters or Boolean shape flags.
   Keep semantic and design-system constraints as primitive parameters.
5. Keep simple conditional structure inline; extract only a coherent reusable
   contract.
6. Read the relevant focused reference below before editing public signatures.
7. Finish with no edit when the existing API already satisfies the requested
   concern. Otherwise finish when callers can position the component, supply
   variable content, and understand ownership without hidden switches.

## Topic router

| Signal | Read |
|---|---|
| Modifier parameter, root layout placement, modifier ordering, or conditional layout wrappers | [Modifier and layout](references/modifier-layout.md) |
| Caller-controlled variable visual regions, optional content, primitive content parameters, or Boolean shape flags | [Slot APIs](references/slot-apis.md) |
| Animation belongs to the public component contract | [Compose animations](../compose-animations/SKILL.md) |
| State ownership changes while designing the component | [Compose state and effects](../compose-state-and-effects/SKILL.md) |
| Semantics or screenshot coverage is needed | [Compose UI testing patterns](../compose-ui-testing-patterns/SKILL.md) |
