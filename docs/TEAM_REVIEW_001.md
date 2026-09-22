# SherloCAN Team Review 001

Date: 2026-09-22
Milestone: first runnable vertical slice

## Review board

Product/diagnostics lead — protects the real workshop workflow and asks whether each feature helps isolate a fault.
CAN/J2534 engineer — owns capture integrity, adapter boundaries, timing and loss accounting.
Backend/data engineer — owns sessions, immutable raw data, provenance and analysis APIs.
Frontend/UX engineer — owns investigator workbench, timeline and evidence semantics.
QA/reliability engineer — owns deterministic fixtures, regression tests, Windows compatibility and failure states.
Automotive evidence reviewer — blocks invented ECU mappings, CAN IDs, pins, TSB applicability and causal claims.

These are engineering roles used as review perspectives; they are not claims that external people participated.

## What the review accepts

The current foundation is directionally correct: read-only capture abstraction, bounded queue with explicit drops, immutable-oriented raw writer, Flight Recorder, event markers, baseline/gap detection, synthetic fixtures and an evidence-aware UI concept.

## What the review rejects

The UI currently contains hard-coded live values and therefore must not be presented as a working capture screen.
The synthetic IDs must never be interpreted as Nissan mappings.
J2534 must not be added before the end-to-end replay path proves capture → event → analysis → UI.
A long gap is an observation, not a root cause.

## First working version: definition

The first runnable version is a vertical slice, not a feature-complete diagnostic suite:

1. Start backend and frontend locally.
2. UI verifies backend health.
3. User loads the bundled synthetic NORMAL and FAULT fixtures through the backend demo endpoint.
4. Backend builds a baseline and detects the intentionally inserted long gap.
5. UI renders actual API results and labels all synthetic/unknown data honestly.
6. No CAN transmission and no invented ECU ownership.

## Gate to OpenPort

OpenPort/J2534 work starts after this vertical slice builds and its backend tests pass in CI. Then hardware discovery and capture are introduced behind CaptureAdapter without changing investigation semantics.
