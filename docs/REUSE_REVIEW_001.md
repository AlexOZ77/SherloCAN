# Reuse Review 001 — Don't reinvent the wheel

Date: 2026-09-22

## Team decision

SherloCAN should be an evidence-first integration and investigation layer. Mature protocol libraries and deterministic reverse-engineering workflows should be reused or adapted instead of reimplemented.

## Candidates reviewed

### Python-J2534-Interface (keenanlaws) — ADOPT/WRAP, pending bench validation
MIT, Python 3.10+, Windows/J2534 focus. It already implements registry discovery and PassThru concepts and documents 32-bit compatibility. We should evaluate it behind SherloCAN's CaptureAdapter instead of maintaining a second full J2534 ctypes stack.

Boundary: SherloCAN retains its own immutable raw capture, queue/drop accounting, event timeline, evidence provenance and UI. Vendor/library calls stay behind a provider adapter.

### python-udsoncan + python-can-isotp — ADOPT LATER
Use for active UDS/ISO-TP diagnostics when SherloCAN adds a deliberate diagnostic-session mode. Do not mix active requests with passive forensic capture without explicit session provenance.

### python-can + cantools — ADOPT
Use standard CAN abstractions/log formats and DBC parsing/decoding rather than inventing them. Decoded signals must carry DBC/source provenance.

### CSS Electronics CAN reverse-engineering skills — ADAPT WORKFLOW
MIT. Valuable deterministic workflow: survey → correlate → bit search → build DBC → verify. Hardware-specific CANsub discovery is not reused for OpenPort, but the offline analysis workflow fits SherloCAN strongly. Candidate for a future Signal Investigator module.

### automotive-claude-code-agents / Hermes automotive skills — USE AS REVIEW KNOWLEDGE, NOT RUNTIME DEPENDENCY
Broad diagnostics/network/testing knowledge and specialist roles. Useful for design reviews, checklists and test strategy. Do not copy assertions into the vehicle knowledge base without OEM/measured provenance.

### Canopy vehicle-diagnostics MCP — STUDY ARCHITECTURE
Its source-agnostic diagnostic seam, cited structured output, grounded refusal and human-in-the-loop regression approach align with SherloCAN's evidence model. Study patterns; avoid coupling core operation to an external agent framework.

### Generic vehicle-diagnostics / repair persona skills — REFERENCE ONLY
Useful generic decision trees, but too broad for CAN forensic truth. They must never override OEM data or measured evidence.

## Architecture after review

Hardware provider → CaptureAdapter → normalized CANFrame → immutable raw store → deterministic analyzers → evidence graph → UI.

Protocol packages are replaceable providers. SherloCAN's differentiated layer is provenance, temporal correlation, case history, physical topology, hypotheses, next discriminating test and WHY.

## Immediate changes

1. Stop implementing a full J2534 standard wrapper from scratch.
2. Add a provider seam and dependency probe for j2534-api.
3. Keep the existing registry discovery as a safe fallback/diagnostic probe.
4. Bench-test the external provider with OpenPort 2.0 before making it mandatory.
5. Add cantools/python-can after the capture vertical slice is green.
6. Port the CSS offline reverse-engineering method as an optional analysis module with attribution and tests.
