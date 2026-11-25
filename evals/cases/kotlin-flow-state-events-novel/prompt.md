Review the state and navigation streams for lifecycle, replay, and delivery.
There is one navigation collector at a time. It can be cancelled during
handling, and every unhandled request must remain available when a replacement
collector starts in the same model lifetime. Explain whether a single-consumer
`Channel` meets that requirement. Recommend the smallest safe repair, including
how the owner distinguishes multiple outstanding requests and how an
acknowledgement identifies the handled request. Explain what happens if handling
succeeds just before cancellation. Do not edit files.
