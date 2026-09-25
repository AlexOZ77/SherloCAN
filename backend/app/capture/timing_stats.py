from __future__ import annotations
from statistics import median

def timing_summary(timestamps:list[float])->dict:
    ts=sorted(float(x) for x in timestamps)
    periods=[b-a for a,b in zip(ts,ts[1:]) if b>=a]
    if not periods:
        return {"sample_count":len(ts),"period_count":0,"median_period":None,"mad_period":None,"iqr_period":None}
    med=median(periods)
    absdev=[abs(x-med) for x in periods]
    q=sorted(periods)
    def percentile(p:float)->float:
        if len(q)==1:return q[0]
        pos=(len(q)-1)*p
        lo=int(pos); hi=min(lo+1,len(q)-1); frac=pos-lo
        return q[lo]*(1-frac)+q[hi]*frac
    return {"sample_count":len(ts),"period_count":len(periods),"median_period":med,
            "mad_period":median(absdev),"iqr_period":percentile(.75)-percentile(.25)}
