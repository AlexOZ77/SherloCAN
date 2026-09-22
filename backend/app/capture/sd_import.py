from __future__ import annotations
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path

ALLOWED={".csv",".log",".txt"}

def inspect_sd_logs(root:Path)->list[dict]:
    if not root.exists() or not root.is_dir(): raise ValueError("SD/log folder does not exist")
    rows=[]
    for p in sorted(root.iterdir()):
        if p.is_file() and p.name.lower()!="logcfg.txt" and p.suffix.lower() in ALLOWED:
            h=hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
            rows.append({"name":p.name,"path":str(p),"size_bytes":p.stat().st_size,"sha256":h.hexdigest(),"modified":p.stat().st_mtime,"format":p.suffix.lower().lstrip(".")})
    return rows

def import_sd_log(source:Path,dest_root:Path)->dict:
    if not source.exists() or not source.is_file(): raise ValueError("source log does not exist")
    if source.suffix.lower() not in ALLOWED: raise ValueError("unsupported SD log extension")
    sid="sd-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder=dest_root/"sd_imports"/sid;folder.mkdir(parents=True,exist_ok=False)
    target=folder/source.name
    shutil.copy2(source,target)
    h=hashlib.sha256(target.read_bytes()).hexdigest()
    meta={"session_id":sid,"source_kind":"OPENPORT_SD_IMPORT","original_name":source.name,"original_path":str(source),"evidence_copy":str(target),"sha256":h,"size_bytes":target.stat().st_size,"format":target.suffix.lower().lstrip("."),"imported_at":datetime.now(timezone.utc).isoformat(),"parsed":False,"interpretation":"Original SD log preserved. Format parsing and CAN semantics are not inferred."}
    (folder/"import.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    return meta
