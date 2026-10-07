# SherloCAN feature gate: Grill before build

For a major feature, hardware integration, architecture change, or supported-platform change:

1. Run `grill-me` / `grilling`.
2. Research facts from code/docs/hardware; user decides tradeoffs.
3. Record settled decisions in `docs/decisions/`.
4. Implement on a branch.
5. Run backend, frontend and quality gates.
6. For hardware/legacy OS claims, require target-machine acceptance before marking VERIFIED.

Small bug fixes, copy changes, and tests that do not alter architecture are exempt.
