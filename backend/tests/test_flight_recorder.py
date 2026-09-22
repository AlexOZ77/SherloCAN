from app.capture.base import CANFrame
from app.capture.flight_recorder import FlightRecorder

def f(ts: float) -> CANFrame:
    return CANFrame(timestamp=ts, can_id=0x100, data=b"\x00")

def test_fault_window_keeps_pre_and_post_frames():
    recorder = FlightRecorder(pre_seconds=2.0, post_seconds=2.0)
    for ts in [7.0, 8.0, 9.0, 10.0]:
        recorder.ingest(f(ts))
    window = recorder.mark(10.0, "FAULT", "chassis warning")
    recorder.ingest(f(11.0))
    recorder.ingest(f(12.0))
    recorder.ingest(f(12.1))
    assert window.complete
    assert [x.timestamp for x in window.frames] == [8.0, 9.0, 10.0, 11.0, 12.0]
    assert window.marker.kind == "FAULT"
