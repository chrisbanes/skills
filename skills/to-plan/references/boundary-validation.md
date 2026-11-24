# Boundary validation

Validate consequential boundaries before dependent work relies on them.

1. For consequential persistence, privacy or asynchronous boundaries in the
   planned behavior, put meaningful validation in the observable slice that
   establishes the boundary. Identify the relevant production path, observable
   success/failure and recovery or disclosure outcome from the accepted contract;
   make dependent slices require that evidence before they start.
2. Reuse existing trusted evidence when its inputs and scope apply. Use a separate
   proof only for an unsettled material assumption under to-plan's planning
   procedure, not for every boundary or ordinary edit.
3. Hold dependent work when required boundary evidence is missing or fails.
   Return the defect to its owner under existing repair gates. Release dependent
   work only when prerequisite integration and applicable boundary checks pass.
