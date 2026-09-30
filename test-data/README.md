# Regression test data

Store only sanitized, non-sensitive fixtures suitable for repository use.

Suggested layout:
- qashqai-j11/normal/
- qashqai-j11/restart/
- qashqai-j11/p0603/
- qashqai-j11/data-loss/

Each fixture should have a manifest recording capture source type, timestamp policy, software version, acceptance result, expected observations, and SHA-256 of the immutable raw file.

Do not commit VINs, registration details, owner information, credentials, proprietary binaries or captures without permission.
