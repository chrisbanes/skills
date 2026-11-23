Use only supplied synthetic state and applicable skill references. Return the decision JSON in your response with exactly the named snapshots and fields below. Do not execute delivery, contact providers, start agents or change other files.

The repository keeps `CHANGELOG.md` with an Unreleased section; its trusted `AGENTS.md` asks for an issue-linked Unreleased entry for each user-visible change and says nothing about which PR adds it. No drain is requested in either snapshot. All identity and configuration reads are complete.

- next: a board `next` invocation selected eligible #401, a user-visible fix with a verified plan, and its owner is about to open the PR. Write changelog_in_ticket_pr (whether #401's PR edits `CHANGELOG.md`) and batch_pr (whether the controller opens a separate changelog PR), both booleans.
- named-issue: the user asks this skill to deliver named issue #402, a user-visible fix, outside any board run. Write changelog_in_ticket_pr and batch_pr (booleans).

This is a no-change assessment: write no files, including scratch artifacts.

Put only the exact decision JSON object (no Markdown fences or prose) in the final structured response's `summary` string; put supporting reasoning in `evidence`.
