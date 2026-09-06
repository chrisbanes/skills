# Workflow model compatibility

## Scope and baseline

Repository-local revisions to `to-plan` and `implement-with-subagents`, based on
`2be6d3ed0d4c4d996fb4c3389120be43d63f6d6b`. No global configuration, installed
skills, model defaults, worker definitions, or versions are changed.

The implementation clarifies when an authorized conversation can produce a local
plan and when independently inspected verification evidence can satisfy an
acceptance check without an unnecessary rerun. Publication authorization,
read-only scope, implementation ownership, required dependencies, and real
verification requirements remain intact.

## Evidence status

Compatibility is **not yet established**. The local Codex CLI is 0.153.4.
A minimal Astra availability probe returned READY, but it was not a skill
behavior test. The first evaluator attempt failed to initialize both child
runtimes under the parent sandbox; those process failures are not model-quality
results. Automatic approval review rejected the escalated evaluator retry because
repository-derived tasks and skill content would be sent to external model
services without explicit disclosure authorization. No alternate execution path
was used. Live comparisons remain pending that authorization.

The existing published score tables are unchanged. They do not measure this
revision or establish Astra compatibility.

## Cases and execution limits

Ten additional calibration cases preserve the 15-case workflows/writing
benchmark and its default call count. Planning covers a fully authorized local
draft, a prior confirmed contract, an unresolved material choice, and a
decision-complete discussion-only request that must not write a draft. Evidence
acceptance covers reusable, stale, missing, post-edit, failed, and explicitly
required fresh verification. Existing direct, novel, and restraint cases remain
available as regression controls.

The two positive planning cases require an actual marked draft artifact.
Orchestration cases remain read-only assessments of supplied evidence; their
results cannot prove delegation, commit acceptance, or command execution. A
separate bounded live orchestration check is still required before claiming
end-to-end coverage. CLI feature discovery reports multi_agent available, but
availability alone is not an execution result.

## Comparison protocol

- Core subjects: Astra/medium, Sol/medium, and Terra/medium. Add Luna/high for
  the six verification cases. Set models only through evaluator arguments.
- Pin the judge to Sol/high for both snapshots and every subject. Inspect
  disagreements and inconsistent conditions against raw evidence.
- Stage identical cases, fixtures, and harness in isolated repository snapshots;
  restore only the two target skill trees from the baseline for the old-text
  condition. Retain full input digests and separate output directories.
- Run none/forced arms; these skills remain explicit-only. Preserve raw records
  and keep snapshots/models in separate scorecards. Do not copy baseline records
  across mismatched fingerprints.
- Start with one repetition, then expand to three only after the smoke results
  are valid. Distinguish unnecessary pauses and checks from required restraint.
- No unresolved correctness, authorization, or restraint regression is acceptable
  in the tested conditions. Inspect failures rather than silently averaging them
  away. Do not manufacture RED when the old skill already behaves correctly.
- The existing uplift gates stay advisory and unchanged. A ceiling baseline is
  not evidence that the skill is harmful or that compatibility passed.

Select the ten cases explicitly; `--skill` intentionally excludes calibration
cases. Preview one Astra snapshot with:

```shell
python3 evals/run.py plan --suite workflows-writing \
  --case to-plan-authorized-draft-direct \
  --case to-plan-prior-confirmed-novel \
  --case to-plan-unresolved-choice-negative \
  --case to-plan-discussion-only-negative \
  --case implement-with-subagents-reuse-direct \
  --case implement-with-subagents-stale-evidence-negative \
  --case implement-with-subagents-missing-output-negative \
  --case implement-with-subagents-post-edit-negative \
  --case implement-with-subagents-failed-verification-negative \
  --case implement-with-subagents-explicit-rerun-novel \
  --arm none --arm forced --model gpt-6-astra --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high --repetitions 1 \
  --subject-cost-per-call-usd 1 --judge-cost-per-call-usd 0.4
```

Repeat for Sol and Terra using their per-call assumptions below. For Luna/high,
select only the six `implement-with-subagents` cases. Run the same matrix on
both immutable snapshots. The CLI preview has been checked locally: the core
models each schedule 20 subject and 20 judge calls per snapshot/repetition;
Luna schedules 12 of each. No preview invokes a model.

## Call and cost preview

For ten cases, two arms, two snapshots, and three core subjects, one repetition
requires 120 subject calls plus 120 judge calls. Six Luna cases add 24 subject
calls plus 24 judge calls: **288 top-level calls** total. Three repetitions
require **864 top-level calls**, before retries, existing-case controls, or a
live subagent check. The harness can retry a failed subject or judge once.
These additional calls must be included in an execution budget.

Planning assumptions use 80,000 input and 4,000 output tokens per top-level call,
with no cache discount: Astra $1.00, Sol $0.40, Terra $0.208, Luna $0.0208; each
Sol judge $0.40. This gives approximately **$122 for one repetition** or **$367
for three**, excluding retries, cache writes, and extra controls. These are
API-equivalent estimates, not a quote for Codex subscription usage or a hard
spend cap. Actual usage must be measured from successful runs.

Rates checked on 2026-09-06: [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## Disclosure boundary

The proposed calls send evaluator-owned synthetic task prompts, fixture source,
the selected repository skill text/references, tool outputs, generated diffs,
and blinded judge packets to OpenAI through the authenticated Codex CLI. They
must not load global user instructions, unrelated repository files, credentials,
or personal records into the subject or judge prompts. CLI authentication and
incidental runtime state are separate from model/agent configuration changes.
Input isolation must be checked before execution.

## Local validation

Planning baseline: 79 corpus cases validated; 10 workflow-matrix tests passed.
Implementation validation: `npm run lint` passed; `npm run evals:validate`
validated 88 cases; `npm test` ran 279 tests successfully with one existing
platform-specific skip. The planning fixture baseline passed its one unittest
with `-B`, and `git diff --check` passed. Locked npm dependencies were installed
from the local cache with `npm ci --offline --ignore-scripts`. No model behavior
result is implied by these deterministic checks.

The nested-artifact runner regression was reproduced before the fix: the
existing untracked-file integration test, extended to create
`.scratch/to-plan/task.md`, reported `.scratch/` instead of the file path.
The runner now requests all untracked files, preserving the generated plan in
changed-path grading and the judge diff. The focused runner/grading/judge tests
are rerun after that correction. This is deterministic RED/GREEN evidence;
no skill-behavior RED/GREEN run has occurred.

## Review outcome

The first Spec review required two corrections: retain the unconditional
Plan-mode gate before drafting and capture files inside new untracked
directories. Both were fixed. The post-fix evaluator suite passed all 145 tests.
Fresh independent Standards and Spec reviews each returned ship for the local
implementation, with no open code findings. Reviews were behaviorally read-only
in the shared checkout, not OS-isolated. The live compatibility requirement
remains incomplete; the scratch implementation plan is preserved.

## Main-branch reconciliation

Integrated `84c2c53` before publishing the PR update. Preserved main's two
provider calibration cases alongside the nine compatibility cases: 11 workflow
calibration cases total, with the 15-case benchmark unchanged. After resolving
the suite-count and matrix-test conflicts, lint passed, all 90 corpus cases
validated, and the full local suite ran 283 tests with one platform-specific
skip. All five plugin manifests passed JSON validation. Live model comparisons
remain pending.
