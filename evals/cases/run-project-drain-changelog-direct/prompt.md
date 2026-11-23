Assess supplied complete GitHub Project state in review mode. A `drain` was explicitly requested and the user granted merge at startup. The repository keeps `CHANGELOG.md` with an Unreleased section; its trusted `AGENTS.md` says each user-visible change gets an Unreleased entry linked to its issue as an explicit Markdown link. It does not say where or in which PR the entry is added.

Three independent eligible tickets, #201, #202 and #203, have verified usable plans, no shared paths other than `CHANGELOG.md`, and user-visible changes.

- owner-202: #202's ticket owner has a reviewed implementation and is about to open its PR while #201 and #203 PRs are open. Write changelog_in_ticket_pr (whether the ticket PR edits `CHANGELOG.md`) and entry_in_pr_body (whether the proposed entry goes in a marked PR-body section), both booleans.
- after-last-merge: all three ticket PRs have merged with green required checks and no other eligible work remains. Write batch_pr (boolean), writer (controller or owner), entries (sorted ticket numbers whose entries it adds), independent_review (boolean), and merge_batch (boolean).

Explain where the controller records each proposed entry and how it verifies the links.

Write exact JSON decisions to `.scratch/review-decisions.json`. Use skill references; make no provider calls or described mutations.
