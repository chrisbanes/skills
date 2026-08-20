Refactor refresh so its completion, cancellation, result, and failure are observable to the caller. Preserve the API call to fetch the user and avoid adding lifecycle machinery.
