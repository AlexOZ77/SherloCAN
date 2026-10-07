# ADR-0002: REA-assisted capability acquisition

Status: PROPOSED / GRILL ROUND 1
Date: 2026-10-07

## Context
SherloCAN needs selected useful behaviors from third-party diagnostic applications without coupling the vehicle-test runtime to those applications.

REA (morluto/rea, MIT) can inspect native, managed, Electron/JavaScript and runtime behavior with Evidence. Upstream REA currently requires Node.js 22+ and its documented Windows native Ghidra boundary is Windows 10+ x64. SherloCAN target hardware is Windows 8.1 x64 build 9600.

## Recommended boundary
REA is a DEVELOPMENT/INVESTIGATION dependency only. It MUST NOT be installed or executed on the Windows 8.1 vehicle laptop and MUST NOT become a SherloCAN runtime dependency.

Pipeline:
target app -> REA investigation on supported analysis workstation -> Evidence bundle / feature contract -> Grill -> approved ADR -> clean SherloCAN implementation -> CI -> Windows 8.1 packaging -> hardware acceptance.

## Candidate capability families
P0:
1. Oscilloscope + CAN time correlation: import/export traces from MT Pro / FNIRSI / other tools where lawful and technically documented; align waveform timestamps with CAN events.
2. Diagnostic-app log adapters: parse exported logs/reports into SherloCAN canonical Evidence without controlling the source app.
3. Feature reconstruction ledger: store observed behavior, unknowns, fixtures and verification status for a capability learned from another app.

P1:
4. Managed/.NET diagnostic-app static inspection to document file formats and observable workflows when source is unavailable.
5. Native binary inspection for device/protocol boundaries where permitted, with static findings explicitly separated from runtime facts.

Excluded by default:
- copying proprietary code/assets/keys;
- bypassing licensing, authentication or access controls;
- patching third-party applications;
- executing untrusted targets on the vehicle laptop;
- claiming protocol semantics from strings/static names alone.

## Evidence contract
Every acquired capability records:
- source application + exact version/artifact SHA-256 when available;
- observation type: static/runtime/documented;
- Evidence IDs or equivalent retained records;
- known/unknown boundary;
- clean-room SherloCAN owner module;
- positive/negative/malformed fixtures;
- verifier and CI result;
- hardware acceptance status when hardware is involved.

## Gate
No P0/P1 capability enters main until Grill is settled and this or a child ADR is ACCEPTED.
