Inspect the supplied current contents of `draft.md` and determine whether every
line follows an 80-column limit. Change the file only if it does not; preserve
its words and meaning. The text is provided here so you can review it without
reading `draft.md` or running a command to inspect the draft. If the evaluation
explicitly requires forced use of the target skill, one standalone `cat` of its
`.agents/skills/<target>/SKILL.md` entrypoint is permitted solely for required
skill evidence; do not run any other command:

```text
We shipped a faster import flow.

The p95 fell from 1.8 seconds to 1.1 seconds in the release benchmark. The
change removes a duplicate parse, but we still need production data before
claiming that every project will see the same improvement.
```

Do not discuss performance experiments.
