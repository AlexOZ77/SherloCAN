from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator
from .base import CANFrame, CaptureAdapter

class FileReplayAdapter(CaptureAdapter):
    """Deterministic CSV replay source used before real J2534 capture."""

    def __init__(self) -> None:
        self.path: Path | None = None
        self._running = False

    def discover(self) -> list[dict]:
        return [{"id": "file-replay", "name": "File Replay", "available": True}]

    def open(self, **config) -> None:
        path = config.get("path")
        if not path:
            raise ValueError("path is required")
        candidate = Path(path)
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        self.path = candidate

    def start(self) -> Iterator[CANFrame]:
        if self.path is None:
            raise RuntimeError("adapter is not open")
        self._running = True
        with self.path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if not self._running:
                    break
                payload = bytes.fromhex(row["data"].replace(" ", ""))
                yield CANFrame(
                    timestamp=float(row["timestamp"]),
                    can_id=int(row["can_id"], 0),
                    data=payload,
                    channel=row.get("channel") or "primary_can",
                    is_extended=(row.get("is_extended", "false").lower() == "true"),
                )

    def stop(self) -> None:
        self._running = False

    def close(self) -> None:
        self.stop()
        self.path = None

    def get_status(self) -> dict:
        return {"id": "file-replay", "name": "File Replay", "available": True,
                "state": "open" if self.path else "closed"}

    def get_capabilities(self) -> dict:
        return {"read": True, "transmit": False, "replay": True}
