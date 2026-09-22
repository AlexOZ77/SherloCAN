# Dependency policy

## Core
FastAPI and SherloCAN deterministic capture/analysis code must run without vehicle hardware.

## Hardware profile
`requirements-hardware.txt` adds reusable automotive packages.

- j2534-api 2.0.0: J2534-1 v04.04 provider. Verified package imports are `J2534` and `J2534_REGISTRY`; do not probe a guessed module named `j2534-api`.
- python-can: standard CAN abstraction/log interoperability.
- cantools: DBC parsing/decoding.

## Active diagnostics
udsoncan/python-can-isotp remain future optional dependencies. They are intentionally excluded from the passive capture milestone.

## Validation states
INSTALLED != DRIVER_FOUND != DEVICE_OPENED != CHANNEL_CONNECTED != CAPTURE_VALIDATED.
OpenPort support may only be labelled CAPTURE_VALIDATED after a physical bench/vehicle test.
