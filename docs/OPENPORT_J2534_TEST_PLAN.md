# OpenPort 2.0 / J2534 hardware test plan

## Review decision
Hardware support is developed behind CaptureAdapter. No guessed Nissan bitrate, pins, CAN IDs or ECU ownership enter the implementation.

## Phase A — driver discovery
Install the official Tactrix OpenPort driver/J2534 DLL. SherloCAN enumerates registered PassThru providers and reports DLL path, registry view, process bitness and file availability.

## Phase B — architecture gate
Determine DLL architecture before loading it. A 32-bit DLL must not be loaded into a 64-bit Python process. If required, run a dedicated x86 SherloCAN J2534 Bridge and communicate locally with the main application.

## Phase C — device test
Load only the selected registered DLL. Resolve required PassThru entry points. Test device availability without starting a vehicle session. Tactrix documents a vendor-specific device-instance IOCTL; use it only for Tactrix devices and keep generic J2534 discovery separate.

## Phase D — read-only CAN capture
Only after API validation: PassThruOpen → PassThruConnect using a user/profile-selected documented bitrate → PassThruReadMsgs in a worker → normalized CANFrame queue. No arbitrary PassThruWriteMsgs feature is exposed.

## Phase E — vehicle test
1. Ignition OFF, connect OpenPort USB and OBD.
2. SherloCAN Device Test.
3. Select documented/measured bus configuration.
4. Start capture.
5. Normal session.
6. Fault session: OFF → ON → START.
7. Mark FAULT when P0603/chassis warning appears.
8. Compare windows and preserve raw SHA-256 capture.

## Acceptance
- Disconnect is distinct from no CAN activity.
- Dropped/overflow counts are visible.
- Raw data remains immutable.
- No CAN-ID→ECU attribution without evidence.
- Application exposes no transmit/injection/fuzzing controls.
