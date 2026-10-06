from pathlib import Path

from app.capture.base import CANFrame
from app.capture.log_analysis import analyze_frames, analyze_normalized_log


def test_analyze_frames_reports_rate_period_and_gap():
    frames = [
        CANFrame(0.00, 0x123, b"\x01"),
        CANFrame(0.01, 0x123, b"\x02"),
        CANFrame(0.02, 0x123, b"\x03"),
        CANFrame(0.10, 0x123, b"\x04"),
        CANFrame(0.00, 0x456, b"\x00\x01"),
        CANFrame(0.02, 0x456, b"\x00\x02"),
    ]
    result = analyze_frames(frames, gap_ratio=3.0)
    assert result["frame_count"] == 6
    assert result["unique_can_ids"] == 2
    row = next(x for x in result["ids"] if x["can_id"] == "0x123")
    assert row["count"] == 4
    assert row["median_period_ms"] == 10.0
    assert row["typical_dlc"] == 1
    assert row["ecu_owner"] == "UNKNOWN"
    assert any(x["kind"] == "LONG_GAP" and x["can_id"] == "0x123" for x in result["anomalies"])
    assert sum(result["timeline"]["counts"]) == 6


def test_analysis_reads_existing_normalized_replay(tmp_path: Path):
    path = tmp_path / "frames.csv"
    path.write_text(
        "timestamp,can_id,data,channel,is_extended\n"
        "0.000,0x100,01,primary_can,false\n"
        "0.010,0x100,02,primary_can,false\n"
        "0.020,0x200,AABB,primary_can,false\n",
        encoding="utf-8",
    )
    result = analyze_normalized_log(path)
    assert result["frame_count"] == 3
    assert result["unique_can_ids"] == 2
    assert result["interpretation"].startswith("Timing/rate observations only")


def test_empty_analysis_rejected():
    import pytest
    with pytest.raises(ValueError, match="no frames"):
        analyze_frames([])
