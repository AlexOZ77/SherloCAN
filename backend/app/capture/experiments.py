from __future__ import annotations
import csv,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

VALID_ROLES={"NORMAL_A","FAULT_B"}

def _registry(root:Path)->Path:return root/"experiments.json"

def load_sessions(root:Path)->list[dict]:
    p=_registry(root)
    if not p.exists(): return []
    return json.loads(p.read_text(encoding="utf-8"))

def save_session(root:Path,session:dict,role:str,note:str="",trial:int|None=None)->dict:
    if role not in VALID_ROLES: raise ValueError("role must be NORMAL_A or FAULT_B")
    if not session.get("session_id"): raise ValueError("session_id is required")
    if trial is not None and trial < 1: raise ValueError("trial must be >= 1")
    root.mkdir(parents=True,exist_ok=True)
    rows=[x for x in load_sessions(root) if x["session_id"]!=session["session_id"]]
    item={"session_id":session["session_id"],"role":role,"note":note,"saved_at":datetime.now(timezone.utc).isoformat(),
          "started_at":session.get("started_at"),"completed_at":session.get("completed_at"),
          "evidence":session.get("evidence"),"error":session.get("error"),"trial":trial}
    rows.append(item);_registry(root).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    return item

def _counts(path:str|Path)->Counter[str]:
    counts:Counter[str]=Counter()
    with Path(path).open(encoding="utf-8",newline="") as h:
        for row in csv.DictReader(h): counts[row["can_id"]]+=1
    return counts

def compare_sessions(a:dict,b:dict)->dict:
    ea,eb=a.get("evidence") or {},b.get("evidence") or {}
    ca,cb=_counts(ea["raw_path"]),_counts(eb["raw_path"])
    ids=sorted(set(ca)|set(cb))
    return {"a_session_id":a["session_id"],"b_session_id":b["session_id"],
      "a_data_loss":bool(ea.get("capture_data_loss")),"b_data_loss":bool(eb.get("capture_data_loss")),
      "ids":[{"can_id":i,"normal_count":ca[i],"fault_count":cb[i],"delta":cb[i]-ca[i],
              "presence":"BOTH" if ca[i] and cb[i] else "NORMAL_ONLY" if ca[i] else "FAULT_ONLY"} for i in ids],
      "interpretation":"Descriptive RAW comparison only; ECU ownership and root cause are not inferred."}
