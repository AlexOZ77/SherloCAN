# Team Review 005 — Read-only Capture Sink

Date: 2026-09-22

## Implemented
A deterministic capture sink now joins CaptureSession, bounded FrameQueue and RawCaptureWriter. Accepted frames are persisted to append-only CSV and receive a final SHA-256 digest. Queue overflow is surfaced as capture_data_loss=true and dropped frames are not written into the evidence file.

## Deliberate boundary
This cycle does NOT claim that PassThruReadMsgs is wired to OpenPort yet. The sink is hardware-independent so it can be tested before vendor-DLL interaction. No CAN IDs, ECU ownership, bitrate, voltage, latency or frame rate are invented.

## Team assessment
- Architecture: reusable sink is ready for FileReplay and J2534 Reader.
- Evidence: RAW file and digest establish an integrity primitive.
- Reliability: queue loss is explicit and testable.
- Safety: no transmit path added.
- QA: regression test forces a one-frame queue and verifies CAPTURE DATA LOSS.

## Next hardware gate
Verify the exact j2534-api read-message object/signature from upstream source, implement a bounded reader worker, normalize only fields proven by the library, and then connect it to this sink.
