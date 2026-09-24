Create one concise local implementation plan for this repository. Planning only:
do not edit source files or contact a provider. The task is to quote paths in two
diagnostics while preserving spaces exactly and using the same single-quote
formatting contract at both call sites.

The fixture contains an existing `manifest_reader.py:missing_manifest_error`
call site that returns `manifest not found: {path}`, and an existing
`profile_loader.py:invalid_profile_error` call site that returns
`invalid profile at {path}`. Add a shared `path_diagnostics.py:quote_path`
helper that wraps the supplied path in single quotes. Keep each diagnostic's
prefix and public function signature unchanged. A path such as
`configs/team manifest.json` must be preserved in the exact output, including
the spaces and quotes.

Plan two focused, test-first increments. The first introduces the shared helper
and applies it to the missing-manifest call site. The second applies the same
helper to the separate invalid-profile call site. Give each slice its own
observable result, exact test input and output assertion, focused command from
the fixture root, expected red failure, and green completion condition. Map
both requested behaviors to acceptance rows and their proving slice/check.
Write the plan now.
