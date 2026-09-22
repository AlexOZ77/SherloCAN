from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
from .capture import capture_from_open_channel

@dataclass(frozen=True,slots=True)
class CaptureRequest:
    provider_index:int
    channel_id:int
    bitrate:int
    timeout_ms:int=100
    max_frames:int=1000
    queue_size:int=10000

def run_bounded_capture(request:CaptureRequest,root:Path)->dict:
    """Run one explicit bounded capture and return evidence metadata."""
    session_id=str(uuid4())
    root.mkdir(parents=True,exist_ok=True)
    raw_path=root/f"{session_id}.csv"
    started=datetime.now(timezone.utc)
    result=capture_from_open_channel(
        provider_index=request.provider_index,channel_id=request.channel_id,
        bitrate=request.bitrate,output_path=raw_path,timeout_ms=request.timeout_ms,
        max_frames=request.max_frames,queue_size=request.queue_size,
    )
    return {
        "session_id":session_id,
        "started_at":started.isoformat(),
        "completed_at":datetime.now(timezone.utc).isoformat(),
        "request":asdict(request),
        "evidence":result.to_dict(),
    }
