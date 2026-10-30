Prepare the stable changelog notes for 2.0.0 in this TypeScript library. Update only CHANGELOG.md; finalize the 2.0.0 heading and its prerelease history, leaving publication for the later release step. Report the reviewed scope and any evidence or coverage gaps. This is changelog maintenance, not release preparation. Do not run publishing, Git mutations or read real credentials.

The previous stable ancestor tag is 1.4.0. Later ancestor tags are 2.0.0-alpha01 and 2.0.0-rc00. The complete changes since 1.4.0 are:
- 2.0.0-alpha01 added streaming responses.
- 2.0.0-rc00 changed streaming responses to use bounded buffering; the alpha behavior is superseded.
- Since rc00, public request cancellation now stops the underlying work (regression fix).
- The bounded buffering change is PR #812 by repository maintainer `chrisbanes`: https://github.com/chrisbanes/skills/pull/812
- The request cancellation fix is PR #845 by contributor `Avery Example` (`avery-example`): https://github.com/chrisbanes/skills/pull/845; profile: https://github.com/avery-example
- Repository evidence lists `chrisbanes` as a maintainer and does not list `avery-example` as a maintainer.
- Existing curated entry describes the other consumer-visible change accurately.
- Rename internal helper, with no observable behavior change.
The current Unreleased section is in CHANGELOG.md.

This repository has no Kotlin build or Gradle publishing plugin. No next development version has been selected; none is needed for this task.

The changelog renderer supports HTML details blocks. GitHub Release pages link back to this changelog and do not retain separate notes.
