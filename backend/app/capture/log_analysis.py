from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import median

from .base import CANFrame
from .replay import FileReplayAdapter


def analyze_frames(frames: list[CANFrame], gap_ratio: float = 3.0) -> dict:
    if gap_ratio <= 1:
        raise ValueError("gap_ratio must be > 1")
    ordered = sorted(frames, key=lambda f: f.timestamp)
    if not ordered:
        raise ValueError("log contains no frames")

    grouped: dict[int, list[CANFrame]] = defaultdict(list)
    for frame in ordered:
        grouped[frame.can_id].append(frame)

    ids = []
    anomalies = []
    for can_id, items in sorted(grouped.items()):
        periods = [b.timestamp - a.timestamp for a, b in zip(items, items[1:]) if b.timestamp >= a.timestamp]
        positive = [p for p in periods if p > 0]
        med = median(positive) if positive else None
        duration = items[-1].timestamp - items[0].timestamp
        hz = ((len(items) - 1) / duration) if len(items) > 1 and duration > 0 else None
        dlcs = [f.dlc for f in items]
        ids.append({
            "can_id": hex(can_id),
            "count": len(items),
            "median_period_ms": round(med * 1000, 3) if med else None,
            "observed_rate_hz": round(hz, 3) if hz else None,
            "typical_dlc": int(median(dlcs)),
            "first_timestamp": items[0].timestamp,
            "last_timestamp": items[-1].timestamp,
            "ecu_owner": "UNKNOWN",
        })
        if med:
            for prev, current in zip(items, items[1:]):
                gap = current.timestamp - prev.timestamp
                ratio = gap / med
                if ratio >= gap_ratio:
                    anomalies.append({
                        "kind": "LONG_GAP",
                        "can_id": hex(can_id),
                        "timestamp": current.timestamp,
                        "gap_ms": round(gap * 1000, 3),
                        "ratio": round(ratio, 2),
                        "detail": f"Observed inter-frame gap {gap * 1000:.3f} ms ({ratio:.2f}x median)",
                        "ecu_owner": "UNKNOWN",
                    })

    start, end = ordered[0].timestamp, ordered[-1].timestamp
    duration = max(0.0, end - start)
    # Compact timeline buckets for UI; no payload interpretation is performed.
    bucket_count = min(120, max(1, len(ordered)))
    width = duration / bucket_count if duration > 0 else 1.0
    buckets = [0] * bucket_count
    for frame in ordered:
        index = min(bucket_count - 1, int((frame.timestamp - start) / width)) if duration > 0 else 0
        buckets[index] += 1

    return {
        "frame_count": len(ordered),
        "unique_can_ids": len(grouped),
        "first_timestamp": start,
        "last_timestamp": end,
        "duration_s": round(duration, 6),
        "ids": ids,
        "timeline": {"bucket_width_s": width, "counts": buckets},
        "anomalies": sorted(anomalies, key=lambda a: a["timestamp"]),
        "interpretation": "Timing/rate observations only. ECU ownership and root cause remain UNKNOWN.",
    }


def analyze_normalized_log(path: Path, gap_ratio: float = 3.0) -> dict:
    adapter = FileReplayAdapter()
    adapter.open(path=path)
    try:
        return analyze_frames(list(adapter.start()), gap_ratio=gap_ratio)
    finally:
        adapter.close()
