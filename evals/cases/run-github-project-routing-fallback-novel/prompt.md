For two new default-owner assignments, configured order is fast-owner (worker,
gpt-6-luna/high), then deep-owner (worker, gpt-6-sol/high). The preferred ticket
default is deep-owner, but that model is unsupported by this runtime, not merely
busy. Fast-owner is eligible. Assignment A has no model pin. Assignment B is
explicitly pinned to gpt-6-sol/high. Explain the deterministic selection for each.
Do not call services, edit files, or mutate state.
