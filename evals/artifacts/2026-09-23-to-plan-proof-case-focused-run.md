# Focused `to-plan` proof and countercase results

These are targeted, single-repetition forced-arm checks for the proof-needed
case and its evidence-backed no-proof counterexample. Both are non-gating
model observations, not suite-wide comparisons or proof of target-runtime mount
behavior.

## Proof-needed case

- Run ID: `to-plan-material-assumption-proof-calibration:forced:1`
- Run fingerprint: `94bfabef9ce6ee93571fa07bce8a9d52a1a8fd5193898b6a81589271400d97c3`
- Case digest: `990e3028461438d4f736774f9622b5dc4f1c363162d1c3ecf348d20d4deb46b1`
- Recorded repository HEAD: `bf473cb60d47a68b0272154c217df7e7c1869b12`
- Captured staged `to-plan/SKILL.md` SHA-256:
  `558a08c148ee0c02d4f63491b317c863a512ca57ea74423cf6d6f7ba7906361e`
- Subject: `gpt-5.6-terra`, medium reasoning; judge: `gpt-5.6-sol`, high
  reasoning; Codex CLI: `codex-cli 0.155.1`.
- Cost inputs: subject `$0.208/call`, judge `$0.40/call`; estimate `$0.608`
  for one subject and one judge call, not billed cost.
- Command:

  ```sh
  python3.13 evals/run.py run --suite workflows-writing --case to-plan-material-assumption-proof-calibration --arm forced --model gpt-5.6-terra --reasoning medium --judge-model gpt-5.6-sol --judge-reasoning high --subject-cost-per-call-usd 0.208 --judge-cost-per-call-usd 0.40 --repetitions 1 --execute --output-dir ../cb12-candidate-evidence/skill-evals/cb12-fix-first-proof-accepted-final
  ```

- The first completed subject command was `/bin/zsh -lc 'cat
  .agents/skills/to-plan/SKILL.md'`; it exited 0. Captured output matched the
  staged entrypoint hash above on event `item_1`. Forced integrity is `valid`.
- The artifact validator returned 0. Objective grading and the judge passed;
  all five rubric criteria passed: `bounded-proof`, `failure-gate`,
  `repository-evidence`, `task-dependency`, and `planning-boundary`. No
  forbidden actions or violations were recorded.
- Usage: subject 182,496 input / 9,267 output tokens; judge 38,661 input / 871
  output tokens; no retries.
- Human audit: **accept**. Raw `results.json` SHA-256:
  `ddda11e3aa57aee27d6dc08773b164259a6ca806fd6cc0994e72c72bfdd6667d`.

## No-proof countercase

- Run ID: `to-plan-authorized-draft-direct:forced:1`
- Run fingerprint: `77b380ab472598c32d64fd83bd0d45a6eeaa36be87ac337d2b9bc8b905d9a193`
- Case digest: `653b65ff0aca5b3b0d82653b9ac82414d8cec435c01cac13a904acdbfef17b69`
- Same subject, judge, reasoning, CLI version, and cost inputs as the proof
  case. Cost estimate: `$0.608` for one subject and one judge call.
- Command:

  ```sh
  python3.13 evals/run.py run --suite workflows-writing --case to-plan-authorized-draft-direct --arm forced --model gpt-5.6-terra --reasoning medium --judge-model gpt-5.6-sol --judge-reasoning high --subject-cost-per-call-usd 0.208 --judge-cost-per-call-usd 0.40 --repetitions 1 --execute --output-dir ../cb12-candidate-evidence/skill-evals/cb12-fix-first-countercase
  ```

- The first completed command read the captured staged `to-plan/SKILL.md`;
  forced integrity is `valid`. Its artifact validator, objective grading, and
  all five rubric criteria passed. No forbidden actions or violations were
  recorded.
- Usage: subject 224,184 input / 4,536 output tokens; judge 35,535 input / 1,008
  output tokens; no retries.
- Human audit: **accept**. Raw `results.json` SHA-256:
  `cfc78df638fa9474a57ee55267b20867c4576a80204c30733e15275b2616276c`.

## Harness diagnosis and limits

Codex emits the first standalone read as a shell wrapper (`/bin/zsh -lc
'cat …'`), while the forced-evidence checker previously accepted only bare
`cat`. The checker now unwraps that exact shell form and still rejects
compound commands; a regression test covers both. Earlier proof attempts had
valid observed reads but failed case validation or rubric requirements and
were audited as rejected. The accepted proof prompt now states the required
`os.replace` proposal, current `published.write_bytes(contents)` behavior, and
the template's exact T1 → T2 → T3 dependency syntax.

Each accepted case has one forced repetition only. These results do not compare
arms or establish repeatability. The fixture is synthetic and cannot establish
that the actual target runtime permits cross-mount replacement; the bounded
runtime proof remains unrun.
