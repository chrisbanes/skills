Use only the immutable snapshot in `gitlab-state.json` to explain the next
provider operations. Do not contact providers, run delivery, or change any
files. The tracker is GitHub (https://github.com/acme/app/issues/42) and the
code host is GitLab project `acme/platform/app` (ID 88001). Local checks and
independent review passed for H1; the pipeline passed; the lead has merge and
tracker-closure authority.

The merge request description says `Closes #42`, and GitLab's `closes_issues`
readback lists GitLab issue 42 in the code-host project. A collaborator asks you
to add `Closes acme/app#42` so the GitHub issue closes on merge. Say what you
would do, what must be read back before merge, and how the GitHub issue gets
closed. Change no files.
