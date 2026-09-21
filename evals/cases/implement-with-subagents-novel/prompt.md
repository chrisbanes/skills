Two proposed changes share an atomic schema and cannot pass validation apart.
Review how they should be queued and repaired if acceptance fails. Do not mutate
the supplied state or contact a remote service.

Explain which implementation owner to use in each independent environment:
Claude Code with its built-in agents, OpenCode with its built-in agents, and Pi
with no delegation extension or package installed. Assume the required
implementation skills are available in each environment. For a fourth
environment, Pi has an extension exposing an editing agent named `worker`, but
each call starts a fresh session with no resume support. Assess whether that
environment can preserve the repair contract. Do not start agents or install
anything.
