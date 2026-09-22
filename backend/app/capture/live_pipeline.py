from __future__ import annotations
from dataclasses import asdict,dataclass
from pathlib import Path
from .base import CANFrame
from .session import CaptureSession
from .raw_writer import RawCaptureWriter

@dataclass(frozen=True,slots=True)
class CaptureSummary:
    frames_observed:int
    frames_accepted:int
    frames_dropped:int
    unique_ids:int
    raw_path:str
    sha256:str
    capture_data_loss:bool
    def to_dict(self): return asdict(self)

def persist_frames(frames:list[CANFrame],path:str|Path,queue_size:int=10000)->CaptureSummary:
    """Deterministic sink used by replay and future J2534 reader."""
    session=CaptureSession(source="j2534-read",queue_size=queue_size)
    writer=RawCaptureWriter(path)
    writer.open(); session.start()
    ids=set()
    for frame in frames:
        accepted=session.ingest(frame)
        if accepted:
            writer.write(frame); ids.add(frame.can_id)
    session.stop()
    digest=writer.close()
    stats=session.queue.stats
    return CaptureSummary(stats.received,stats.enqueued,stats.dropped,len(ids),str(path),digest,stats.dropped>0)
