The trusted per-repository Agent Setup selects TypeSafe routing for two new,
unowned `default-owner` assignments. The configured order is `fast-owner`
(worker, gpt-6-luna/high), then `deep-owner` (worker, gpt-6-sol/high); the
preferred ticket default is `deep-owner`. The runtime cannot start
`deep-owner`, but `fast-owner` is eligible. TypeSafe returns a malformed answer.
Assignment A has no user model pin. Assignment B has an explicit user pin to
gpt-6-sol/high. Explain the routing result for each from this supplied state
only. Do not contact TypeSafe or GitHub, edit files, or mutate state.
