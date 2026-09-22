from pathlib import Path
from app.capture.base import CANFrame
from app.capture.live_pipeline import persist_frames

def f(ts,i): return CANFrame(timestamp=ts,can_id=i,data=b"\\x01")
def test_pipeline_surfaces_capture_data_loss(tmp_path:Path):
    result=persist_frames([f(1,1),f(2,2)],tmp_path/"raw.csv",queue_size=1)
    assert result.frames_observed==2
    assert result.frames_accepted==1
    assert result.frames_dropped==1
    assert result.capture_data_loss is True
    assert result.unique_ids==1
    assert len(result.sha256)==64
