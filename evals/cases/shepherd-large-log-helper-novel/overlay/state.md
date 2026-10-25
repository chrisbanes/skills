# Immutable evaluation state

A selected PR has a 90000-line failed CI log at candidate abc1234. The controller has already read the PR state and identified one question: which build step first fails with ENOSPC before the test failures cascade?
A reviewer profile can read only the local checkout. A generic read-only helper can read the exact failed log and return line references, the first failing step, its error and uncertainty. The controller retains the checkout and all mutation authority.
The lead is Sol/high. The user policy selects Luna/low for exact evidence extraction without judgment; this helper only locates the first ENOSPC build-step evidence, while the controller decides cause and repair. An alternative helper profile explicitly pins Sol but leaves reasoning unspecified.
The draft asks the helper to poll all PRs, classify every review comment, repair the failure and push a fix.
