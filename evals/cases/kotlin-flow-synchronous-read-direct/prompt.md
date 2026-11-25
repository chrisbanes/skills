Review the display-name API. A caller needs the trimmed name on the very next
synchronous read after update returns, even before the sharing coroutine runs.
Existing observers can tolerate delayed cache updates. Explain how the current
sharing policy behaves with no subscribers and immediately after a write.
Recommend the smallest change that supports both uses without editing files.
