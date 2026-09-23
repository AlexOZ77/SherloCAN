from __future__ import annotations

def assess_capture(result:dict)->dict:
    evidence=result.get("evidence") or {}
    checks=[
        {"id":"device_opened","passed":bool(result.get("device_opened")),"required":True},
        {"id":"channel_connected","passed":bool(result.get("channel_connected")),"required":True},
        {"id":"frames_observed","passed":int(evidence.get("frames_observed") or 0)>0,"required":True},
        {"id":"no_data_loss","passed":int(evidence.get("frames_dropped") or 0)==0 and not bool(evidence.get("capture_data_loss")),"required":True},
        {"id":"raw_path","passed":bool(evidence.get("raw_path")),"required":True},
        {"id":"sha256","passed":bool(evidence.get("sha256")),"required":True},
        {"id":"disconnect_clean","passed":bool(result.get("disconnected_cleanly")),"required":True},
        {"id":"device_close_clean","passed":bool(result.get("device_closed_cleanly")),"required":True},
        {"id":"no_transmit","passed":result.get("transmit_performed") is False,"required":True},
    ]
    passed=all(x["passed"] for x in checks if x["required"])
    return {"status":"PASS" if passed else "FAIL","checks":checks,
            "rule":"PASS means the bounded capture is technically usable as evidence; it does not establish diagnosis or causality."}
