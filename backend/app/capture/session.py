from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4
from .base import CANFrame
from .flight_recorder import FlightRecorder, EventWindow
from .queue import FrameQueue

class CaptureState(StrEnum):
    CREATED="CREATED"; CAPTURING="CAPTURING"; STOPPED="STOPPED"

@dataclass(slots=True)
class CaptureSession:
    source: str
    queue_size: int = 10000
    pre_seconds: float = 60.0
    post_seconds: float = 60.0
    id: str = field(default_factory=lambda: str(uuid4()))
    state: CaptureState = CaptureState.CREATED
    frame_count: int = 0

    def __post_init__(self):
        self.queue=FrameQueue(self.queue_size)
        self.flight=FlightRecorder(self.pre_seconds,self.post_seconds)

    def start(self): self.state=CaptureState.CAPTURING
    def ingest(self,frame:CANFrame):
        if self.state != CaptureState.CAPTURING: raise RuntimeError("session is not capturing")
        accepted=self.queue.put(frame)
        self.flight.ingest(frame)
        self.frame_count += 1
        return accepted
    def mark(self,timestamp:float,kind:str,note:str="")->EventWindow:
        return self.flight.mark(timestamp,kind,note)
    def stop(self):
        self.flight.finalize(); self.state=CaptureState.STOPPED
    def status(self):
        return {"id":self.id,"source":self.source,"state":self.state,"frames":self.frame_count,
                "queue_depth":self.queue.depth,"dropped":self.queue.stats.dropped,
                "events":len(self.flight.completed)}
