# SherloCAN Architecture Map

SherloCAN is a Python/FastAPI CAN capture and investigation project with a web frontend and Windows packaging.

## Current high-level flow
Hardware or replay source -> capture/J2534 layer -> raw capture/session -> acceptance gate -> analysis/experiments -> API -> frontend.

## Important boundaries
- `backend/app/capture/j2534/`: OpenPort/J2534 hardware integration.
- `backend/app/capture/raw_writer.py`: raw evidence persistence.
- `backend/app/capture/acceptance.py`: capture-quality gate.
- `backend/app/capture/replay.py`: deterministic replay path.
- `backend/app/capture/hypotheses.py`, `experiments.py`, `experiment_protocol.py`: diagnostic investigation.
- `backend/app/capture/evidence_manifest.py`: evidence provenance.
- `backend/tests/`: automated backend verification.
- `.github/workflows/`: CI and Windows release automation.

## Architectural invariants
1. Capture is separated from interpretation.
2. Raw data is preserved before derived analysis.
3. Acceptance precedes diagnostic conclusions.
4. Replay is the preferred deterministic regression mechanism.
5. Vehicle knowledge must distinguish known, inferred and unknown fields.
6. Hardware write/control is outside the autonomous-agent boundary.

Agents must update this map when introducing a new major subsystem or moving these boundaries.
