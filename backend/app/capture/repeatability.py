from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import median
from .divergence import first_divergence
from .markers import marker_time

def _key(e:dict)->tuple[str,str]:
    return (e["can_id"],e["kind"])

def repeatability(root:Path,sessions:list[dict],align_to:str="START",window_before:float=5.0,window_after:float=15.0)->dict:
    normals=sorted([s for s in sessions if s["role"]=="NORMAL_A" and s.get("trial")],key=lambda s:s["trial"])
    faults=sorted([s for s in sessions if s["role"]=="FAULT_B" and s.get("trial")],key=lambda s:s["trial"])
    if len(normals)<2 or len(faults)<2:
        raise ValueError("at least two numbered NORMAL_A and FAULT_B trials are required")
    trials=normals+faults
    if len({(s["role"],s["trial"]) for s in trials})!=len(trials):
        raise ValueError("duplicate trial numbers detected")
    bad=[s["session_id"] for s in trials if (s.get("evidence") or {}).get("capture_data_loss")]
    if bad:
        return {"status":"BLOCKED_DATA_LOSS","sessions":bad,"signals":[],"pairwise":[],
          "interpretation":"Repeatability is blocked because one or more selected captures report data loss."}

    anchors={}
    for s in trials:
        a=marker_time(root,s["session_id"],align_to)
        if a is None: raise ValueError(f"{align_to} marker missing in {s['session_id']}")
        anchors[s["session_id"]]=a

    # Within-role stability is measured independently. A signal is counted once per trial,
    # not once per cross-product comparison.
    normal_events=defaultdict(set)
    fault_events=defaultdict(set)
    fault_times=defaultdict(list)
    comparisons=[]
    for a in normals:
        for b in faults:
            d=first_divergence(a["evidence"]["raw_path"],b["evidence"]["raw_path"],
                a_anchor=anchors[a["session_id"]],b_anchor=anchors[b["session_id"]],
                window_before=window_before,window_after=window_after,anchor_kind=align_to)
            comparisons.append({"normal_trial":a["trial"],"fault_trial":b["trial"],
                                "first_observed_change":d["first_observed_change"]})

    # Use the first NORMAL trial as a descriptive reference for each B. This avoids
    # duplicating each B event across every A pairing.
    ref=normals[0]
    for b in faults:
        d=first_divergence(ref["evidence"]["raw_path"],b["evidence"]["raw_path"],
            a_anchor=anchors[ref["session_id"]],b_anchor=anchors[b["session_id"]],
            window_before=window_before,window_after=window_after,anchor_kind=align_to)
        for e in d["events"]:
            k=_key(e); fault_events[k].add(b["trial"]); fault_times[k].append(e["at"])

    # A-within-A instability: observations appearing when each later A is compared
    # with the first A are tracked separately and never mislabeled as FAULT evidence.
    for a in normals[1:]:
        d=first_divergence(ref["evidence"]["raw_path"],a["evidence"]["raw_path"],
            a_anchor=anchors[ref["session_id"]],b_anchor=anchors[a["session_id"]],
            window_before=window_before,window_after=window_after,anchor_kind=align_to)
        for e in d["events"]: normal_events[_key(e)].add(a["trial"])

    rows=[]
    for k in sorted(set(fault_events)|set(normal_events)):
        cid,kind=k; fset=fault_events[k]; nset=normal_events[k]
        rows.append({"can_id":cid,"kind":kind,
          "normal_trials_observed":len(nset),"normal_trials_total":len(normals),
          "fault_trials_observed":len(fset),"fault_trials_total":len(faults),
          "reproduced_in_all_fault_trials":len(fset)==len(faults),
          "normal_instability_observed":bool(nset),
          "median_fault_time":median(fault_times[k]) if fault_times[k] else None})
    rows.sort(key=lambda x:(not x["reproduced_in_all_fault_trials"],x["normal_instability_observed"],-x["fault_trials_observed"],x["can_id"],x["kind"]))
    return {"status":"OK","normal_trials":len(normals),"fault_trials":len(faults),"alignment":align_to,
      "window_before":window_before,"window_after":window_after,"signals":rows,"pairwise":comparisons,
      "interpretation":"Repeatability is descriptive. Fault occurrence is counted once per B trial; A-within-A instability is reported separately. It does not establish ECU ownership or causality."}
