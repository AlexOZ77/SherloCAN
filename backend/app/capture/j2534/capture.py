from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from .reader import ReaderConfig, read_bounded
from ..live_pipeline import persist_frames

@dataclass(frozen=True, slots=True)
class J2534CaptureResult:
    provider_index: int
    protocol: str
    bitrate: int
    frames_observed: int
    frames_accepted: int
    frames_dropped: int
    unique_ids: int
    capture_data_loss: bool
    raw_path: str
    sha256: str
    transmit_performed: bool = False
    def to_dict(self): return asdict(self)

def capture_from_open_channel(
    *,
    provider_index: int,
    channel_id: int,
    bitrate: int,
    output_path: str | Path,
    timeout_ms: int = 100,
    max_frames: int = 1000,
    queue_size: int = 10000,
) -> J2534CaptureResult:
    if bitrate <= 0:
        raise ValueError("bitrate must be explicit and > 0")
    if max_frames <= 0:
        raise ValueError("max_frames must be > 0")
    if timeout_ms < 0:
        raise ValueError("timeout_ms must be >= 0")
    frames = read_bounded(ReaderConfig(channel_id=channel_id, timeout_ms=timeout_ms, max_frames=max_frames))
    summary = persist_frames(frames, output_path, queue_size=queue_size)
    return J2534CaptureResult(
        provider_index=provider_index,
        protocol="CAN",
        bitrate=bitrate,
        frames_observed=summary.frames_observed,
        frames_accepted=summary.frames_accepted,
        frames_dropped=summary.frames_dropped,
        unique_ids=summary.unique_ids,
        capture_data_loss=summary.capture_data_loss,
        raw_path=summary.raw_path,
        sha256=summary.sha256,
    )
