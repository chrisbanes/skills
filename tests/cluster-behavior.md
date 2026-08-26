# Cluster behavior smoke checks

The committed evaluator owns the canonical behavioral corpus, including the
eight routing cases across the Compose and Kotlin/Gradle suites. Validate it
without model calls:

```sh
npm run evals:validate
npm test
```

Use a fresh installed client context only to smoke-test behavior the evaluator
cannot observe: skill discovery and relative-link loading. On each supported
client, give the router a Kotlin source task with both one-shot event delivery
and sealed route mapping. It should report
[`kotlin-concurrency-and-flow`](../skills/kotlin-concurrency-and-flow/SKILL.md)
and [`kotlin-control-flow`](../skills/kotlin-control-flow/SKILL.md), without a
Compose skill unless the task supplies a Compose API/composable or explicitly
asks for new Compose code.

Record the candidate commit, client/model, selected entrypoints, loaded
references, and any missing safeguard. Re-run the affected smoke check after a
router or installer correction. Release only when deterministic validation,
lint, and the repository test suite pass.
