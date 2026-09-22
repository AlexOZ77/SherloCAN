from __future__ import annotations
from dataclasses import asdict,dataclass

@dataclass(frozen=True,slots=True)
class ChannelTestResult:
    provider_index:int
    protocol:str
    bitrate:int
    device_opened:bool
    channel_connected:bool
    channel_id:int|None
    disconnected_cleanly:bool
    device_closed_cleanly:bool
    transmit_performed:bool=False
    error:str|None=None
    def to_dict(self): return asdict(self)

def run_channel_test(provider_index:int,protocol:str,bitrate:int)->ChannelTestResult:
    """Explicit connect/disconnect gate. Does not write CAN messages."""
    if protocol!="CAN": raise ValueError("Only raw CAN is allowed in passive capture v0.2")
    if bitrate<=0: raise ValueError("bitrate must be explicitly provided and > 0")
    from J2534 import (get_list_j2534_devices,set_j2534_device_to_connect,pt_open,pt_close,pt_connect,pt_disconnect,ProtocolId)
    devices=get_list_j2534_devices()
    if provider_index<0 or provider_index>=len(devices): raise IndexError("Invalid J2534 provider index")
    set_j2534_device_to_connect(provider_index)
    device_id=None; channel_id=None
    try:
        device_id=pt_open()
        if device_id is False: raise RuntimeError("PassThruOpen returned failure")
        channel_id=pt_connect(device_id,ProtocolId.CAN,0,bitrate)
        if channel_id is False: raise RuntimeError("PassThruConnect returned failure")
        disconnected=pt_disconnect(channel_id)
        closed=pt_close(device_id)
        return ChannelTestResult(provider_index,protocol,bitrate,True,True,int(channel_id),disconnected is not False,closed is not False)
    except Exception as exc:
        if channel_id not in (None,False):
            try: pt_disconnect(channel_id)
            except Exception: pass
        if device_id not in (None,False):
            try: pt_close(device_id)
            except Exception: pass
        return ChannelTestResult(provider_index,protocol,bitrate,device_id not in (None,False),False,None,False,False,error=f"{type(exc).__name__}: {exc}")
