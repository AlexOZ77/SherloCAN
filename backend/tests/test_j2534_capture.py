from app.capture.base import CANFrame
from app.capture.j2534 import capture as capture_module

def test_capture_reports_measured_summary(monkeypatch, tmp_path):
    frames=[
        CANFrame(timestamp=1.0,can_id=0x100,data=b"\x01"),
        CANFrame(timestamp=2.0,can_id=0x101,data=b"\x02"),
    ]
    monkeypatch.setattr(capture_module,"read_bounded",lambda config: frames)
    result=capture_module.capture_from_open_channel(
        provider_index=0,channel_id=7,bitrate=125000,
        output_path=tmp_path/"capture.csv",max_frames=2,
    )
    assert result.frames_observed==2
    assert result.frames_accepted==2
    assert result.frames_dropped==0
    assert result.unique_ids==2
    assert result.capture_data_loss is False
    assert result.transmit_performed is False
    assert len(result.sha256)==64

def test_capture_surfaces_queue_loss(monkeypatch,tmp_path):
    frames=[
        CANFrame(timestamp=1.0,can_id=0x100,data=b"\x01"),
        CANFrame(timestamp=2.0,can_id=0x101,data=b"\x02"),
    ]
    monkeypatch.setattr(capture_module,"read_bounded",lambda config: frames)
    result=capture_module.capture_from_open_channel(
        provider_index=0,channel_id=7,bitrate=125000,
        output_path=tmp_path/"loss.csv",max_frames=2,queue_size=1,
    )
    assert result.frames_dropped==1
    assert result.capture_data_loss is True
