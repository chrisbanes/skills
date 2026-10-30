Read-only: review the changelog handoff for preparing Kotlin library release 2.0.0, followed by 2.0.1-SNAPSHOT. Use only the supplied state. Do not run commands, edit files, contact providers, mutate Git, load credentials or publish. Show the notes and remaining release gates; do not ask to publish now.

Published modules apply com.vanniktech.maven.publish through a convention plugin. Publishing route, coordinates and destination are not yet supplied. Repository checks are unit tests, Metalava API generation and compatibility. API files are Metalava api/api.txt files. No passing candidate-specific check evidence has been supplied.

The complete stable cycle is based on ancestor tag 1.4.0, followed by 2.0.0-alpha01 and 2.0.0-rc00. Alpha added streaming with unbounded buffering; RC superseded that with bounded buffering. Since RC, request cancellation was fixed. There are no other changes in this supplied range.

The proposed notes below already cover both final behaviors. Repository evidence verifies chrisbanes as maintainer and Avery Example as non-maintainer. PR URLs, author/profile facts below are verified supplied evidence. The renderer supports HTML details. Changelog finalization belongs to the release helper; keep Unreleased until that step.

## Unreleased

- Add streaming responses with bounded buffering ([#812](https://github.com/chrisbanes/skills/pull/812), by maintainer chrisbanes).
- Fix request cancellation so underlying work stops ([#845](https://github.com/chrisbanes/skills/pull/845), by [Avery Example](https://github.com/avery-example)).

<details>
<summary>Prerelease history</summary>

## 2.0.0-rc00

- Streaming responses now use bounded buffering.

## 2.0.0-alpha01

- Add streaming responses with unbounded buffering.

</details>

## 1.4.0

- Initial stable API.
