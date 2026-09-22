# Team Review 009 — Measured-only Capture Evidence UI

Date: 2026-09-22

## Implemented
A Capture Evidence card is now part of the main dashboard. Its empty state explicitly says that live capture has not run. It does not use synthetic replay metrics as hardware measurements.

The component contract accepts only capture-pipeline evidence: observed, accepted, dropped, unique IDs, data-loss flag, RAW path and SHA-256.

## Review
- UX: absence of measurement is visible rather than represented by plausible placeholder numbers.
- Evidence: queue loss has a dedicated warning state.
- Architecture: UI component is ready for a session API without coupling to demo replay.
- Documentation: USER_GUIDE_RU.md updated in the same cycle.

## Next
Implement a bounded capture session API/controller and bind its completed result to CaptureEvidenceCard. Hardware start must remain explicit and require a validated provider/channel configuration.
