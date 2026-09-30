# Agent-ready development workflow

SherloCAN uses agents as contributors, not final authorities.

## Development loop
Issue/goal -> branch -> tests -> implementation -> replay/regression -> CI -> PR -> human review -> merge.

For diagnostic work:
raw capture -> acceptance gate -> observation -> hypothesis -> controlled experiment -> repeatability -> evidence manifest -> review -> verified knowledge.

## Definition of done
A change is done only when its tests pass, relevant regressions pass, documentation reflects behavior, evidence is traceable, and limitations are recorded.

## Diagnostic language
Prefer factual states:
- UNKNOWN: not established.
- HYPOTHESIS: plausible explanation to test.
- SUPPORTED: repeated evidence is consistent but not sufficient for final verification.
- VERIFIED: evidence requirements and review completed.
- REJECTED: experiment contradicts the hypothesis.

Agents must not silently promote states.
