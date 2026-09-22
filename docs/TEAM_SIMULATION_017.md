# Team simulation 017 — repeatability A1/A2/A3 vs B1/B2/B3

This is a software/test simulation, not vehicle evidence.

## Model
Three NORMAL trials contain only synthetic 0x100 around START. Three FAULT trials additionally contain synthetic 0x200 at +420 ms and 0x300 at +440 ms. Absolute START times differ in every file.

## Expected
After per-session START alignment, NEW_ID 0x200 and 0x300 are observed in all three FAULT trials. The engine reports 3/3 FAULT repeatability and keeps the interpretation descriptive. No ECU owner or root cause is assigned.

## Review perspectives
- Diagnostic: repeated B-only observations are stronger targets for the next test than a one-off A/B difference.
- CAN/data: every session must have its own START marker; absolute clocks are irrelevant after alignment.
- Evidence: REPEATED IN ALL B means reproducible observation, not causal proof.
- Reliability: a DATA LOSS trial should be visibly treated as limited evidence in the next refinement.
- UX: operator numbers captures A1/A2/A3 and B1/B2/B3; analysis remains unavailable until at least two trials exist in each class.

## Failure paths
Missing numbered trials -> analysis rejected.
Missing START marker -> analysis rejected.
One-off event -> PARTIAL, not repeated.
Unknown CAN ID -> remains unknown.
Different START timestamps -> normalized per session.
