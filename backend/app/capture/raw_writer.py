from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from .base import CANFrame

class RawCaptureWriter:
    """Append-only CSV raw capture with final SHA-256 integrity digest."""

    HEADER = ["sequence", "timestamp", "can_id", "dlc", "data", "channel", "is_extended"]

    def __init__(self, path: str | Path, flush_every: int = 250) -> None:
        self.path = Path(path)
        self.flush_every = max(1, flush_every)
        self._handle = None
        self._writer = None
        self._sequence = 0

    def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("x", encoding="utf-8", newline="")
        self._writer = csv.writer(self._handle)
        self._writer.writerow(self.HEADER)
        self._handle.flush()

    def write(self, frame: CANFrame) -> None:
        if self._writer is None or self._handle is None:
            raise RuntimeError("writer is not open")
        self._writer.writerow([
            self._sequence,
            f"{frame.timestamp:.9f}",
            hex(frame.can_id),
            frame.dlc,
            frame.data.hex().upper(),
            frame.channel,
            str(frame.is_extended).lower(),
        ])
        self._sequence += 1
        if self._sequence % self.flush_every == 0:
            self._handle.flush()

    def write_batch(self, frames: list[CANFrame]) -> None:
        for frame in frames:
            self.write(frame)

    def close(self) -> str:
        if self._handle is not None:
            self._handle.flush()
            self._handle.close()
            self._handle = None
            self._writer = None
        return self.sha256()

    def sha256(self) -> str:
        digest = hashlib.sha256()
        with self.path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @property
    def frame_count(self) -> int:
        return self._sequence
