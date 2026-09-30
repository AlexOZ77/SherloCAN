# Security and Vehicle Safety

SherloCAN interacts with vehicle networks. Treat changes affecting hardware communication as safety-sensitive.

## Supported security reports
Open a private security report through GitHub when available. Do not publish secrets, credentials, private captures, VINs or personally identifying vehicle data in issues.

## Safety baseline
- Read-only capture is the default.
- Autonomous agents must not add CAN transmission, ECU flashing/coding, actuator control, immobilizer/security access or bypasses.
- Hardware-facing changes require explicit review and bench/vehicle validation as appropriate.
- Do not commit proprietary driver binaries, credentials or private vehicle data.

## Evidence integrity
Raw logs are immutable evidence. Derived files must be reproducible and traceable to their source capture and software version.
