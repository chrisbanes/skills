We shipped a faster import flow.

The p95 fell from 1.8 seconds to 1.1 seconds in the release benchmark. The
change removes a duplicate parse, but we still need production data before
claiming that every project will see the same improvement.
