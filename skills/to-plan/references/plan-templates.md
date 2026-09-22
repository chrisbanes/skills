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

### Planning decisions

- <Non-obvious contract-realizing choice, supporting repository evidence, and
  decision the implementer must preserve.>

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
**Depends on:** `none` | `<task ID>, ...`
**Prerequisites:** <Earlier slice or none; relevant context or exemplar.>
**Files and symbols:** <Existing files/symbols to edit and new files/symbols to
create, labelled existing/new.>
**Test:** <Exact test file and seam; fixture/setup; inputs/actions; assertions;
and expected red failure, or why an automated red test is impractical.>
**Implementation:** <Ordered edits, including interfaces or pseudocode when
needed, control/data flow, branches/errors/edge cases, and call-site wiring.>
**Validate:** From `<working directory>`, after <setup or none>, run `<exact
focused command>`; expect <specific successful result>.
**Complete when:** <Observable completion condition.>

### Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <Criterion> | <number> | <Test or precise manual check> |

### Final validation

- From `<working directory>`, after <setup or none>, run `<exact final
  command>`; expect <specific successful result>.
- <Evidence-based exception and execution-time check, when applicable.>

### Review focus

- <Ticket-specific risk for implementation review.>

### Allowed deviations

- Within the fixed contract, <bounded mechanical choices or none> may be
  repaired after one focused diagnosis pass and at most two
  repair edit-and-validation cycles across all unexpected mismatches; normal
  test-first implementation cycles do not count. Report the repair.

### Re-plan triggers

- Stop for any required design or contract change, overlapping baseline change,
  a mismatch unresolved after the repair budget is exhausted, or
  <task-specific material condition>. Report the
  evidence, attempted repair and validation, and remaining decision or upstream
  change; do not invoke `to-plan` from the implementation worktree.
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

## Planning decisions

- <Non-obvious contract-realizing choice, supporting repository evidence, and
  decision the implementer must preserve.>

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
**Depends on:** `none` | `<task ID>, ...`
**Prerequisites:** <Earlier slice or none; relevant context or exemplar.>
**Files and symbols:** <Existing files/symbols to edit and new files/symbols to
create, labelled existing/new.>
**Test:** <Exact test file and seam; fixture/setup; inputs/actions; assertions;
and expected red failure, or why an automated red test is impractical.>
**Implementation:** <Ordered edits, including interfaces or pseudocode when
needed, control/data flow, branches/errors/edge cases, and call-site wiring.>
**Validate:** From `<working directory>`, after <setup or none>, run `<exact
focused command>`; expect <specific successful result>.
**Complete when:** <Observable completion condition.>

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <Criterion> | <number> | <Test or precise manual check> |

## Final validation

- From `<working directory>`, after <setup or none>, run `<exact final
  command>`; expect <specific successful result>.
- <Evidence-based exception and execution-time check, when applicable.>

## Review focus

- <Task-specific risk for implementation review.>

## Allowed deviations

- Within the fixed contract, <bounded mechanical choices or none> may be
  repaired after one focused diagnosis pass and at most two
  repair edit-and-validation cycles across all unexpected mismatches; normal
  test-first implementation cycles do not count. Report the repair.

## Re-plan triggers

- Stop for any required design or contract change, overlapping baseline change,
  a mismatch unresolved after the repair budget is exhausted, or
  <task-specific material condition>. Report the
  evidence, attempted repair and validation, and remaining decision or upstream
  change; do not invoke `to-plan` from the implementation worktree.
```
