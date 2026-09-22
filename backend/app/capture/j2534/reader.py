from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from ..base import CANFrame

@dataclass(frozen=True, slots=True)
class ReaderConfig:
    channel_id: int
    timeout_ms: int = 100
    max_frames: int = 1000

def normalize_raw_can(message, timestamp: float | None = None) -> CANFrame:
    """Normalize a raw J2534 CAN message into SherloCAN's internal frame."""
    data = bytes(message.get_data_bytes())
    if len(data) < 4:
        raise ValueError("J2534 raw CAN message is shorter than its 4-byte identifier")
    can_id = int.from_bytes(data[:4], "big")
    return CANFrame(
        timestamp=monotonic() if timestamp is None else timestamp,
        can_id=can_id,
        data=data[4:],
        channel="j2534_raw_can",
        is_extended=can_id > 0x7FF,
    )

def read_bounded(config: ReaderConfig) -> list[CANFrame]:
    """Bounded receive loop. This module does not import or call a write API."""
    from J2534 import pt_read_message, PassThruMsgBuilder, ProtocolId

    frames: list[CANFrame] = []
    for _ in range(config.max_frames):
        message = PassThruMsgBuilder(ProtocolId.CAN, 0)
        result = pt_read_message(config.channel_id, message, 1, config.timeout_ms)
        if result != 0:
            break
        frames.append(normalize_raw_can(message))
    return frames
