# Team Design Review 011 — Atomic Hardware Capture

Date: 2026-09-22

## Decision before implementation
The team reviewed the proposed Open → Connect → Capture → Disconnect → Close flow.

### Architecture
Do not expose channel_id to the operator. Device and channel handles belong to one bounded operation and must never survive the request.

### Reliability
Cleanup belongs in finally. Disconnect and Close must be attempted independently so a disconnect failure cannot prevent device close. Cleanup outcomes must be evidence fields, not hidden log-only details.

### Diagnostics
Bitrate remains explicit. Protocol remains raw CAN only. A successful connect is not a successful capture; traffic is confirmed only when frames are actually observed.

### Safety
No PassThruWriteMsgs path. Capture remains bounded by max_frames and read timeout.

### UX
START CAPTURE should require an explicit bitrate and show RUNNING. Completed evidence must show frame counts, DATA LOSS, RAW digest, and cleanup state. Hardware errors must not leave a green status.

## Approved implementation
Create one atomic controller that owns provider selection, PassThruOpen, PassThruConnect, bounded read/evidence persistence, PassThruDisconnect and PassThruClose.
