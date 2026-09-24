# Focused `to-plan` specificity calibration results

This is a single-repetition, explicit-skill comparison of the specificity
calibration and its one-function counterexample. It covers only the recorded
case versions and settings below; it does not establish repeatability or
automatic routing behavior.

## Run

- Run directory: `.scratch/skill-evals/cb13-specificity-20260924`
- Recorded repository HEAD: `40c35fbb19aefdb105fe2b916e30653bc3a30879`
- Subject: `gpt-6-luna`, high reasoning; judge: `gpt-6-sol`, high reasoning.
- Codex CLI: `codex-cli 0.155.1`.
- Arms: `none`, `forced`; repetitions: 1.
- Four subject calls and four judge calls; no retries or process failures.
- Cost estimate inputs were `$0.25` per subject call and `$1.00` per judge
  call, yielding a `$5.00` estimate for the run. These are estimate assumptions,
  not billed usage.
- Raw `results.json` SHA-256:
  `93cdb4f9ec409cbc83c10396c45b63b290d4e589c8500cb4621b8df0283c15b9`.

## Specificity calibration

- Case: `to-plan-specificity-calibration`
- Case digest: `56ef622d3c3f603234272f2947942f5b41d63ea75f95f2af783dfb3558d000d6`
- Run fingerprints: `feae9df88696e9df77198b081f62f6a78f781ab81ac624805f7e46f0f6e275f4` (`none`), `d610431494221348610474e2ff0fffff969fcf5f924387fb52d154b434d4614b` (`forced`).
- Forced validator passed; all six rubric criteria passed. The plan uses T1
  for the shared formatter and missing-manifest call site, then T2 depending on
  T1 for the invalid-profile call site. It names both test methods and commands,
  exact spaced-path assertions and red results, and maps both behaviors to
  their proving slice and check.
- The `none` arm did not produce a plan satisfying the structural validator
  or rubric, as expected for this explicit-only skill.

## One-function counterexample

- Case: `to-plan-authorized-draft-direct`
- Case digest: `653b65ff0aca5b3b0d82653b9ac82414d8cec435c01cac13a904acdbfef17b69`
- Run fingerprints: `16695564a57226383d48888bf68ca2cb40b18cb2a91057ef1e074015c24f069d` (`none`), `903a52872213ce18f2a93a56feabb9435540f35e2e4cf832127063c768b86683` (`forced`).
- Forced validator passed; all five rubric criteria passed. The generated plan
  remains one test-first slice and adds no proof task.
- The `none` arm did not produce a plan satisfying the structural validator
  or rubric, as expected for this explicit-only skill.

## Limits

The calibration is synthetic and checks planning behavior for two supplied
call sites. It does not prove production behavior, cross-run consistency, or
provider publication behavior. The advisory scorecard excludes calibration
cases from benchmark gates; its `not met` entries are not regression claims.
