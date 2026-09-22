from __future__ import annotations
from dataclasses import dataclass,asdict

@dataclass(frozen=True,slots=True)
class Hypothesis:
    id:str;title:str;test:str

HYPOTHESES=[
 Hypothesis("H1","ECM power / shutdown sequence","Measure ECM power during ON→OFF and verify delayed shutdown."),
 Hypothesis("H2","CAN joint / network intermittent","Repeat capture with controlled connector/wiggle marker and look for reproducible multi-ID disruption."),
 Hypothesis("H3","ECM KAM / internal retention","If network timing remains stable, test backup/keep-alive supply and ECM retention path."),
 Hypothesis("H4","Common power / ground event","Correlate simultaneous multi-ID changes with power/ground measurements."),
]

def evaluate_hypotheses(repeat:dict)->dict:
    signals=repeat.get("signals",[])
    repeated=[s for s in signals if s.get("reproduced_in_all_fault_trials")]
    multi_network=[s for s in repeated if s.get("kind") in {"NEW_ID","LOST_ID","PERIOD_SHIFT","FREQUENCY_SHIFT","DLC_CHANGE"}]
    rows=[]
    for h in HYPOTHESES:
        status="NOT_TESTED";evidence=[];next_test=h.test
        if repeated:
            if h.id=="H2":
                status="SUPPORTED";evidence=[f"{s['can_id']} {s['kind']} repeated {s['fault_trials_observed']}/{s['fault_trials_total']} FAULT trials" for s in multi_network[:3]]
            elif h.id in {"H1","H3","H4"}:
                status="INCONCLUSIVE";evidence=["Repeatable CAN observations exist, but no direct power/KAM/ground measurement is attached."]
        rows.append({**asdict(h),"status":status,"evidence":evidence,"next_test":next_test})
    return {"hypotheses":rows,"rules":"Statuses summarize available evidence only. SUPPORTED is not CONFIRMED and does not establish root cause."}
