from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import re

@dataclass(frozen=True,slots=True)
class ConfigCheck:
    valid:bool;filename_ok:bool;type_name:str|None;protocol_id:int|None;warnings:list[str];features:list[str]

def validate_logcfg(text:str,filename:str="logcfg.txt")->ConfigCheck:
    clean=[re.sub(r";.*$","",x).strip() for x in text.splitlines()]
    clean=[x for x in clean if x]
    pairs={}
    for line in clean:
        if "=" in line:
            k,v=line.split("=",1);pairs.setdefault(k.strip().lower(),[]).append(v.strip())
    t=(pairs.get("type") or [None])[0]
    pid=None
    if pairs.get("protocolid"):
        try: pid=int(pairs["protocolid"][0],0)
        except ValueError: pass
    warnings=[]
    if filename.lower()!="logcfg.txt":warnings.append("OpenPort standalone configuration must be named logcfg.txt.")
    if not t:warnings.append("No channel type=... found.")
    features=[]
    if t=="obd":
        features.append("ACTIVE_DIAGNOSTIC_REQUESTS")
        warnings.append("type=obd sends diagnostic requests; it is not passive raw-CAN capture.")
    if any(k in pairs for k in ("mode","paramid")):features.append("PARAMETER_LOGGING")
    return ConfigCheck(not warnings or (t=="obd" and len(warnings)==1),filename.lower()=="logcfg.txt",t,pid,warnings,features)

def build_obd01_template(params:list[str])->str:
    known={
      "rpm":("Engine_RPM","0x0C","16","x,0.25,*"),
      "speed":("Vehicle_Speed","0x0D","8","x"),
      "coolant":("Coolant_Temp","0x05","8","x,40,-"),
    }
    lines=["; SherloCAN generated OpenPort 2.0 standalone configuration",
           "; ACTIVE OBD parameter logging — NOT passive CAN sniffing",
           "type=obd","protocolid=6"]
    for key in params:
        if key not in known: raise ValueError(f"unsupported template parameter: {key}")
        name,pid,bits,scale=known[key]
        lines += ["",f"paramname={name}","mode=0x01",f"paramid={pid}",f"databits={bits}",f"scalingrpn={scale}"]
    return "\n".join(lines)+"\n"
