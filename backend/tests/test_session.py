from app.capture.base import CANFrame
from app.capture.session import CaptureSession, CaptureState

def test_session_tracks_frames_drops_and_event():
    s=CaptureSession(source="synthetic",queue_size=1,pre_seconds=1,post_seconds=1)
    s.start()
    assert s.ingest(CANFrame(1.0,0x100,b"\x00"))
    assert not s.ingest(CANFrame(1.1,0x100,b"\x01"))
    s.mark(1.1,"FAULT")
    s.ingest(CANFrame(2.2,0x100,b"\x02"))
    s.stop()
    status=s.status()
    assert status["state"] == CaptureState.STOPPED
    assert status["frames"] == 3
    assert status["dropped"] == 2
    assert status["events"] == 1
