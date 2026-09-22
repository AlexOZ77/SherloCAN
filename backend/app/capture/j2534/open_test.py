from __future__ import annotations
from dataclasses import asdict, dataclass
from .pe import dll_architecture, process_architecture, architecture_compatible

@dataclass(frozen=True, slots=True)
class OpenTestResult:
    provider_index:int
    name:str
    dll_path:str
    dll_architecture:str
    process_architecture:str
    architecture_compatible:bool|None
    device_opened:bool
    device_id:int|None
    closed_cleanly:bool
    channel_connected:bool=False
    capture_validated:bool=False
    error:str|None=None
    def to_dict(self): return asdict(self)

def run_open_test(provider_index:int=0)->OpenTestResult:
    """Controlled PassThruOpen/Close only. No protocol channel and no vehicle messages."""
    from J2534 import get_list_j2534_devices,set_j2534_device_to_connect,pt_open,pt_close
    devices=get_list_j2534_devices()
    if not devices: raise RuntimeError("No J2534 devices registered")
    if provider_index<0 or provider_index>=len(devices): raise IndexError("Invalid J2534 provider index")
    name,dll_path=devices[provider_index]
    arch=dll_architecture(dll_path); compatible=architecture_compatible(arch)
    if compatible is not True:
        return OpenTestResult(provider_index,name,dll_path,arch,process_architecture(),compatible,False,None,False,error="DLL architecture is not compatible with this process")
    set_j2534_device_to_connect(provider_index)
    device_id=None
    try:
        opened=pt_open()
        if opened is False:
            return OpenTestResult(provider_index,name,dll_path,arch,process_architecture(),True,False,None,False,error="PassThruOpen returned failure")
        device_id=int(opened)
        closed=pt_close(device_id)
        return OpenTestResult(provider_index,name,dll_path,arch,process_architecture(),True,True,device_id,closed is not False)
    except Exception as exc:
        if device_id is not None:
            try: pt_close(device_id)
            except Exception: pass
        return OpenTestResult(provider_index,name,dll_path,arch,process_architecture(),True,False,device_id,False,error=f"{type(exc).__name__}: {exc}")
