# Review Contracts

Named skills are preferred providers, not mandatory dependencies. Record the
provider used for each contract and its result.

Review every contract once against the frozen candidate's full verified-base-to-
`HEAD` diff and uncommitted changes. After a repair changes the reviewed
candidate, whether committed or uncommitted, retain only review evidence that
still applies. Review the changed range and its interaction
with the previously reviewed effective diff for each affected contract; repeat
full verification and review when prior evidence is invalid or that scope
cannot be bounded. Record the reviewed heads, affected range, and disposition
so the combined evidence covers the exact final `HEAD` and clean worktree
before every push.

## Correctness And Standards

1. Review the scope required by the evidence rule above.
2. Check behavioral correctness, regressions, security, repository
   instructions, tests, error handling, and maintainability.
3. Report concrete findings with evidence and priority.
4. Fix each actionable finding, explain why no change is warranted, or stop on
   material uncertainty.
5. Reverify affected behavior and finish with no actionable finding except one
   explicitly classified as very low priority.

## Reuse, Clarity, And Efficiency

1. Inspect the same required scope for existing reusable code, unnecessary
   duplication, avoidable work, unclear control flow, and repository-standard
   alternatives.
2. Apply only high-confidence, behavior-preserving improvements.
3. Reverify the changed scope and apply the evidence rule to the final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

## Over-Engineering

1. Inspect the updated scope for needless abstractions, speculative
   generality, wrappers, configuration, indirection, dependencies, and code
   that can be deleted.
2. Apply only high-confidence, behavior-preserving simplifications.
3. Reverify the changed scope and apply the evidence rule to the final `HEAD`.
4. Finish with no actionable finding except one explicitly classified as very
   low priority.

One provider may satisfy multiple contracts only when it reports each result
separately. Tests, compilation, or a clean diff alone do not satisfy a review
contract. Providers must not stage, commit, or push.
