from app.capture.acceptance import assess_capture

def test_acceptance_pass():
    r=assess_capture({"device_opened":True,"channel_connected":True,"disconnected_cleanly":True,
      "device_closed_cleanly":True,"transmit_performed":False,
      "evidence":{"frames_observed":10,"frames_dropped":0,"capture_data_loss":False,"raw_path":"x.csv","sha256":"abc"}})
    assert r["status"]=="PASS"

def test_acceptance_fails_data_loss():
    r=assess_capture({"device_opened":True,"channel_connected":True,"disconnected_cleanly":True,
      "device_closed_cleanly":True,"transmit_performed":False,
      "evidence":{"frames_observed":10,"frames_dropped":1,"capture_data_loss":True,"raw_path":"x.csv","sha256":"abc"}})
    assert r["status"]=="FAIL"
