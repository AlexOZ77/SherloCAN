## Purpose

## Risk class
- [ ] R0 docs/tests
- [ ] R1 refactor/no diagnostic semantics change
- [ ] R2 analysis/vehicle-profile/acceptance behavior
- [ ] R3 hardware write/control (requires explicit human design approval)

## Verification
- [ ] Backend tests pass
- [ ] Relevant frontend/build checks pass
- [ ] Regression/replay checked when CAN-analysis behavior changes
- [ ] Capture Acceptance Gate was not bypassed or weakened to pass
- [ ] Raw evidence was not modified
- [ ] Unknown fields remain UNKNOWN unless evidence is attached

## Evidence / reproduction
Describe fixtures, captures, experiment protocol and evidence manifest. For R2 changes this section is required.

## Safety
- [ ] No new CAN transmit/write/control behavior
- [ ] No secrets/private vehicle data included

## Limitations / unresolved hypotheses

## Human gate
This PR must not be self-merged by an autonomous agent.
