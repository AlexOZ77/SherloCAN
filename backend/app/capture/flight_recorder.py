from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from .base import CANFrame

@dataclass(frozen=True, slots=True)
class CaptureMarker:
    timestamp: float
    kind: str
    note: str = ""

@dataclass(slots=True)
class EventWindow:
    marker: CaptureMarker
    start_timestamp: float
    end_timestamp: float
    frames: list[CANFrame] = field(default_factory=list)
    complete: bool = False

class FlightRecorder:
    """Time-based pre/post event recorder independent of adapter type."""

    def __init__(self, pre_seconds: float = 60.0, post_seconds: float = 60.0) -> None:
        if pre_seconds < 0 or post_seconds < 0:
            raise ValueError("window durations cannot be negative")
        self.pre_seconds = pre_seconds
        self.post_seconds = post_seconds
        self._buffer: deque[CANFrame] = deque()
        self._active: list[EventWindow] = []
        self.completed: list[EventWindow] = []

    def ingest(self, frame: CANFrame) -> None:
        self._buffer.append(frame)
        cutoff = frame.timestamp - self.pre_seconds
        while self._buffer and self._buffer[0].timestamp < cutoff:
            self._buffer.popleft()

        for window in list(self._active):
            if frame.timestamp <= window.end_timestamp:
                if frame.timestamp > window.marker.timestamp:
                    window.frames.append(frame)
            else:
                window.complete = True
                self._active.remove(window)
                self.completed.append(window)

    def mark(self, timestamp: float, kind: str, note: str = "") -> EventWindow:
        marker = CaptureMarker(timestamp=timestamp, kind=kind.upper(), note=note)
        start = timestamp - self.pre_seconds
        end = timestamp + self.post_seconds
        pre_frames = [f for f in self._buffer if start <= f.timestamp <= timestamp]
        window = EventWindow(marker=marker, start_timestamp=start, end_timestamp=end, frames=pre_frames)
        if self.post_seconds == 0:
            window.complete = True
            self.completed.append(window)
        else:
            self._active.append(window)
        return window

    def finalize(self) -> list[EventWindow]:
        for window in list(self._active):
            window.complete = True
            self.completed.append(window)
        self._active.clear()
        return self.completed
