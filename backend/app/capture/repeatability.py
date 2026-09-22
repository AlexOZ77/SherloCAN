from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from .divergence import first_divergence
from .markers import marker_time

def repeatability(root:Path,sessions:list[dict],align_to:str="START",window_before:float=5.0,window_after:float=15.0)->dict:
    normals=sorted([s for s in sessions if s["role"]=="NORMAL_A" and s.get("trial")],key=lambda s:s["trial"])
    faults=sorted([s for s in sessions if s["role"]=="FAULT_B" and s.get("trial")],key=lambda s:s["trial"])
    if len(normals)<2 or len(faults)<2: raise ValueError("at least two numbered NORMAL_A and FAULT_B trials are required")
    occurrence=defaultdict(lambda:{"normal_trials":set(),"fault_trials":set(),"fault_times":[]})
    comparisons=[]
    for a in normals:
        aa=marker_time(root,a["session_id"],align_to)
        if aa is None: raise ValueError(f"{align_to} marker missing in {a['session_id']}")
        for b in faults:
            ba=marker_time(root,b["session_id"],align_to)
            if ba is None: raise ValueError(f"{align_to} marker missing in {b['session_id']}")
            d=first_divergence(a["evidence"]["raw_path"],b["evidence"]["raw_path"],a_anchor=aa,b_anchor=ba,window_before=window_before,window_after=window_after,anchor_kind=align_to)
            comparisons.append({"normal_trial":a["trial"],"fault_trial":b["trial"],"first_observed_change":d["first_observed_change"]})
            for e in d["events"]:
                key=(e["can_id"],e["kind"])
                occurrence[key]["normal_trials"].add(a["trial"])
                occurrence[key]["fault_trials"].add(b["trial"])
                occurrence[key]["fault_times"].append(e["at"])
    rows=[]
    nN,nF=len(normals),len(faults)
    for (cid,kind),x in occurrence.items():
        nf=len(x["fault_trials"]); nn=len(x["normal_trials"])
        rows.append({"can_id":cid,"kind":kind,"normal_trials_observed":nn,"normal_trials_total":nN,
          "fault_trials_observed":nf,"fault_trials_total":nF,"reproduced_in_all_fault_trials":nf==nF,
          "median_fault_time":sorted(x["fault_times"])[len(x["fault_times"])//2] if x["fault_times"] else None})
    rows.sort(key=lambda x:(not x["reproduced_in_all_fault_trials"],-x["fault_trials_observed"],x["can_id"],x["kind"]))
    return {"normal_trials":nN,"fault_trials":nF,"alignment":align_to,"window_before":window_before,"window_after":window_after,
      "signals":rows,"pairwise":comparisons,"interpretation":"Repeatability ranks observations only; it does not establish ECU ownership or causality."}
