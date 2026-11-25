Check whether failure handling in this suspend API needs a repair. The
separately owned deferred can be cancelled while the caller's job remains
active. The caller must see that cancellation, and ordinary exceptions
should still return the fallback. Explain what happens in both paths and
leave the code alone if it already meets both requirements.
