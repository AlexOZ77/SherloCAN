# Team Review 003 — Capture Integrity Gate

Date: 2026-09-22

## Verified
- Frontend CI for the Device Open UI increment: PASS.
- TypeScript typecheck: PASS.
- Production frontend build: PASS.

## Implemented this cycle
CaptureSession no longer feeds a frame into FlightRecorder when FrameQueue rejects it because of backpressure. The session still counts the observed frame and the queue records the drop. A regression test proves the dropped frame is absent from the recorder event window.

## Why this matters
Before this fix, SherloCAN could report a frame as dropped by the bounded processing queue while still retaining it in the Flight Recorder. That creates contradictory evidence during forensic comparison. The evidence path is now consistent with the accepted processing stream.

## Team assessment
- Architecture: capture boundary is clearer and deterministic.
- Diagnostics: event windows can no longer silently contain downstream-dropped frames.
- Safety: no vehicle transmit capability was added.
- UX: next UI state should surface CAPTURE DATA LOSS when dropped > 0.
- QA: backend CI must validate the new regression test.

## Next gate
1. Add CAPTURE DATA LOSS evidence/event and UI indicator.
2. Validate the exact j2534-api PassThruConnect API from source before implementation.
3. Require explicit protocol/bitrate configuration; do not infer Nissan values.
4. Then implement channel open/close without diagnostic transmit.

Status: Capture integrity fix IMPLEMENTED; hardware CAN channel NOT IMPLEMENTED.
