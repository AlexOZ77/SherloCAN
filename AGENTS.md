# SherloCAN Agent Development Contract

This file defines the operating contract for autonomous or semi-autonomous coding agents working in SherloCAN.

## Mission
Improve SherloCAN as a reproducible, evidence-driven CAN diagnostic tool without turning hypotheses into facts.

## Allowed without human approval
- Inspect code, tests, documentation and non-sensitive test fixtures.
- Create a feature branch and commits.
- Add or improve unit, integration and regression tests.
- Refactor when observable behavior is preserved by tests.
- Prepare Windows build changes and documentation.
- Open a pull request and report failed checks.

## Human approval required
- Merge to main or create a production/stable release.
- Change a verified vehicle signal definition or diagnostic conclusion.
- Change acceptance thresholds solely to make a failing capture/test pass.
- Introduce CAN transmission, ECU coding, flashing, actuator control or other write operations.
- Delete/replace raw diagnostic evidence.
- Mark a hypothesis VERIFIED without the evidence requirements below.

## Non-negotiable safety rules
1. SherloCAN is read-only by default. No CAN transmit path may be introduced implicitly.
2. Raw captures are evidence. Never rewrite them in place.
3. Capture Acceptance Gate runs before diagnostic interpretation. DATA_LOSS/REJECTED data must not support a verified conclusion.
4. Unknown CAN fields remain UNKNOWN until supported by repeatable evidence.
5. A correlation is not a causal diagnosis.
6. Tests and quality gates must never be bypassed, muted or weakened merely to obtain a green build.
7. Generated artifacts must identify source commit/version.

## Evidence states
Use: UNKNOWN -> HYPOTHESIS -> SUPPORTED -> VERIFIED or REJECTED.
VERIFIED requires: accepted capture(s), reproducible observation, documented experiment/procedure, evidence manifest, and human review when the conclusion affects a vehicle profile or diagnostic recommendation.

## Required workflow
1. Read AGENTS.md, ARCHITECTURE.md and relevant docs/code.
2. State the intended change and risk class in the PR.
3. Work only on a non-main branch.
4. Add/update tests before claiming completion.
5. Run backend tests and applicable frontend/build checks.
6. For CAN-analysis behavior, run regression fixtures and preserve raw evidence.
7. Open a PR. Never self-merge.
8. Record limitations and unresolved hypotheses.

## Risk classes
- R0 docs/tests only.
- R1 internal refactor, no diagnostic semantics change.
- R2 analysis/vehicle-profile/acceptance behavior change: evidence required.
- R3 hardware write/control/ECU coding/flashing: prohibited for autonomous implementation without explicit human design approval.

When instructions conflict, choose the safer, more evidence-preserving action and request human review.
