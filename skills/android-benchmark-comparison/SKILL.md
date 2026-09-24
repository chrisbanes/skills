---
name: android-benchmark-comparison
description: Use when comparing physical Android benchmark configurations, investigating inconsistent rankings, or selecting an Android default from measured results. Do not use for code-level Compose performance diagnosis without a configuration comparison.
---

# Android benchmark comparison

## Core principle

Treat a physical Android configuration comparison as a reproducible experiment:
verify comparable workloads and device conditions before interpreting a ranking
or choosing a default.

## Procedure

1. State the decision, configurations, workloads, metric definitions, and
   repetitions. Preserve exact build identity, configuration, raw results, and
   traces; then verify every intended case and iteration ran. Distinguish
   missing, failed, and excluded runs; do not compare only the fastest
   survivors.
2. Control and record relevant device conditions, including device model and
   state, thermal and power mode, display brightness, background load, and
   network or input conditions. Keep device-specific commands and CPU masks in
   the project's runbook.
3. Balance or reverse run order and repeat the comparison. Report the spread
   and whether the ordering holds; do not discard slow iterations after seeing
   the result.
4. When rankings reverse or variability is material, defer a firm default
   decision until the reversal is resolved. Give the complete next comparison,
   not just its first blocker: confirm the same named cases and iterations,
   repeat with balanced or reversed run order, and inspect trace data whose
   timestamps overlap each measured interval for placement, contention, or
   thermal changes. Fixed-performance mode does not
   prove CPU placement. If an affinity experiment was attempted, discover the
   device topology and verify placement during the measured interval. Restore
   the recorded original affinity settings after the experiment and verify that
   restoration before another run; do not merely note that restoration needs
   checking. Label verified affinity runs as controlled comparisons. If the
   original settings or any other check are unavailable, state the gap and keep
   any default choice explicitly provisional.
5. Calculate summaries from unrounded observations, then round only for
   presentation. Name the aggregation explicitly: the mean of per-run
   percentiles is not a percentile of pooled observations. Choose an
   aggregation that answers the stated decision; do not prescribe one statistic
   universally.
6. Separate controlled-experiment evidence from normal user performance. If
   several conditions changed together, report the comparison as more
   controlled but do not attribute its whole difference to one control. Use
   CPU frame-duration evidence to inform a visual quality/performance decision,
   without claiming it measures GPU shader time.
7. Finish with the raw-evidence location, completed-case counts, variability,
   trace findings, controls and restoration status, plus the bounded decision
   or remaining uncertainty. When a reversal is unresolved, state the full
   sequence still needed: matching coverage, balanced or reversed order,
   measured-interval trace inspection, and restoration of any changed affinity
   settings. Name *run order* explicitly in the recommendation: a "balanced
   comparison" alone does not tell the team to balance or reverse run order.
   Label any earlier default choice provisional.

## Boundaries

- A single stable benchmark run can support a narrow observation, but not a
  robust configuration ranking.
- Do not turn a device-specific CPU mask, brightness value, iteration count, or
  summary statistic into a permanent default.
- When traces or repeat coverage cannot resolve a reversal, keep the default
  unchanged or make a provisional decision with that limitation explicit.
