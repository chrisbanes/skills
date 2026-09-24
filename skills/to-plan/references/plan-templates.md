# Plan Templates

Use exactly one source-appropriate template.

## GitHub plan comment

```markdown
<!-- to-plan:implementation-plan:v2 -->

**Revision:** <positive integer>
**Supersedes:** <previous plan permalink or none>
**Replan report:** <verified report permalink or none>

## Implementation plan

**Issue:** <canonical issue URL>
**Planned against:** `<branch>` at `<full SHA>`
**Publication mode:** Reviewed | Autonomous
**Local state:** Clean | Unrelated changes present

### Approach

<Concise intended route.>

### Guardrails

- <Behavior or contract that must remain unchanged.>
- <Explicitly out-of-scope work.>
- For mechanical mismatches within this fixed contract, allow one focused
  diagnosis and at most two repair edit-and-validation cycles; normal test-first
  cycles do not count. Stop for a design or contract change, overlapping baseline
  change, or exhausted repair budget, and report the evidence and remaining decision.

### Planning decisions

- <Non-obvious contract-realizing choice and supporting evidence; do not
  restate Guardrails.>
- <Optional: material assumption, proportionate evidence or bounded proof, and
  the result or failure gate. Express any proof using the existing slice fields;
  dependent slices name its task ID.>

### Implementation context

- **Existing:** `<path>` — `<symbol>` currently <responsibility, relevant call
  flow, and callers>.
- **New:** `<path>` — `<symbol>` will <responsibility and wiring>.
- **Follow:** `<path:symbol>` for <repository-supported pattern to reuse>.
- Omit **New** or **Follow** when the plan creates no symbol or needs no
  repository exemplar.

### Implementation slices

**Task graph and parallelism:** <Confirm the graph is acyclic; list shared-file
or integration constraints and identify sets of ready tasks safe to run
concurrently.>

#### 1. <Observable increment>

**Task ID:** `<stable unique ID, e.g. T1>`
**Depends on:** `none` (reserved root marker; not a task ID) | `<task ID>, ...`
**Prerequisites:** <Earlier slice or none; include the result of any required
proof and the proof task ID where applicable.>
**Files and symbols:** <Name each existing file/symbol to edit and each new
file/symbol to create; state its responsibility and how it connects to callers.>
**Test:** <Exact test file and seam, setup/fixture, concrete inputs/actions,
assertions, and expected red failure; explain if an automated red test is
impractical.>
**Implementation:** <Ordered edits that produce this slice's observable
deliverable; state interface/ownership and call-site wiring where relevant, plus
material branches, errors, and edge cases.>
**Validate:** From `<working directory>`, after <setup or none>, run `<exact
focused command>`; expect <specific successful result proving this slice>.
**Complete when:** <Observable deliverable and its focused check are complete.>

### Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <One observable acceptance criterion> | <slice number> | <Named focused check in the slice> |

### Final validation

- From `<working directory>`, after <setup or none>, run `<exact final
  command>`; expect <specific successful result>.
- <Evidence-based exception and execution-time check, when applicable.>

### Review focus

- <Ticket-specific risk not already stated in Guardrails; omit when there is none.>

### Allowed deviations (when task-specific)

- <Any task-specific mechanical allowance; omit when the standard handoff rule
  is sufficient.>

### Re-plan triggers (when task-specific)

- <A material task-specific stop condition beyond the standard re-plan rules;
  omit when none applies.>
```

## Conversation plan

```markdown
<!-- to-plan:conversation-plan:v1 id=<lowercase UUIDv4> -->

# <Established task title>

**Planned against:** `<branch>` at `<full SHA>`
**Local state:** Clean | Unrelated changes present

## Approach

<Concise intended route.>

## Guardrails

- <Behavior or contract that must remain unchanged.>
- <Explicitly out-of-scope work.>
- For mechanical mismatches within this fixed contract, allow one focused
  diagnosis and at most two repair edit-and-validation cycles; normal test-first
  cycles do not count. Stop for a design or contract change, overlapping baseline
  change, or exhausted repair budget, and report the evidence and remaining decision.

## Planning decisions

- <Non-obvious contract-realizing choice and supporting evidence; do not
  restate Guardrails.>
- <Optional: material assumption, proportionate evidence or bounded proof, and
  the result or failure gate. Express any proof using the existing slice fields;
  dependent slices name its task ID.>

## Implementation context

- **Existing:** `<path>` — `<symbol>` currently <responsibility, relevant call
  flow, and callers>.
- **New:** `<path>` — `<symbol>` will <responsibility and wiring>.
- **Follow:** `<path:symbol>` for <repository-supported pattern to reuse>.
- Omit **New** or **Follow** when the plan creates no symbol or needs no
  repository exemplar.

## Implementation slices

**Task graph and parallelism:** <Confirm the graph is acyclic; list shared-file
or integration constraints and identify sets of ready tasks safe to run
concurrently.>

### 1. <Observable increment>

**Task ID:** `<stable unique ID, e.g. T1>`
**Depends on:** `none` (reserved root marker; not a task ID) | `<task ID>, ...`
**Prerequisites:** <Earlier slice or none; include the result of any required
proof and the proof task ID where applicable.>
**Files and symbols:** <Name each existing file/symbol to edit and each new
file/symbol to create; state its responsibility and how it connects to callers.>
**Test:** <Exact test file and seam, setup/fixture, concrete inputs/actions,
assertions, and expected red failure; explain if an automated red test is
impractical.>
**Implementation:** <Ordered edits that produce this slice's observable
deliverable; state interface/ownership and call-site wiring where relevant, plus
material branches, errors, and edge cases.>
**Validate:** From `<working directory>`, after <setup or none>, run `<exact
focused command>`; expect <specific successful result proving this slice>.
**Complete when:** <Observable deliverable and its focused check are complete.>

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <One observable acceptance criterion> | <slice number> | <Named focused check in the slice> |

## Final validation

- From `<working directory>`, after <setup or none>, run `<exact final
  command>`; expect <specific successful result>.
- <Evidence-based exception and execution-time check, when applicable.>

## Review focus

- <Task-specific risk for implementation review; omit when there is none.>

## Allowed deviations (when task-specific)

- <Any task-specific mechanical allowance; omit when the standard handoff rule
  is sufficient.>

## Re-plan triggers (when task-specific)

- <A material task-specific stop condition beyond the standard re-plan rules;
  omit when none applies.>
```
