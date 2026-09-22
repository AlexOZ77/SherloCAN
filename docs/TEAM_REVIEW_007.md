# Team Review 007 — Integrated Read-only Capture Pipeline

Date: 2026-09-22

## Implemented
The bounded J2534 reader is now connected to the evidence-aware capture sink.

Pipeline:
Open J2534 CAN channel → bounded reader → CANFrame normalizer → CaptureSession → bounded FrameQueue → append-only RAW CSV → SHA-256.

Measured summary fields are returned from the pipeline: frames_observed, frames_accepted, frames_dropped, unique_ids, capture_data_loss, raw_path and sha256.

## QA
Tests use a mocked reader so CI does not require OpenPort hardware. One test validates a loss-free capture. A second forces queue overflow and requires CAPTURE DATA LOSS to become true.

## Safety / evidence
No transmit operation was added. Bitrate remains an explicit input. No ECU ownership is inferred. This integration is hardware-ready but not yet physically validated on the user's OpenPort 2.0.

## Next
Expose this pipeline through a bounded capture API/session controller, then bind UI counters and DATA LOSS state exclusively to returned measurements.
