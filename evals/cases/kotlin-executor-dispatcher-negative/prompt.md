Review the single-thread codec boundary and edit only if its concurrency
ownership is wrong. Preserve required thread affinity and avoid replacing a
correctly owned dispatcher merely because it wraps an executor.
