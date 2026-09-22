# SherloCAN v0.2 architecture

The capture core is adapter-independent:

CaptureAdapter → Frame Normalizer → bounded queue → Raw Writer / Live Analyzer / UI stream.

## Evidence rule

Raw capture, user observations, OEM documentation, measurements and inference remain separate provenance classes.

## Safety

v0.2 begins with application-level read-only capture. It does not provide arbitrary CAN transmit, injection, fuzzing, coding or programming.

## Development gate

FileReplayAdapter and synthetic tests must work before a real J2534/OpenPort implementation is enabled.
