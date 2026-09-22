# Team Review 008 — Operator Guide + Capture UI Contract

Date: 2026-09-22

## Delivered
- Started a living Russian operator/functionality guide: USER_GUIDE_RU.md.
- Documented current features, safety boundary, OpenPort gates, evidence pipeline, first-run procedure and J11 P0603 A/B experiment.
- Explicitly separated implemented functions from future functionality.
- Repaired the capture API import-line regression again on the current branch.

## UI contract for next implementation
The live capture screen must bind only to backend measurements:
- Frames observed / accepted / dropped
- Unique CAN IDs
- CAPTURE DATA LOSS
- RAW evidence path
- SHA-256
No voltage, fps, latency, ECU ownership or bitrate may appear as measured unless the backend provides the measurement or the operator explicitly configured the value.

## Documentation rule
USER_GUIDE_RU.md is now a release artifact. Every functional cycle must update it with usage, measurement provenance, limitations and tests.
