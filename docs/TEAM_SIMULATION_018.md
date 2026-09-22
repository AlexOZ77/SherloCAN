# Team simulation 018 — Hypothesis Manager

Software simulation only; no vehicle result.

## Initial state
With no repeated A/B evidence, H1 ECM power/shutdown, H2 CAN joint/network intermittent, H3 ECM KAM/internal retention and H4 common power/ground are all NOT_TESTED.

## Injected synthetic observation
Repeatability result contains synthetic NEW_ID 0x200 in 3/3 FAULT trials.

Expected:
- H2 -> SUPPORTED because repeatable CAN behavior supports performing a network/joint test.
- H1/H3/H4 -> INCONCLUSIVE because CAN repeatability alone neither proves nor rejects power, KAM, or common ground hypotheses.
- Nothing -> CONFIRMED.
- Root cause remains unassigned.

## Team review
Diagnostic: next-test text must be actionable.
Evidence: SUPPORTED must never mean confirmed.
CAN: unknown ID ownership remains unknown.
Reliability: future version must include DATA LOSS and direct measurement evidence before status transitions.
UX: each card shows status, evidence, next test; no probability percentages.
