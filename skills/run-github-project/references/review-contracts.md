# Review Contracts

Named skills are preferred providers, not mandatory dependencies. Record the
provider used for each contract and its result.

## Correctness And Standards

1. Review the exact verified-base-to-`HEAD` diff and uncommitted changes.
2. Check behavioral correctness, regressions, security, repository
   instructions, tests, error handling, and maintainability.
3. Report concrete findings with evidence and priority.
4. Fix each actionable finding, explain why no change is warranted, or stop on
   material uncertainty.
5. Reverify affected behavior and finish with no actionable finding except one
   explicitly classified as very low priority.

## Reuse, Clarity, And Efficiency

1. Inspect the same exact scope for existing reusable code, unnecessary
   duplication, avoidable work, unclear control flow, and repository-standard
   alternatives.
2. Apply only high-confidence, behavior-preserving improvements.
3. Reverify every changed scope and repeat this contract against final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

## Over-Engineering

1. Inspect the updated scope for needless abstractions, speculative
   generality, wrappers, configuration, indirection, dependencies, and code
   that can be deleted.
2. Apply only high-confidence, behavior-preserving simplifications.
3. Reverify every changed scope and repeat this contract against final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

One provider may satisfy multiple contracts only when it reports each result
separately. Tests, compilation, or a clean diff alone do not satisfy a review
contract. Providers must not stage, commit, or push.
