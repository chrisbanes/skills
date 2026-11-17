# GitLab code-host binding: bounded live check on gitlab.com

Status: **passed, with the limits below.** Run `20261117213248-3d36` (attempt 1
of 2) passed both journeys, used 13 of 16 provider writes including one merge
into a run-owned base branch, saw no 429, and verified its own cleanup. The run
had **0 model turns**.

Contract: [issue #158](https://github.com/chrisbanes/skills/issues/158) and its
[approved plan](https://github.com/chrisbanes/skills/issues/158#issuecomment-6960763338),
implemented by `references/gitlab-binding.md`. Harness:
`scripts/gitlab_code_host_live_check.py` at `62e4422a0420e7147408c5b83cc2011c09e1c662`,
authorized explicitly by the maintainer before any write.

## Command

```sh
env -u GITLAB_TOKEN -u GITLAB_ACCESS_TOKEN -u OAUTH_TOKEN -u GLAB_CONFIG_DIR \
  python3 scripts/gitlab_code_host_live_check.py --live --result <absolute scratch path>
```

The credential was the `glab:gitlab.com` login. No credential was printed or
stored: the result keeps statuses, counts, identifiers and rate-limit headers
only. The result file stayed outside the repository and is transcribed here.

## Guard

At most 16 writes and 2 write attempts; reads only under project `88319115`
(`banes3/Banes-project`) plus `user` and `version`; writes only to the run base
branch, the two run task branches and the merge requests the run recorded;
refusal of auto-merge keys, any `merge_trains` path, a second merge, writes to
`main`, a login other than account `43935395`, and credential-override
variables. `guard.denied` was empty.

## Fixture identities

- gitlab.com `19.6.0-pre`; account `43935395`; project `88319115`.
- `main` tip before and after the run: `d66002663caa41d45ffb0780bde5d1d20dd8e602` (unchanged).
- Merge-policy fingerprint `7c8bdc7b906f28c021adffb2262d36f21cc86b7165c6b659b3e3e14b381ebc4e`:
  `merge_method: merge`, `squash_option: default_off`, both `only_allow_*`
  false, `merge_trains_enabled`, `merge_pipelines_enabled` and
  `allow_merge_on_skipped_pipeline` recorded as `unavailable` (null on Free),
  `main` protected with Maintainer push and merge, no force push, no code-owner
  approval, `approval_rules: []`, `approvals_before_merge: 0`.

## Results

| Step | Result |
| --- | --- |
| Preflight: account, project identity by ID and path, fingerprint, `main` read-only | passed, 0 writes |
| Journey A: commit with `FAIL_PIPELINE`, draft MR !14 targeting the run base, `closes_issues` empty | passed |
| Journey A: MR pipeline `3081261429` read through `merge_requests/:iid/pipelines` reported `failed` | passed |
| Journey A: discussion, reply, resolve, readback of two resolved notes; approvals read | passed |
| Journey B: draft MR !15; merge refused with zero writes while draft (`detailed_merge_status: checking`) | passed |
| Journey B: ready by removing the `Draft: ` title prefix, readback `draft: false` | passed |
| Journey B: pipeline `3081263116` `success`, status `mergeable`, merge with `sha` and `squash: false` only | passed |
| Merge readback: `state: merged` at head `c133469715e20dbc91690cf12af2cb75f07e8da2`, merge commit `5b7eed5d940758ba5fe3446474536cb47632d256` is the run-base tip | passed |
| Cleanup: !14 `closed`, !15 `merged`, all three run branches 404 on readback | verified |

Writes: **13 of 16**, 1 merge, 48 API requests. In order: create run base;
commit, create MR, discussion, reply, resolve (A); commit, create MR, ready,
merge (B); close !14, delete A's branch, delete the run base. GitLab removed
B's merged source branch itself (`remove_source_branch_after_merge: true`), so
cleanup found it gone and sent no delete.

## Contract findings

- A freshly created draft reported `detailed_merge_status: checking`, not
  `draft_status`. The binding's merge operation now re-reads transient
  statuses with bounded polling; the draft flag alone already refuses.
- The merge-request pipelines endpoint returned the branch pipeline for the
  head, so no `pipelines?sha=` fallback was needed.

## Limits of this evidence

- Merge into a protected branch is **not live-qualified**: the run merged only
  into its own unprotected base branch and only read `main`'s settings.
- gitlab.com Free at `19.6.0-pre`. It does not prove any self-managed version,
  edition or settings; merge trains and approval rules are covered by eval
  fixtures only, because the fixture has merge trains unavailable and no
  approval rules.
- One personal project, no concurrent human activity, one page of discussions,
  no 429 or restart in the live run.
- Persistent residue: closed !14 and merged !15 with their notes and
  pipelines. The merge landed only on the deleted run base, so `main` is
  unchanged.
