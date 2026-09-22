# Team Review 006 — Bounded J2534 Reader

Date: 2026-09-22

## Implemented
- Added a bounded raw-CAN receive component for the J2534 boundary.
- The reader has explicit timeout and maximum-frame limits.
- The module does not import or call a J2534 write-message API.
- Raw messages are normalized into SherloCAN CANFrame objects.
- Normalization rejects messages shorter than the four-byte raw CAN identifier field.
- Unit tests cover 11-bit-range ID, 29-bit-range ID and malformed input.

## Important validation boundary
This commit establishes the SherloCAN reader seam and normalization tests. It is not evidence that a physical OpenPort 2.0 has returned frames. The exact runtime behavior of the installed vendor/library combination still has to be validated on the Windows/OpenPort machine before declaring live capture operational.

## Next integration
Connect the bounded reader to the existing evidence-aware capture sink and expose measured-only capture statistics. Any queue overflow must surface as CAPTURE DATA LOSS.
