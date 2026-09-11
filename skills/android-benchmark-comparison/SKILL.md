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
4. When rankings reverse or variability is material, investigate before making
   the decision. Use traces to check the measured interval and plausible
   causes such as CPU placement, contention, or thermal state. A fixed-
   performance setting does not prove CPU placement. If affinity is used,
   discover the device topology, verify placement during the measured trace
   interval, label the outcome a controlled comparison, and restore device
   settings afterwards.
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
   or remaining uncertainty.

## Boundaries

- A single stable benchmark run can support a narrow observation, but not a
  robust configuration ranking.
- Do not turn a device-specific CPU mask, brightness value, iteration count, or
  summary statistic into a permanent default.
- When traces or repeat coverage cannot resolve a reversal, keep the default
  unchanged or make a provisional decision with that limitation explicit.
