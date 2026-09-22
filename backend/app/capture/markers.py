from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path

VALID_MARKERS={"IGN_ON","START","ENGINE_RUNNING","FAULT","DTC","WIGGLE","ROAD_BUMP","CONNECTOR","OTHER"}

def _path(root:Path,session_id:str)->Path:return root/f"{session_id}.markers.json"

def load_markers(root:Path,session_id:str)->list[dict]:
    p=_path(root,session_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def add_marker(root:Path,session_id:str,kind:str,timestamp:float,note:str="")->dict:
    if kind not in VALID_MARKERS: raise ValueError(f"unsupported marker: {kind}")
    if timestamp<0: raise ValueError("timestamp must be >= 0")
    rows=load_markers(root,session_id)
    item={"kind":kind,"timestamp":timestamp,"note":note,"created_at":datetime.now(timezone.utc).isoformat()}
    rows.append(item);rows.sort(key=lambda x:x["timestamp"])
    root.mkdir(parents=True,exist_ok=True);_path(root,session_id).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    return item

def marker_time(root:Path,session_id:str,kind:str)->float|None:
    matches=[m["timestamp"] for m in load_markers(root,session_id) if m["kind"]==kind]
    return matches[0] if matches else None
