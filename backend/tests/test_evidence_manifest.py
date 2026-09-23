from app.capture.evidence_manifest import build_evidence_manifest

def test_manifest_keeps_unknown_ownership_and_causality():
    m=build_evidence_manifest({"session_id":"s1","device_opened":True,"channel_connected":True,
      "disconnected_cleanly":True,"device_closed_cleanly":True,"transmit_performed":False,
      "evidence":{"frames_observed":5,"raw_path":"x.csv","sha256":"abc"}})
    assert m["claims"]["traffic_confirmed"] is True
    assert m["claims"]["ecu_ownership"]=="UNKNOWN"
    assert m["claims"]["causality"]=="NOT_ESTABLISHED"
