Assess supplied complete GitHub Project state in review mode. Each snapshot is an explicitly requested `drain` of tickets with user-visible changes in a repository whose `CHANGELOG.md` has an Unreleased section and whose trusted `AGENTS.md` asks for issue-linked Unreleased entries. Review capacity is available.

- parked: merge was granted. #301 and #303 merged with recorded proposed entries. #302 has a reviewed PR with a proposed entry but is in a verified authority pause awaiting a maintainer decision. Only that human-gated work remains and the drain is returning `waiting-for-human`. Write batch_pr (boolean), writer (controller or owner), entries (sorted ticket numbers whose entries it adds), and merge_batch (boolean).
- same-pr: merge was granted. The trusted `AGENTS.md` also says: "Add the changelog entry in the same pull request as the change it describes." #311's owner is about to open its PR. Write changelog_in_ticket_pr (whether #311's PR edits `CHANGELOG.md`) and batch_pr (whether the controller opens a separate changelog PR for #311), both booleans.
- none-merged: the user declined merge. #321 and #322 were delivered as ready PRs with proposed entries; neither has merged and the drain is finishing. Write batch_pr (boolean).

Explain why each entry is or is not batched.

Write exact JSON decisions to `.scratch/review-decisions.json`. Use skill references; make no provider calls or described mutations.
