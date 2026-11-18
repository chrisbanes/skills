Assess the independent snapshots in `gitlab-state.json`. Use the supplied
observations only. Do not contact either provider or change any files.
Put a JSON object directly in the final summary field. Use the scenario IDs
as keys, with exactly the fields listed below. Use lowercase hyphenated
decision strings, booleans for yes/no and numeric IDs for provider records.

Each scenario uses the common raw notes plus any additional notes it lists.
Return the lowercase SHA-256 of the decoded semantic payload for the matching leaf.
Use null when there is no verified active note.

- matching-leaf: activeNoteId, stripTransportFooter, write, payloadSha256
- ambiguous-create: action, noteId, retry
- presentation: action, activeNoteId, editPredecessor
- forked-chain: action, activeNoteId, retry
