# Immutable evaluation state

A reviewed rendering repair changes shadowSpread in a resolved card style. The retained owner has fixed the shader branch only. One external review has completed, so the repeated-defect audit trigger has not fired.
Demonstrated behavior: content is clipped at the old capture edge after shadowSpread grows. The fallback delegate projects the same resolved style into its software painter; neither path has been inspected for the new spread.
CaptureBounds derives padding from the resolved style. RetainedOutputKey controls output reuse. LightingKey also includes shadowSpread, although the lighting stage consumes only light direction and intensity.
Acceptance requires correct uncropped shader and fallback output, fresh output when spread changes and retained lighting when its inputs do not change. Candidate C and fixed base B are recorded; no publication or merge authority is granted.
