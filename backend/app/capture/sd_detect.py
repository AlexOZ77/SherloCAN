from __future__ import annotations
import csv,ctypes,re
from dataclasses import dataclass,asdict
from pathlib import Path

@dataclass(frozen=True,slots=True)
class FormatDetection:
    classification:str
    format_name:str
    parser:str|None
    confidence:str
    reason:str

_CANDUMP=re.compile(r"^\s*(?:\([0-9.]+\)\s+)?\S+\s+[0-9A-Fa-f]{1,8}#[0-9A-Fa-f]*")

def detect_log_format(path:Path)->FormatDetection:
    sample=path.read_text(encoding="utf-8",errors="replace")[:65536]
    lines=[x for x in sample.splitlines() if x.strip()]
    if any(_CANDUMP.match(x) for x in lines[:30]):
        return FormatDetection("RAW_CAN_SUPPORTED","can-utils/candump","python-can","HIGH","Frame-level candump signature detected.")
    if path.suffix.lower()==".csv" and lines:
        try:
            header=next(csv.reader([lines[0]]))
        except Exception:
            header=[]
        norm={x.strip().lower() for x in header}
        if {"timestamp","can_id","dlc","data"}.issubset(norm):
            return FormatDetection("RAW_CAN_SUPPORTED","SherloCAN CSV","sherlocan-csv","HIGH","Canonical SherloCAN frame columns detected.")
        if len(header)>=2 and not ({"can_id","id","arbitration_id"} & norm):
            return FormatDetection("PARAMETER_LOG","parameter CSV",None,"MEDIUM","Tabular signals detected without frame-level CAN ID columns.")
    return FormatDetection("UNKNOWN","unknown",None,"LOW","No verified frame-level signature recognized.")

def discover_windows_candidates()->list[dict]:
    if not hasattr(ctypes,"windll"): return []
    k=ctypes.windll.kernel32;mask=k.GetLogicalDrives();rows=[]
    DRIVE_REMOVABLE=2
    for i in range(26):
        if not mask & (1<<i): continue
        root=Path(f"{chr(65+i)}:/")
        try: drive_type=k.GetDriveTypeW(str(root))
        except Exception: continue
        if drive_type!=DRIVE_REMOVABLE: continue
        try:
            cfg=(root/"logcfg.txt").exists()
            logs=[p for p in root.iterdir() if p.is_file() and p.name.lower()!="logcfg.txt" and p.suffix.lower() in {".csv",".log",".txt",".asc",".blf"}]
        except OSError: continue
        rows.append({"root":str(root),"removable":True,"logcfg_present":cfg,"log_count":len(logs),"candidate_reason":"REMOVABLE_WITH_LOGCFG" if cfg else ("REMOVABLE_WITH_LOGS" if logs else "REMOVABLE_ONLY"),"openport_confirmed":False})
    return rows

def detection_dict(path:Path)->dict:return asdict(detect_log_format(path))
