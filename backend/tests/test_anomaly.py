from app.capture.base import CANFrame
from app.capture.anomaly import build_baseline, detect_long_gaps

def f(ts: float) -> CANFrame:
    return CANFrame(timestamp=ts, can_id=0x321, data=b"\x01\x02")

def test_long_gap_uses_baseline_period_ratio():
    baseline_frames = [f(0.00), f(0.01), f(0.02), f(0.03)]
    baseline = build_baseline(baseline_frames)
    fault_frames = [f(1.00), f(1.01), f(1.02), f(1.08)]
    anomalies = detect_long_gaps(fault_frames, baseline, ratio=3.0)
    assert len(anomalies) == 1
    assert anomalies[0].kind == "LONG_GAP"
    assert anomalies[0].can_id == 0x321
