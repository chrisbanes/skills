# GPT-6 alternate-CLI targeted rechecks

These are targeted live runs with `gpt-6-luna/high` as subject and
`gpt-6-sol/high` as judge. They used the ChatGPT-bundled Codex CLI
`0.155.0-alpha.16` because the installed Homebrew CLI did not finish its
`--version` preflight. The CLI change gives these records a separate fingerprint
from the frozen complete-suite run. The per-call cost figures were planning
assumptions, not measured billing.

| Case and revision | Forced | Automatic | Raw output |
| --- | ---: | ---: | --- |
| Compose state hoisting direct, `0aa790e` | 3/3 | 3/3 | `/private/tmp/gpt6-compose-state-hoisting-alt-cli-3rep` |
| Shepherd novel, `0aa790e` | 3/3 | Ineligible | `/private/tmp/gpt6-shepherd-novel-alt-cli-3rep` |
| Release direct, `0aa790e` | 2/3 | 2/3 | `/private/tmp/gpt6-release-direct-alt-cli-3rep` |
| Grounded writing direct, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing novel, `ab748e1` | 1/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing no-change, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Release direct after ledger-order repair, `15415a2` | 3/3 | 2/3 | `/private/tmp/gpt6-release-direct-ledger-alt-cli-3rep` |
| Grounded writing direct after shared-contract repair, `15415a2` | Not run | 3/3 | `/private/tmp/gpt6-writing-direct-contract-alt-cli-3rep` |

The Compose revision fixed the observed preview-tooling scope miss in all six
targeted repetitions. The shepherd check-inventory revision passed all three
forced repetitions. Neither result establishes a complete-suite score.

In the pre-ledger release run, one forced and one automatic subject placed
bounded streaming only in prerelease history, omitting it from the final stable
summary. The revised release procedure drafts the stable summary from surviving
coverage-ledger rows before grouping history. Its recheck fixed that omission
in all six packets. The remaining automatic packet passed the deterministic
changelog validator but failed the judge's approval-handoff criterion: it
called the known publishing mechanism pending and referred to notes “shown
below” without presenting them there. The original judge verdict is retained.

The writing triad on `ab748e1` exposed three distinct issues. Two automatic
direct rewrites dropped the supplied shared public API guarantee; the later
shared-contract guidance passed a three-repetition automatic direct recheck.
Two forced and two automatic novel reviews still omitted some combination of
the conditional return-to-Full behavior, setting choice, or practical trade-off.
Two automatic no-change subjects made unnecessary edits to an adequate internal
report. The objective restraint failures stand even when the judge accepted the
content. The novel and no-change misses remain open; there is no post-repair
full writing triad.

All rows are combined objective-and-judge outcomes from the raw results, not
regraded or rejudged values. Each listed run has a uniform skill source SHA and
catalog digest within that run. Do not splice rows into a new suite score or
replace the README result tables from these focused probes.

Before a full rerun, repair and recheck the grounded-writing novel and no-change
cases, and resolve the release approval-handoff miss. At the current planning
assumptions, a three-suite, three-repetition run requires 693 subject and 693
judge calls and estimates $145.53; this is not a quoted price or an approved
spend. Keep the frozen full-suite results as the latest complete-suite evidence
until a new uniform-head run finishes and its failures are audited.
