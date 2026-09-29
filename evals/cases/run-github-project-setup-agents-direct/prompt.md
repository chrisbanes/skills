An existing repository has a committed GitHub Project workflow binding and
trusted instruction reference. Its Project and repository IDs match complete
live reads, and it already uses the required Status schema. The binding lacks
the required execution approver login; the user supplies `alice` for that
value. It also has no Agent Setup section and no active claims. The user asks
to run `setup` to bring the existing binding up to date and add agent
configuration, but specifies no role or model preferences. The runtime
supports a default-owner worker with runtime-default model and reasoning.
Explain the setup changes and result from this supplied state only. Do not
contact GitHub, edit files, commit, or mutate Project state.
