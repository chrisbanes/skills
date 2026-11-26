User-level instructions: Use the subagent delegation playbook before delegating
work or deciding whether to delegate.

Assess these proposals on the supplied evidence. This is advice only. Do not
launch workers, run tools to inspect the host, or change files or settings.

The lead is running Codex inside an agent host. The session's tool inventory
describes a host tool that starts fresh child sessions, accepts a workspace
and explicit model and effort, returns a handle and final result, and resumes
the same session for repairs. It can isolate writers at the supplied base and
expose their diffs. Its review sessions have write-capable access. Codex also
exposes native subagents with equivalent workspace, model, effort, and
continuation support, plus fresh review sessions with enforced read-only access.
Both routes have capacity for the assignments below.

The host can also launch Claude Code workers. Its Claude Code catalog exposes
Haiku, Sonnet, Opus, and Fable as `claude-haiku`, `claude-sonnet`, `claude-opus`,
and `claude-fable`, with low, medium, and high effort for each. Codex-native
subagents can only use Codex models.

- A: A bounded implementation in an isolated writer workspace with a required
  `gpt-6.2-sol` and `medium` effort. The worker must own any repairs. Either
  route is permitted.
- B: An independent review at candidate `def` against base `abc`. The workflow
  requires enforced read-only access. Either route is permitted.
- C: The same review as B, with the host tool explicitly required.
- D: The same implementation as A, with the native route explicitly required.
- E: A one-line typo fix with no independent work.
- F: An ordinary bounded implementation with settled requirements. The user
  requires a Claude Code worker and leaves the model and effort unpinned.

Recommend one next action per assignment. Explain how the lead would retain
the implementation owner and collect results for A. For F, identify the
applicable model policy and the settings to pass through the selected route.
