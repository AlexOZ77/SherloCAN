from app.capture.base import CANFrame
from app.capture.session import CaptureSession

def frame(ts:float)->CANFrame:
    return CANFrame(timestamp=ts,can_id=0x123,dlc=1,data=b"\\x00",channel="test",is_extended=False)

def test_dropped_frame_does_not_enter_flight_recorder():
    s=CaptureSession(source="test",queue_size=1,pre_seconds=60,post_seconds=60)
    s.start()
    assert s.ingest(frame(1.0)) is True
    assert s.ingest(frame(2.0)) is False
    window=s.mark(2.0,"FAULT")
    assert [x.timestamp for x in window.frames] == [1.0]
    assert s.status()["dropped"] == 1
