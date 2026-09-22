from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from .base import CANFrame

@dataclass(frozen=True, slots=True)
class IDBaseline:
    can_id: int
    count: int
    median_period: float | None
    typical_dlc: int

@dataclass(frozen=True, slots=True)
class CANAnomaly:
    kind: str
    can_id: int
    timestamp: float
    detail: str

def build_baseline(frames: list[CANFrame]) -> dict[int, IDBaseline]:
    grouped: dict[int, list[CANFrame]] = {}
    for frame in frames:
        grouped.setdefault(frame.can_id, []).append(frame)

    result: dict[int, IDBaseline] = {}
    for can_id, items in grouped.items():
        items.sort(key=lambda f: f.timestamp)
        periods = [b.timestamp - a.timestamp for a, b in zip(items, items[1:])]
        dlcs = [f.dlc for f in items]
        result[can_id] = IDBaseline(
            can_id=can_id,
            count=len(items),
            median_period=median(periods) if periods else None,
            typical_dlc=int(median(dlcs)),
        )
    return result

def detect_long_gaps(
    frames: list[CANFrame],
    baseline: dict[int, IDBaseline],
    ratio: float = 3.0,
) -> list[CANAnomaly]:
    if ratio <= 1:
        raise ValueError("ratio must be > 1")
    last_seen: dict[int, float] = {}
    anomalies: list[CANAnomaly] = []
    for frame in sorted(frames, key=lambda f: f.timestamp):
        previous = last_seen.get(frame.can_id)
        expected = baseline.get(frame.can_id)
        if previous is not None and expected and expected.median_period and expected.median_period > 0:
            gap = frame.timestamp - previous
            gap_ratio = gap / expected.median_period
            if gap_ratio >= ratio:
                anomalies.append(CANAnomaly(
                    kind="LONG_GAP",
                    can_id=frame.can_id,
                    timestamp=frame.timestamp,
                    detail=f"gap={gap:.6f}s ratio={gap_ratio:.2f}",
                ))
        last_seen[frame.can_id] = frame.timestamp
    return anomalies
