# Team Review 002 — Device Open UI Gate

Date: 2026-09-22
Scope: SherloCAN v0.2 / OpenPort J2534 branch

## Result
The frontend production CI was green before this increment. The UI now exposes an explicit **VERIFY DEVICE OPEN** action wired to the backend `POST /api/capture/j2534/open-test` endpoint.

The operation is intentionally narrow: **PassThruOpen → PassThruClose**. It does not create a CAN channel, select a bitrate, read traffic, or transmit diagnostic requests.

## Review perspectives
- **Architecture:** hardware state is no longer implied by preflight discovery; Device Open is a separate gate.
- **Diagnostics:** CAN protocol/bitrate and ECU ownership remain UNKNOWN until measured or explicitly configured.
- **Safety:** opening the J2534 device is user-triggered; no automatic vehicle-bus connection was added.
- **UX:** the OpenPort card distinguishes PREFLIGHT from DEVICE OPEN VERIFIED and explains that CAN is still unopened.
- **QA:** new UI code requires CI confirmation after this commit; physical OpenPort validation is still outstanding.

## Remaining blockers
1. Verify the new frontend commit in GitHub Actions.
2. Validate PassThruOpen/Close on the user's actual OpenPort 2.0 Windows machine.
3. Inspect the verified j2534-api PassThruConnect API/constants before implementing CAN Channel.
4. Do not hardcode a J11 CAN bitrate.
5. Fix the CaptureSession queue/FlightRecorder integrity issue before live capture.

## Status
Implemented in code: **YES**
CI for this exact increment: **PENDING**
Physical OpenPort test: **NOT YET RUN**
CAN channel: **NOT IMPLEMENTED**
Live CAN capture: **NOT IMPLEMENTED**
