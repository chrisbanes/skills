# Plan Templates

Use exactly one source-appropriate template. Keep every slice executable, but
scale its detail to uncertainty and risk: the fields below are a contract, not
a demand for an exhaustive edit recipe. Reference source requirement identities
and shared setup instead of repeating them. Add precise symbols, ordered edits,
wiring and failure branches where they resolve ambiguity or protect correctness.

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
**Epoch closure:** <null, or one-line JSON object with effective {url, digest},
retained_work [dispositions], and evidence [dispositions] when closing amendments>

### Approach

<Concise intended route.>

### Guardrails

- <Behavior or contract that must remain unchanged.>
- <Explicitly out-of-scope work.>
- Continue routine implementation and fixture corrections within unchanged
  requirements, coverage, architecture and authority; record the correction and
  renew affected evidence. A factual plan mismatch allows one diagnosis and two
  repair cycles; ordinary repairs do not consume that budget. Investigate unknown
  overlap; stop for material design/contract changes or exhausted grants.
- Reuse the existing delivery record and valid checks/reviews. Use an integration
  amendment only for a changed published integration decision requiring durable
  consumption; preserve repair budgets and grants.

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
**Files and symbols:** <Name affected files and ownership/interfaces; identify
entry symbols and new symbols where needed to locate or disambiguate the work.>
**Test:** <When behavioral tests apply, name the test file and seam,
setup/fixture, inputs/actions, assertions and expected results. Follow repository
policy and explicit test-first requests; include a sensitivity check when useful.
Otherwise omit this field and specify focused validation below.>
**Implementation:** <State the observable change and settled decisions. Give
ordered edits, exact wiring and material branches/errors only where uncertainty,
safety or a necessary seam requires that precision.>
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

## Approved source contract

<Concise confirmed goal, acceptance criteria, scope, constraints and material
decisions. Include everything a fresh session needs; do not rely on chat history.>

## Approach

<Concise intended route.>

## Guardrails

- <Behavior or contract that must remain unchanged.>
- <Explicitly out-of-scope work.>
- Continue routine implementation and fixture corrections within unchanged
  requirements, coverage, architecture and authority; record the correction and
  renew affected evidence. A factual plan mismatch allows one diagnosis and two
  repair cycles; ordinary repairs do not consume that budget. Investigate unknown
  overlap; stop for material design/contract changes or exhausted grants.

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
**Files and symbols:** <Name affected files and ownership/interfaces; identify
entry symbols and new symbols where needed to locate or disambiguate the work.>
**Test:** <When behavioral tests apply, name the test file and seam,
setup/fixture, inputs/actions, assertions and expected results. Follow repository
policy and explicit test-first requests; include a sensitivity check when useful.
Otherwise omit this field and specify focused validation below.>
**Implementation:** <State the observable change and settled decisions. Give
ordered edits, exact wiring and material branches/errors only where uncertainty,
safety or a necessary seam requires that precision.>
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
