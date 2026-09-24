Prepare the changelog portion of releasing 2.0.0, followed by 2.0.1-SNAPSHOT. Update only CHANGELOG.md; finalize the 2.0.0 heading and its prerelease history, leaving publication for the later release step. Identify any remaining release gates in your response. Do not run publishing, Git mutations or read real credentials.

The previous stable ancestor tag is 1.4.0. Later ancestor tags are 2.0.0-alpha01 and 2.0.0-rc00. The complete changes since 1.4.0 are:
- 2.0.0-alpha01 added streaming responses.
- 2.0.0-rc00 changed streaming responses to use bounded buffering; the alpha behavior is superseded.
- Since rc00, public request cancellation now stops the underlying work (regression fix).
- The bounded buffering change is PR #812 by repository maintainer `chrisbanes`: https://github.com/chrisbanes/skills/pull/812
- The request cancellation fix is PR #845 by contributor `Avery Example` (`avery-example`): https://github.com/chrisbanes/skills/pull/845; profile: https://github.com/avery-example
- Repository evidence lists `chrisbanes` as a maintainer and does not list `avery-example` as a maintainer.
- Existing curated entry describes the other consumer-visible change accurately.
- Rename internal helper, with no observable behavior change.
The current Unreleased section is in CHANGELOG.md. API files are Metalava-generated `api/api.txt` files. Repository checks are unit tests and Metalava API generation and compatibility; no passing evidence for the candidate has been supplied.

The published modules apply `com.vanniktech.maven.publish` from `gradle-maven-publish-plugin` through the repository convention plugin.

The changelog renderer supports HTML details blocks. GitHub Release pages link back to this changelog and do not retain separate notes.
