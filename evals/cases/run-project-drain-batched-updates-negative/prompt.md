Use only supplied synthetic state and applicable skill references. All identity and configuration reads are complete. Trusted repository instructions opt in regenerating Markdown indexes under `docs/indexes/*.md` and specify how to apply and verify them. The change is independently shippable and outside the main build unless a snapshot states otherwise.

- next: a board `next` ticket changes a component and would regenerate its eligible index.
- named-issue: the user explicitly asks for one issue outside a board run. Its fix would regenerate the same eligible index.
- no-opt-in: a `drain` fix has a normal Unreleased entry in `CHANGELOG.md`. The repository has no deferral rule for that file.
- build-input: in a `drain`, the opted-in file `docs/indexes/components.md` is an input to a required packaging build for this ticket.
- conflicting-rules: in a `drain`, the proposed `docs/indexes/formats.md` edit matches two active deferral rules with different regeneration inputs and no priority between them.
- same-pr: in a `drain`, trusted instructions require the generated index change in the same PR as the feature using it, even though its path matches the batching rule.
- standalone: in a `drain`, the complete ticket deliverable is correcting one opted-in index. There is no independent change to merge.

For each snapshot, write edit_in_ticket_pr and defer_update, both booleans. Do not execute delivery, contact providers, start agents or write files, including scratch artifacts.

Put only the exact decision JSON object in the final structured response's `summary` string, with no Markdown fences or prose. Put supporting reasoning in `evidence`.
