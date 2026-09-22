from app.capture.base import CANFrame
from app.capture.queue import FrameQueue

def frame(ts: float) -> CANFrame:
    return CANFrame(timestamp=ts, can_id=0x123, data=b"\x01")

def test_overflow_is_counted():
    queue = FrameQueue(maxsize=2)
    assert queue.put(frame(0.0))
    assert queue.put(frame(0.1))
    assert not queue.put(frame(0.2))
    assert queue.stats.received == 3
    assert queue.stats.enqueued == 2
    assert queue.stats.dropped == 1
    assert queue.depth == 2
