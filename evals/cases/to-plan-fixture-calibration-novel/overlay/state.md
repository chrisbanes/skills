# Immutable evaluation state

The confirmed source requires independent left/right peak limiting during an active crossfade and after completion on two audio backends. No source decision is pending. This is planning analysis only.
LimiterProfile gains ceilingDb. Existing profile consumers include encodeProfile and gainCacheKey; ProfileWireFieldsTest audits serialized field completeness. Their files are outside the proposed implementation edit list.
The proposed unfamiliar fixture holds a mixer handle across backend recreation, averages an entire silent-heavy track and sums left/right results. It currently changes the crossfade only after completion.
Only new target-runtime code can establish fixture sensitivity; there is no trusted applicable fixture evidence. Suppressing the left limiter is an available bounded fault.
The proposed task graph has T1 establish the fixture and T2/T3 expand left/right, active/completed and backend coverage. The author proposes running all three concurrently.
