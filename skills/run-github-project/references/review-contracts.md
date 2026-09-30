# Review Contracts

Give these contracts to the delivery workflow's single fresh independent
read-only reviewer by default. Supply the approved source and repository
standards with the candidate diff. Record each contract's result separately;
reuse current coverage instead of launching another review. Reviewers report
findings; the implementation owner applies repairs. Use extra reviewers only
for distinct risks, substantial scope, or an explicitly requested review skill.

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
