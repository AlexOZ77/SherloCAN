import sys,types
from app.capture.j2534 import atomic_capture

class Result:
    def to_dict(self): return {"frames_observed":1,"frames_accepted":1,"frames_dropped":0,"unique_ids":1,"capture_data_loss":False,"raw_path":"x","sha256":"a"*64}

def test_atomic_capture_always_disconnects_and_closes(monkeypatch,tmp_path):
    calls=[]
    fake=types.SimpleNamespace(
        get_list_j2534_devices=lambda:["OpenPort"],
        set_j2534_device_to_connect=lambda i:calls.append(("select",i)),
        pt_open=lambda:11,
        pt_connect=lambda device,protocol,flags,bitrate:22,
        pt_disconnect=lambda channel:calls.append(("disconnect",channel)) or True,
        pt_close=lambda device:calls.append(("close",device)) or True,
        ProtocolId=types.SimpleNamespace(CAN=5),
    )
    monkeypatch.setitem(sys.modules,"J2534",fake)
    monkeypatch.setattr("app.capture.j2534.capture.capture_from_open_channel",lambda **kwargs:Result())
    result=atomic_capture.run_atomic_capture(atomic_capture.AtomicCaptureRequest(0,125000,max_frames=1),tmp_path)
    assert result["evidence"]["frames_observed"]==1
    assert result["disconnected_cleanly"] is True
    assert result["device_closed_cleanly"] is True
    assert ("disconnect",22) in calls and ("close",11) in calls
    assert result["transmit_performed"] is False
