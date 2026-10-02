Assess two invocations of the same approved delivery contract using only supplied
state: one was launched manually, and the other comes from a verified Project
controller handoff. Source, plan, reviewed behavior-test seams and clean base
are identical. Neither asks explicitly for parallel execution. The manual
invocation has no merge grant; the Project controller retains its own merge
grant and all board, claim and issue mutations. All needed providers exist.

The plan has four stable tasks and an acyclic graph:

| Task | Dependencies | Exclusive write set |
| --- | --- | --- |
| A | none | parser.py, tests/test_parser.py |
| B | none | renderer.py, tests/test_renderer.py |
| C | A | parser.py, tests/test_parser.py |
| D | A, B, C | integration.py, tests/test_integration.py |

Each task has a decision-complete implementation brief and focused validation.
Two implementation workers and a later independent reviewer can run under the
manual caller's capacity. The Project caller grants two spare active descendant
slots, including all nested workers and reviewers, but currently a different
ready ticket is waiting for its first implementation worker; an extra worker
for this ticket has lower scheduling priority. A delivery coordinator can
prepare the PR description from the approved source while workers implement.

Explain ownership, the first ready dispatches, capacity differences, dependent
release, integration, same-owner repairs, validation reuse and final review for
both callers. Distinguish implementation behavior from caller authority and
capacity; do not change the plan, invent a second scheduler or polling loop,
start agents, run commands, contact providers or edit files.
