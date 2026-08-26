# GitHub Mode

Read this reference after selecting GitHub mode. The common workflow and finish
gates in `SKILL.md` still apply.

## Build the source packet

Fetch live GitHub state and read:

- The complete issue body and every comment.
- Any linked specification or parent issue.
- Official blockers and any textual `Blocked by` contract.
- Completed blockers and their delivered outcomes.
- Linked or closing pull requests.

When an earlier conversation established the issue, inspect later trusted user
messages only for a revoked or replaced target or a changed stakeholder
contract. Require every stakeholder-contract change to be recorded in the live
issue, specification, or ADR; otherwise block pending an upstream update. Do not
switch to conversation mode or request another compact confirmation.

Treat acceptance criteria and recorded upstream decisions as authoritative.
Compatible comments may clarify them. Block on unresolved conflicts between
authoritative sources.

Find all comments containing either plan marker, including minimized comments:

```html
<!-- to-plan:implementation-plan:v1 -->
<!-- to-plan:implementation-plan:v2 -->
```

Treat v1 as a revision-one root. For v2, parse the positive revision,
`Supersedes` permalink or `none`, and `Replan report` permalink or `none`.
Require one root, contiguous revisions, at most one child per revision, and one
unminimized leaf. Verify that the active GitHub identity authored every marker
comment and can create the next revision. A fork, gap, duplicate, missing
predecessor, foreign marker, or minimized active leaf is a blocker.

When the active plan is already claimed, accept an autonomous replan only from
a runner-owned comment containing:

```html
<!-- run-github-project:replan-request:v1 -->
```

Verify its author, disposition, previous plan permalink and digest, base, and
retained implementation evidence. Permit only the exact linked implementation
PR and retained work named by that report. Competing, foreign, or mismatched PRs
still block.

An unmarked implementation plan is context, not an editable target. Block when
it conflicts with the proposed plan or could be mistaken for the active
execution contract.

## Enforce readiness

Require all of the following:

- The issue is open and labelled `ready-for-agent`.
- Every blocker is complete and its required outcome exists in the baseline.
- No open implementation PR exists, except the exact runner-owned PR allowed by
  a verified autonomous replan.
- The issue has explicit, complete acceptance criteria.
- Every criterion maps to automated or precise manual verification.

Inspect the baseline rather than inferring delivery from a closed blocker.
Return all readiness failures together and do not draft while any remain.

## Refresh before publishing

Immediately before any GitHub write, refresh:

- Issue state, body, comments, label, blockers, and implementation PRs.
- `HEAD` and the complete working-tree path inventory. Reinspect every entry
  whose earlier exclusion required reading its contents, even when its path and
  status are unchanged.
- Plan markers, minimized state, revision edges, active-leaf permission, and any
  autonomous replan report.

Reapply readiness and overlap checks. Retain baseline evidence only while
`HEAD` matches the planned SHA. If `HEAD` moved, inspect the committed delta,
rerun checkout identity and affected checks, and update the SHA only after they
pass.

Refresh incidental metadata without renewed approval. When decisions, slices,
files, tests, commands, coverage, guardrails, deviations, or review focus
change, update the draft while preserving compatible user edits. Normal mode
requires approval again; `--auto` revalidates and continues.

## Publish and verify

Plan comments are the only GitHub state this skill may mutate. Never change the
issue body, labels, assignee, relationships, Project fields, status, or any
non-plan comment.

Compute a semantic payload digest without the marker, revision metadata, or
superseded wrapper. If the active leaf already has the same payload and
baseline, perform no write, delete only an exact matching temporary draft after
verification, and return the leaf as a no-op. Otherwise:

1. Create one v2 comment with revision one and `Supersedes: none`, or the active
   revision plus one and its permalink. Include the verified replan-report
   permalink when applicable.
2. Refetch marker comments and verify the new author, exact body, digest,
   revision, predecessor, report link, branch, SHA, and publication time. If
   creation times out, perform bounded reconciliation by exact revision and
   digest before retrying.
3. Require one root, no fork or gap, and the new comment as the unique
   unminimized leaf.
4. Minimize the predecessor as `OUTDATED`. If unavailable, edit only that
   runner-owned predecessor to add a superseded-by link and wrap its unchanged
   payload in `<details>`, then verify its digest. Report failure of both
   presentation methods without invalidating the verified new leaf.
5. Delete only the exact draft after the active leaf is verified.

Never edit an active semantic payload in place, split one revision across
locations, or perform broad `.scratch` cleanup. Preserve the draft whenever
publication or active-leaf verification fails.
