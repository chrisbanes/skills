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

### Implementation slices

#### 1. <Observable increment>

**Red test:** <Exact test file, seam, and expected failure.>
**Implementation:** <Exact files/symbols and smallest intended move.>
**Validate:** `<Exact focused command.>`
**Complete when:** <Observable completion condition.>

### Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <Criterion> | <number> | <Test or precise manual check> |

### Final validation

- `<Exact final command.>`
- <Evidence-based exception and execution-time check, when applicable.>

### Review focus

- <Ticket-specific risk for implementation review.>

### Allowed deviations

- <Local implementation choices that may change autonomously.>

### Re-plan triggers

- <Material condition that requires stopping.>
```

## Conversation plan

```markdown
<!-- to-plan:conversation-plan:v1 id=<lowercase UUIDv4> -->

# <Confirmed task title>

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

## Implementation slices

### 1. <Observable increment>

**Red test:** <Exact test file, seam, and expected failure.>
**Implementation:** <Exact files/symbols and smallest intended move.>
**Validate:** `<Exact focused command.>`
**Complete when:** <Observable completion condition.>

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| <Criterion> | <number> | <Test or precise manual check> |

## Final validation

- `<Exact final command.>`
- <Evidence-based exception and execution-time check, when applicable.>

## Review focus

- <Task-specific risk for implementation review.>

## Allowed deviations

- <Local implementation choices that may change autonomously.>

## Re-plan triggers

- <Material condition that requires stopping.>
```
