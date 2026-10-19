# GitHub Mode

Read this reference after selecting GitHub mode and the
[shared workflow](workflow.md). That workflow owns baseline, discovery, draft,
handoff, repair, and finish contracts.

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

Find all full-plan and integration-amendment marker comments, including
minimized comments. When amendments exist or are requested, apply
[integration amendments](integration-amendments.md) as well: the full-plan leaf
alone is not the effective contract. Full replans close the preceding amendment
epoch with its exact effective tip/digest and retained-work disposition.

The full-plan markers are:

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

For a claimed-plan integration amendment, use the retained-owner/controller
request checks in that reference. For a full autonomous replan, accept only from
a runner-owned comment containing:

```html
<!-- run-github-project:replan-request:v1 -->
```

Verify its author, disposition, previous plan permalink and digest, base, and
retained implementation evidence. Permit only the exact linked implementation
PR and retained work named by that report. Competing, foreign, or mismatched PRs
still block.

A runner-authored revision headed `Fast path` is a valid predecessor from
`run-github-project`; supersede it with a full plan revision.

An unmarked implementation plan is context, not an editable target. Block when
it conflicts with the proposed plan or could be mistaken for the active
execution contract.

## Enforce readiness

Require all of the following:

- The issue is open and labelled `ready-for-agent`.
- Every blocker is complete and its required outcome exists in the baseline.
- No open implementation PR exists, except the exact retained PR allowed by
  a verified autonomous replan or integration amendment request, or named by a
  `deliver-spec` fast-path escalation record in that runner-authored PR.
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

Refresh incidental metadata and routine equivalent file, fixture or command
corrections under the existing scope and publication authority; preserve user
edits and revalidate affected evidence. Require renewed approval only for a
material change to the accepted outcome, coverage, architecture or authority.
`--auto` revalidates within its existing grant, never expands it. For delivery
corrections that need no published decision change, use the shared workflow's
brief correction record instead of creating a new plan revision.

## Publish and verify

Plan comments are the only GitHub state this skill may mutate. Never change the
issue body, labels, assignee, relationships, Project fields, status, or any
non-plan comment.

### Payload digest

Every full-plan and runner-marker payload digest uses this one form, so any
agent and any tool reproduces it:

1. Start from the comment's `body` string as decoded from the API JSON.
2. Replace each CRLF with LF.
3. For a `to-plan:implementation-plan` comment, drop every line before the
   first `## Implementation plan` line (the marker, revision metadata and any
   superseded banner or `<details>` opening), and drop a final `</details>`
   line. Every other marker comment keeps its whole body.
4. Strip all trailing LF characters. This absorbs the newline that tools such
   as `jq -r` add.
5. Hash the UTF-8 bytes with SHA-256 and record lowercase hexadecimal with no
   prefix.

For example, the body
`<!-- to-plan:implementation-plan:v2 -->\r\n\r\n**Revision:** 1\r\n\r\n## Implementation plan\r\n\r\nStep one.\r\n`
has the payload `## Implementation plan\n\nStep one.` and the digest
`bcce4e2c20ff2a6fa053e9560880d1491c6458c51ed25e4ad6aa0b847d6c4da7`.

The complete `Epoch closure` line, including retained-work and evidence
dispositions, is semantic payload: always include it in the digest, never
discard it as revision metadata.

### Publication

If the active leaf already has the same payload and
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
   runner-owned predecessor to add a superseded-by link and `<details>` opening
   before its `## Implementation plan` line and a final `</details>` line,
   leaving the payload unchanged, then verify its digest. Report failure of both
   presentation methods without invalidating the verified new leaf.
5. Delete only the exact draft after the active leaf is verified.

An amendment is a separate append-only component of one effective contract,
not a split full-plan revision. Apply its publication and no-op gates separately.
Never edit an active semantic payload in place, split one full-plan revision across
locations, or perform broad `.scratch` cleanup. Preserve the draft whenever
publication or active-leaf verification fails.
