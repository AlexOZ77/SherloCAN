from __future__ import annotations
import csv
from collections import defaultdict
from dataclasses import asdict,dataclass
from pathlib import Path
from statistics import median

@dataclass(frozen=True,slots=True)
class IDTiming:
    can_id:str;count:int;first:float;last:float;median_period:float|None;frequency_hz:float|None;typical_dlc:int

def load_timing(path:str|Path)->dict[str,IDTiming]:
    groups=defaultdict(list)
    with Path(path).open(encoding="utf-8",newline="") as h:
        for row in csv.DictReader(h):
            groups[row["can_id"]].append((float(row["timestamp"]),int(row["dlc"])))
    out={}
    for cid,items in groups.items():
        items.sort(); ts=[x[0] for x in items]; periods=[b-a for a,b in zip(ts,ts[1:]) if b>=a]
        span=ts[-1]-ts[0]; freq=(len(ts)-1)/span if len(ts)>1 and span>0 else None
        out[cid]=IDTiming(cid,len(ts),ts[0],ts[-1],median(periods) if periods else None,freq,int(median([x[1] for x in items])))
    return out

def first_divergence(a_path:str|Path,b_path:str|Path,period_ratio:float=1.5,frequency_ratio:float=1.5)->dict:
    a,b=load_timing(a_path),load_timing(b_path); events=[]
    for cid in sorted(set(a)|set(b)):
        x,y=a.get(cid),b.get(cid)
        if x is None: events.append({"kind":"NEW_ID","can_id":cid,"at":y.first,"detail":"observed only in FAULT B"});continue
        if y is None: events.append({"kind":"LOST_ID","can_id":cid,"at":x.last,"detail":"not observed in FAULT B"});continue
        if x.typical_dlc!=y.typical_dlc: events.append({"kind":"DLC_CHANGE","can_id":cid,"at":y.first,"detail":f"{x.typical_dlc} → {y.typical_dlc}"})
        if x.median_period and y.median_period:
            ratio=max(x.median_period,y.median_period)/min(x.median_period,y.median_period)
            if ratio>=period_ratio: events.append({"kind":"PERIOD_SHIFT","can_id":cid,"at":y.first,"detail":f"median period ratio={ratio:.2f}"})
        if x.frequency_hz and y.frequency_hz:
            ratio=max(x.frequency_hz,y.frequency_hz)/min(x.frequency_hz,y.frequency_hz)
            if ratio>=frequency_ratio: events.append({"kind":"FREQUENCY_SHIFT","can_id":cid,"at":y.first,"detail":f"frequency ratio={ratio:.2f}"})
    events.sort(key=lambda e:(e["at"],e["can_id"],e["kind"]))
    first=events[0] if events else None
    clusters=[]
    if events:
        cluster=[events[0]]
        for e in events[1:]:
            if e["at"]-cluster[0]["at"]<=0.050: cluster.append(e)
            else:
                if len(cluster)>1: clusters.append({"kind":"MULTI_ID_EVENT","at":cluster[0]["at"],"count":len(cluster),"can_ids":sorted({x["can_id"] for x in cluster})})
                cluster=[e]
        if len(cluster)>1: clusters.append({"kind":"MULTI_ID_EVENT","at":cluster[0]["at"],"count":len(cluster),"can_ids":sorted({x["can_id"] for x in cluster})})
    return {"first_observed_change":first,"events":events,"multi_id_events":clusters,
            "normal":[asdict(v) for v in a.values()],"fault":[asdict(v) for v in b.values()],
            "causality":"NOT_ESTABLISHED","ecu_ownership":"UNKNOWN"}
