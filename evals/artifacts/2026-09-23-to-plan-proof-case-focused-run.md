# Focused `to-plan` proof case run

This is a single-run, non-gating evaluation record for
`to-plan-material-assumption-proof-calibration`. It documents the focused model
run requested during review of CB-12. It is not a suite-wide result or evidence
that the target runtime supports cross-mount replacement.

## Reproduction and provenance

- Suite: `workflows-writing`
- Case: `to-plan-material-assumption-proof-calibration`
- Arm / repetition: `forced` / `1`
- Subject: `gpt-5.6-terra`, medium reasoning
- Judge: `gpt-5.6-sol`, high reasoning
- CLI: `codex-cli 0.155.1`
- Explicit cost inputs: subject `$0.208` per call; judge `$0.40` per call.
  The estimate is `$0.608` for one subject and one judge call; this is an
  estimate from the supplied inputs, not a billed amount.
- Command:

  ```sh
  python3.13 evals/run.py run --suite workflows-writing --case to-plan-material-assumption-proof-calibration --arm forced --model gpt-5.6-terra --reasoning medium --judge-model gpt-5.6-sol --judge-reasoning high --subject-cost-per-call-usd 0.208 --judge-cost-per-call-usd 0.40 --repetitions 1 --execute --output-dir .scratch/skill-evals/cb12-watson-second-finding
  ```

- Case digest: `4656daf84ced01cae2527c24018ec4c86f24d06b4c634f62993f4b34048084a0`
- Run fingerprint: `8a59a45e0a73341f109c0d47cb4375f289fa64de71bbc642338d3581b6d00cc5`
- Captured `to-plan/SKILL.md` SHA-256: `558a08c148ee0c02d4f63491b317c863a512ca57ea74423cf6d6f7ba7906361e`
- The run recorded repository HEAD `10e1b94d91f8488fc7391180c472ad044d05f21d`;
  the case digest matches the case and fixture in reviewed candidate
  `17d20fc70adeba2f8ed3e9b4ddaa947652b41a25`.
- Raw local `results.json` SHA-256:
  `0d58daafa9efdd270bd07216cc217836275282979437e0ed8d7c6bcced884a50`.
  The raw run directory is local scratch evidence, not part of the repository.

## Result and audit

The deterministic validator returned 0 (`validated
to-plan-material-assumption-proof-calibration`). Objective grading passed; the
judge returned 0 and marked all five rubric criteria passing; the combined
outcome field is true, with no forbidden-action failures or violations. The
subject used 212,132 input and 7,538 output tokens; the judge used 38,357 input
and 882 output tokens. Neither process retried.

| Criterion | Result and evidence in the plan |
| --- | --- |
| `bounded-proof` | T1 probes a unique sentinel from configured staging to published and requires exact destination bytes plus source absence. |
| `failure-gate` | A T1 failure stops T2 and triggers re-planning; no copy/delete fallback is allowed. |
| `repository-evidence` | It reports the existing direct destination write and marker ordering, both configured mount values, and labels staging plus `os.replace`/`Path.replace` before marking as proposed post-proof behavior. |
| `task-dependency` | The acyclic plan orders T1 → T2 → T3, with T2 gated on T1. |
| `planning-boundary` | It writes only the plan, with no source/configuration edit, runtime proof, or provider contact. |

The final human audit decision is **reject as valid forced behavioral
evidence**. Although the plan, validator, and judge checks pass, the harness
reports `invocation_failure`: the forced-target event integrity check did not
observe the staged `to-plan` skill being read. The audit rationale and run
record are in the local scratch evidence. The scorecard therefore reports this
case as invalid forced evidence, and the passing rubric must not be presented as
a valid skill-effect measurement.

This one forced repetition cannot establish repeatability, compare arms, or
prove behavior on an actual cross-mount runtime. The fixture is synthetic; the
required target-runtime probe remains unrun.
