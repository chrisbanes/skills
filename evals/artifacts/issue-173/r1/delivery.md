# Issue 173 delivery evidence

- Source: [issue 173](https://github.com/chrisbanes/skills/issues/173) and [accepted brief](https://github.com/chrisbanes/skills/issues/173#issuecomment-6979596607).
- [Published plan](https://github.com/chrisbanes/skills/issues/173#issuecomment-6983464373), revision 1. The decoded, normalized body hashes to `318bf992bd76c23e0db28139bdefd31f282412f09e16348b24db516e17ee0472`.
- Implementation base: `a90a4af6af1b5332354a584a4ea2bd15e27dc93c`. The GitLab binding, shepherd, and focused fixtures/tests were byte-identical to the plan base `3d9da4774f441854a8ff4c513487301b057053ca`.

## Offline coverage

- The existing delivery fixture exercises exact H1 selection, an optional manual job, a blocking manual job despite a permissive project policy, a blocking job with a successful pipeline, a blocked latest pipeline with an older success, unknown job policy, stale and foreign pipelines, and merged-results pipelines with matching, missing, and mismatched MR head-pipeline identity. The grader rejects each inverted merge decision. Existing merge-train and tracker-closure scenarios still apply.
- The fake transport advances the source from C1 to H2 after the final MR read. The real direct-merge request carries C1 and receives a fake HTTP 409. The MR stays open and the base tip stays fixed. In a separate offline attempt, the C1 pipeline cannot qualify H2, and a new merge write is sent only after a successful H2 pipeline is read. The live qualification script is untouched.

## Preservation and integration

- Evidence writes are limited to this revision record. The controller's baseline at `/tmp/skills-project22.iHGKcT/issue-173-evidence-baseline.txt` inventories 36 existing paths by mode and blob ID. Compare it against `git ls-tree -r HEAD evals/artifacts` excluding this revision.
- Read-only three-way comparison with held #163 head `f796034e7f729d0f3d43d0b64294a54fdcfdafa3` finds no conflict in the eight files both changes touch. The new variants inherit the base snapshots' data, including any future #163 closing inventory. The held head already conflicts with the unchanged implementation base in the provider-routing paragraph of `skills/run-project/SKILL.md`. Resolve that during #163 integration. No #163 change is included here.
- Focused tests: `python3 -m unittest -v evals.tests.test_delivery_bindings scripts.test_gitlab_code_host_live_check`. Broader checks: `npm test`, `npm run references:check`, `npm run lint`, `npm run evals:validate`, and `git diff --check` against the implementation base.
- Independent review and remote actions remain controller-owned. Live GitLab qualification and live model evaluation were out of scope.
