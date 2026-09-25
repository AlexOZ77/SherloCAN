from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from ..base import CANFrame

@dataclass(frozen=True, slots=True)
class ReaderConfig:
    channel_id: int
    timeout_ms: int = 100
    max_frames: int = 1000

def _message_bytes(message) -> bytes:
    """Return the valid J2534 data block across supported j2534-api variants."""
    if hasattr(message, "get_data"):
        return bytes(message.get_data())
    if hasattr(message, "get_data_bytes"):
        return bytes(message.get_data_bytes())
    data_size = int(getattr(message, "DataSize", 0))
    data = getattr(message, "Data", None)
    if data is None:
        raise TypeError("Unsupported J2534 message object: no data accessor")
    return bytes(data[:data_size])

def normalize_raw_can(message, timestamp: float | None = None) -> CANFrame:
    """Normalize one received raw-CAN PASSTHRU_MSG into SherloCAN's internal frame."""
    data = _message_bytes(message)
    if len(data) < 4:
        raise ValueError("J2534 raw CAN message is shorter than its 4-byte identifier")
    can_id = int.from_bytes(data[:4], "big")
    rx_status = int(getattr(message, "RxStatus", getattr(message, "receive_status", 0)) or 0)
    # SAE J2534 RxStatus.CAN_29BIT_ID = 0x00000100.
    is_extended = bool(rx_status & 0x00000100)
    if not is_extended and can_id > 0x7FF:
        # Defensive fallback for provider variants that omit RxStatus.
        is_extended = True
    if timestamp is None:
        device_timestamp_us = int(getattr(message, "Timestamp", getattr(message, "timestamp", 0)) or 0)
        timestamp = device_timestamp_us / 1_000_000 if device_timestamp_us > 0 else monotonic()
    return CANFrame(
        timestamp=timestamp,
        can_id=can_id,
        data=data[4:],
        channel="j2534_raw_can",
        is_extended=is_extended,
    )

def read_bounded(config: ReaderConfig) -> list[CANFrame]:
    """Bounded receive loop. This module does not import or call a write API."""
    from J2534 import pt_read_message, PassThruMsgBuilder, ProtocolId

    frames: list[CANFrame] = []
    attempts = 0
    while len(frames) < config.max_frames and attempts < config.max_frames * 4:
        attempts += 1
        message = PassThruMsgBuilder(ProtocolId.CAN, 0)
        result = pt_read_message(config.channel_id, message, 1, config.timeout_ms)
        if result != 0:
            break
        rx_status = int(getattr(message, "RxStatus", 0) or 0)
        # Ignore transmit echoes/indications. SherloCAN v0.2.1 does not intentionally transmit.
        if rx_status & 0x00000001:
            continue
        try:
            frames.append(normalize_raw_can(message))
        except ValueError:
            continue
    return frames
