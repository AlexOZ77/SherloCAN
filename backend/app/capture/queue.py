from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Full, Queue
from .base import CANFrame

@dataclass(slots=True)
class QueueStats:
    received: int = 0
    enqueued: int = 0
    dropped: int = 0
    max_depth: int = 0

class FrameQueue:
    """Bounded queue. Overflow is explicit and never silently hidden."""

    def __init__(self, maxsize: int = 10000) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._queue: Queue[CANFrame] = Queue(maxsize=maxsize)
        self.stats = QueueStats()

    def put(self, frame: CANFrame) -> bool:
        self.stats.received += 1
        try:
            self._queue.put_nowait(frame)
        except Full:
            self.stats.dropped += 1
            return False
        self.stats.enqueued += 1
        self.stats.max_depth = max(self.stats.max_depth, self._queue.qsize())
        return True

    def get(self, timeout: float | None = None) -> CANFrame | None:
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def drain(self, limit: int | None = None) -> list[CANFrame]:
        frames: list[CANFrame] = []
        while limit is None or len(frames) < limit:
            frame = self.get(timeout=0)
            if frame is None:
                break
            frames.append(frame)
        return frames

    @property
    def depth(self) -> int:
        return self._queue.qsize()
