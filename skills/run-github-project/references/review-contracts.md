# Review Contracts

Give these contracts to the delivery workflow's single fresh independent
read-only reviewer by default. Supply the approved source and repository
standards with the candidate diff. Record each contract's result separately;
reuse current coverage instead of launching another review. Reviewers report
findings; the implementation owner applies repairs. Use extra reviewers only
for distinct risks, substantial scope, or an explicitly requested review skill.

Apply [Behavioral review and repair](behavioral-review.md) for candidate scope,
affected repair reviews, evidence reuse, coverage accounts, related boundary
repairs, external-review convergence and browser diagnostics.
Keep the controller's existing owner, leases, grants, capacity and repair gates.

## Correctness And Standards

1. Review the scope required by the evidence rule above.
2. Check behavioral correctness, regressions, security, repository
   instructions, tests, error handling, and maintainability.
3. Report concrete findings with evidence and priority.
4. Return actionable findings to the implementation owner for repair or an
   evidence-based disposition; stop on material uncertainty.
5. Reverify affected behavior and finish with no actionable finding except one
   explicitly classified as very low priority.

## Reuse, Clarity, And Efficiency

1. Inspect the same required scope for existing reusable code, unnecessary
   duplication, avoidable work, unclear control flow, and repository-standard
   alternatives.
2. Recommend only high-confidence, behavior-preserving improvements.
3. Reverify the changed scope and apply the evidence rule to the final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

## Over-Engineering

1. Inspect the updated scope for needless abstractions, speculative
   generality, wrappers, configuration, indirection, dependencies, and code
   that can be deleted.
2. Recommend only high-confidence, behavior-preserving simplifications.
3. Reverify the changed scope and apply the evidence rule to the final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

One provider may satisfy multiple contracts only when it reports each result
separately. Tests, compilation, or a clean diff alone do not satisfy a review
contract. Reviewers must not edit, stage, commit, or push.
