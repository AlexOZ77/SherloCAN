from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4

@dataclass(frozen=True,slots=True)
class AtomicCaptureRequest:
    provider_index:int
    bitrate:int
    timeout_ms:int=100
    max_frames:int=1000
    queue_size:int=10000

def run_atomic_capture(request:AtomicCaptureRequest,root:Path)->dict:
    """Own the complete J2534 handle lifecycle for one bounded raw-CAN capture."""
    if request.bitrate<=0: raise ValueError("bitrate must be explicit and > 0")
    if request.max_frames<=0: raise ValueError("max_frames must be > 0")
    if request.timeout_ms<0: raise ValueError("timeout_ms must be >= 0")
    from J2534 import get_list_j2534_devices,set_j2534_device_to_connect,pt_open,pt_close,pt_connect,pt_disconnect,ProtocolId
    from .capture import capture_from_open_channel
    devices=get_list_j2534_devices()
    if request.provider_index<0 or request.provider_index>=len(devices): raise IndexError("Invalid J2534 provider index")
    session_id=str(uuid4()); root.mkdir(parents=True,exist_ok=True)
    raw_path=root/f"{session_id}.csv"; started=datetime.now(timezone.utc)
    device_id=None; channel_id=None; evidence=None; error=None
    disconnected=False; closed=False
    try:
        set_j2534_device_to_connect(request.provider_index)
        device_id=pt_open()
        if device_id is False: raise RuntimeError("PassThruOpen returned failure")
        channel_id=pt_connect(device_id,ProtocolId.CAN,0,request.bitrate)
        if channel_id is False: raise RuntimeError("PassThruConnect returned failure")
        evidence=capture_from_open_channel(
            provider_index=request.provider_index,channel_id=int(channel_id),bitrate=request.bitrate,
            output_path=raw_path,timeout_ms=request.timeout_ms,max_frames=request.max_frames,queue_size=request.queue_size,
        ).to_dict()
    except Exception as exc:
        error=f"{type(exc).__name__}: {exc}"
    finally:
        if channel_id not in (None,False):
            try: disconnected=pt_disconnect(channel_id) is not False
            except Exception: disconnected=False
        if device_id not in (None,False):
            try: closed=pt_close(device_id) is not False
            except Exception: closed=False
    return {
        "session_id":session_id,"started_at":started.isoformat(),
        "completed_at":datetime.now(timezone.utc).isoformat(),
        "request":asdict(request),"device_opened":device_id not in (None,False),
        "channel_connected":channel_id not in (None,False),
        "disconnected_cleanly":disconnected,"device_closed_cleanly":closed,
        "evidence":evidence,"error":error,"transmit_performed":False,
    }
