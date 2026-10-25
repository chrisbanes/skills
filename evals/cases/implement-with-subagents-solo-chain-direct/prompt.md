Review the proposed orchestration using the supplied state below. State the next action, ownership and required checks. Do not run commands, launch agents, edit files, or contact providers. Skill and reference reads are allowed.

# Immutable evaluation state

Tasks A and B form a strict chain: A has no dependencies and B depends on A. Neither task can run independently of the other.
Both task seams and tdd are available. An independent read-only final reviewer is available. The starting checkout is clean at base 1111111.
The draft assigns A and B to separate workers and requires a separate lead acceptance before each integration. A has not started.
