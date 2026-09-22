# Team Review 004 — Explicit CAN Channel Gate

Date: 2026-09-22

## Implemented
- Added a separate raw-CAN channel verification operation.
- API requires an explicit positive bitrate; omission returns HTTP 400.
- v0.2 channel gate accepts only protocol CAN. ISO15765/UDS active diagnostic mode is rejected.
- Sequence is bounded: PassThruOpen → PassThruConnect → PassThruDisconnect → PassThruClose.
- No PassThruWriteMsgs call exists in this gate.
- Added tests proving zero bitrate and ISO15765 are rejected.

## Evidence discipline
SherloCAN does not infer a Nissan J11 bitrate in this implementation. A successful channel test only proves that the configured raw CAN channel could be opened and closed; it does not prove traffic was received, ECU ownership, bus health, or vehicle correctness.

## Next cycle
Implement bounded PassThruReadMsgs capture, normalize frames, feed FrameQueue/FlightRecorder, surface dropped-frame evidence, and show only measured traffic metrics.

## Physical validation
Not run on the user's OpenPort 2.0 yet.
