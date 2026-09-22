from __future__ import annotations
from dataclasses import asdict, dataclass
import os, platform, struct

@dataclass(frozen=True, slots=True)
class J2534DeviceInfo:
    name: str
    vendor: str
    dll_path: str
    registry_view: str
    process_bits: int
    dll_exists: bool
    architecture_compatible: bool | None
    source: str = "WINDOWS_REGISTRY"

    def to_dict(self): return asdict(self)

def _views():
    import winreg
    result=[("native",0)]
    if hasattr(winreg,"KEY_WOW64_32KEY"): result.append(("32-bit",winreg.KEY_WOW64_32KEY))
    if hasattr(winreg,"KEY_WOW64_64KEY"): result.append(("64-bit",winreg.KEY_WOW64_64KEY))
    return result

def discover_j2534_devices() -> list[J2534DeviceInfo]:
    if platform.system()!="Windows": return []
    import winreg
    roots=[r"SOFTWARE\PassThruSupport.04.04",r"SOFTWARE\PassThruSupport.05.00"]
    found={}
    bits=struct.calcsize("P")*8
    for root in roots:
      for view,flag in _views():
       try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,root,0,winreg.KEY_READ|flag) as base:
         count=winreg.QueryInfoKey(base)[0]
         for i in range(count):
          sub=winreg.EnumKey(base,i)
          with winreg.OpenKey(base,sub) as key:
           vals={}
           for keyname in ("Name","Vendor","FunctionLibrary"):
            try: vals[keyname]=winreg.QueryValueEx(key,keyname)[0]
            except OSError: vals[keyname]=""
           path=os.path.expandvars(str(vals.get("FunctionLibrary","")))
           name=str(vals.get("Name") or sub)
           vendor=str(vals.get("Vendor") or "UNKNOWN")
           item=J2534DeviceInfo(name,vendor,path,view,bits,os.path.isfile(path),None)
           found[(name,path)]=item
       except OSError: pass
    return list(found.values())
