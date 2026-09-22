# SherloCAN UI/UX direction

## Principle
The UI is an investigator's workbench, not a generic dashboard. It must visually separate observation from interpretation.

## Navigation
Overview → Capture → Network → Timeline → Evidence → Sherlock → Crash.

## Capture workspace
The primary screen is three layers:
1. Session health: source, state, traffic, queue/drop state.
2. Time domain: live activity, event markers, Flight Recorder windows.
3. Investigation: first observed change, evidence, unknowns and next test.

## Visual semantics
- UNKNOWN must be visible, never silently converted to healthy/faulty.
- Red is reserved for observed faults/data loss or explicit user FAULT markers.
- Hypotheses are visually different from measurements.
- Inferred network edges must differ from documented/measured edges.
- ECU ownership is never inferred from a raw CAN ID without evidence.
- Read-only state is permanently visible during capture.

## Event workflow
MARK FAULT → preserve pre/post Flight Recorder window → detect changes → INVESTIGATE EVENT → Evidence/Hypotheses → Next Discriminating Test → WHY?

## Future screens
Network: logical/physical/DTC/live overlays.
Timeline: synchronized CAN/DTC/measurement/user-marker tracks.
Sherlock: evidence graph, supported/contradicted/missing evidence, next test.
Crash: impact zones + harness/connector overlay with temporal before/after evidence.
