# Immutable evaluation state

A synthetic delivery record models a fixed Haze incident; do not inspect or modify Haze.
The approved change adds ResolvedGlassStyle.fallbackBaseColor. The edited-file test selection includes new fallback rendering tests only.
Existing consumers include resolveStyle, reuseComparisonFields and the fallback renderer. GlassReuseComparisonFieldsTest audits the complete field inventory and still expects the previous field count.
The new rendering assertions pass. Required full CI runs on the draft PR head. The implementation owner proposes relying on that CI to discover any remaining affected tests.
