Tracker jira, site https://fixture.atlassian.net. Code host GitHub, repository acme/widgets. Each scenario is independent. The default agent-work role is ready-for-agent. All unmentioned relevant checks and grants in a snapshot pass.

- zero-transitions. A runner-assigned To Do issue has zero transitions to configured In Progress.
- multiple-transitions. A runner-assigned To Do issue has two available transitions to configured In Progress.
- required-fields. A runner-assigned To Do issue has one available transition to configured In Progress with a required field.
- assignment-only. To Do still matches after a skipped claim. The only evidence of ownership is assignment to the runner.
- moved-in-review. A retained claim has been moved by the user to In Review in the In Progress category. The label and runner assignment remain.
- marker-round-trip. A runner-authored v2 marker is in an ADF paragraph plus codeBlock. The new revision is a separate comment, verified as the successor. The predecessor has a linked paragraph and wraps its byte-identical codeBlock in an expand node.
- marker-fallback. The successor is verified, and the expand update was rejected. A fresh read confirms the runner still owns the intact predecessor.
- marker-warning. The paragraph fallback also fails definitively and predecessor and successor content are unchanged.

### Stored ADF shapes for marker-round-trip

Original predecessor body:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Implementation plan"}]},
    {"type": "codeBlock", "content": [{"type": "text", "text": "<!-- to-plan:implementation-plan:v2 -->\n\n**Revision:** 1\n**Supersedes:** none\n\n## Implementation plan\n\nConfirm the snapshot.  \n"}]}
  ]
}
```

Readback of the same predecessor after the separate successor is verified:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Implementation plan"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "Superseded by https://fixture.atlassian.net/browse/KAN-10?focusedCommentId=42"}]},
    {"type": "expand", "attrs": {"title": "Previous plan"}, "content": [
      {"type": "codeBlock", "content": [{"type": "text", "text": "<!-- to-plan:implementation-plan:v2 -->\n\n**Revision:** 1\n**Supersedes:** none\n\n## Implementation plan\n\nConfirm the snapshot.  \n"}]}
    ]}
  ]
}
```
