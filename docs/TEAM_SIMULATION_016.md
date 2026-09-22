# Team simulation 016 — START-aligned P0603 A/B

Status: design/test simulation only. No physical OpenPort/J11 measurements are represented here.

## Roles
- Diagnostic reviewer: verifies experiment semantics.
- CAN/data reviewer: verifies alignment and deterministic outputs.
- Evidence reviewer: blocks causal overclaim.
- Operator/UX reviewer: verifies field workflow.
- Reliability reviewer: checks loss/marker failure paths.

## Modelled happy path
1. NORMAL A RAW contains START at t=10.000 s.
2. Operator registers START marker for A.
3. FAULT B RAW contains START at t=20.000 s.
4. Operator registers START marker for B.
5. Analyzer shifts both timelines so START=0 and limits analysis to -5…+15 s.
6. Synthetic B introduces unknown CAN ID 0x200 at +420 ms and 0x300 at +440 ms.
7. Expected result: FIRST OBSERVED CHANGE = NEW_ID 0x200 at +420 ms; MULTI_ID_EVENT groups two changes within 50 ms.
8. Expected evidence labels remain ECU UNKNOWN and CAUSALITY NOT_ESTABLISHED.

Automated test: backend/tests/test_markers_alignment.py.

## Failure-path walkthrough
- Missing START in either A or B: API returns conflict; no unaligned result is silently presented as START-aligned.
- Negative marker timestamp: rejected.
- Unsupported marker kind: rejected.
- DATA LOSS in either session: existing A/B evidence warning remains relevant; analyst must not treat comparison as complete.
- Connect without frames: not accepted as CAN traffic evidence.
- Different absolute RAW timestamps: alignment removes the absolute offset by subtracting each session's own START marker.
- Events outside -5…+15 s: excluded from the aligned analysis window.
- Several changes within 50 ms: represented as MULTI_ID_EVENT, not multiple independent root causes.

## Team decisions
1. START is operator evidence in v1, not inferred from unknown CAN traffic.
2. IGN_ON/FAULT/DTC/WIGGLE marker types are supported by storage but START is the first alignment anchor exposed in UI.
3. Do not implement automatic ECU ownership until backed by verified mapping.
4. Do not call FIRST OBSERVED CHANGE the root cause.
5. Next test cycle should model repeatability A1/A2/A3 vs B1/B2/B3 and marker-entry ergonomics.
