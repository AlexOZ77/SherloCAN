from app.capture.j2534 import controller

class Result:
    def to_dict(self):
        return {"frames_observed":2,"frames_accepted":2,"frames_dropped":0,"unique_ids":2,"capture_data_loss":False,"raw_path":"x.csv","sha256":"a"*64}

def test_controller_returns_session_and_evidence(monkeypatch,tmp_path):
    monkeypatch.setattr(controller,"capture_from_open_channel",lambda **kwargs: Result())
    req=controller.CaptureRequest(provider_index=0,channel_id=7,bitrate=125000,max_frames=2)
    result=controller.run_bounded_capture(req,tmp_path)
    assert result["session_id"]
    assert result["request"]["bitrate"]==125000
    assert result["evidence"]["frames_observed"]==2
    assert result["evidence"]["capture_data_loss"] is False
    assert result["started_at"]
    assert result["completed_at"]
