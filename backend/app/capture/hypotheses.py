from __future__ import annotations
from dataclasses import dataclass,asdict

@dataclass(frozen=True,slots=True)
class Hypothesis:
    id:str
    title:str
    test:str

HYPOTHESES=[
 Hypothesis("H1","ECM power / shutdown sequence","Measure ECM power during ON→OFF and verify delayed shutdown."),
 Hypothesis("H2","CAN joint / network intermittent","Use a controlled WIGGLE/CONNECTOR marker and look for time-local multi-ID disruption; repeated A/B divergence alone is insufficient."),
 Hypothesis("H3","ECM KAM / internal retention","If network timing remains stable, test backup/keep-alive supply and ECM retention path."),
 Hypothesis("H4","Common power / ground event","Correlate simultaneous multi-ID changes with direct power/ground measurements."),
]

def evaluate_hypotheses(repeat:dict,direct_evidence:list[dict]|None=None)->dict:
    signals=repeat.get("signals",[])
    repeated=[s for s in signals if s.get("reproduced_in_all_fault_trials")]
    direct_evidence=direct_evidence or []
    rows=[]
    for h in HYPOTHESES:
        evidence_for=[];evidence_against=[];unknown=[];status="NOT_TESTED"
        if repeated:
            status="INCONCLUSIVE"
            unknown.append("Repeatable CAN divergence is observational and may be secondary to another state change.")
        for e in direct_evidence:
            if e.get("hypothesis_id")!=h.id: continue
            verdict=e.get("verdict")
            line=e.get("description","Direct test evidence")
            if verdict=="SUPPORTS": evidence_for.append(line)
            elif verdict=="CONTRADICTS": evidence_against.append(line)
        if evidence_for and not evidence_against: status="SUPPORTED"
        elif evidence_against and not evidence_for: status="CONTRADICTED"
        elif evidence_for and evidence_against: status="INCONCLUSIVE"
        rows.append({**asdict(h),"status":status,"evidence_for":evidence_for,
          "evidence_against":evidence_against,"unknown":unknown,"next_test":h.test})
    return {"hypotheses":rows,
      "rules":"A hypothesis changes to SUPPORTED or CONTRADICTED only from explicit direct test evidence. Repeated CAN divergence alone remains INCONCLUSIVE. No automatic CONFIRMED state exists."}
