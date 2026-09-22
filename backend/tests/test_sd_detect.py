from app.capture.sd_detect import detect_log_format

def test_candump_is_raw_can(tmp_path):
    p=tmp_path/"can.log";p.write_text("(1.234) can0 123#010203\n")
    r=detect_log_format(p)
    assert r.classification=="RAW_CAN_SUPPORTED"
    assert r.parser=="python-can"

def test_sherlocan_csv_is_raw(tmp_path):
    p=tmp_path/"raw.csv";p.write_text("sequence,timestamp,can_id,dlc,data,channel,is_extended\n1,1.0,0x123,1,00,x,false\n")
    assert detect_log_format(p).classification=="RAW_CAN_SUPPORTED"

def test_parameter_csv_never_becomes_raw_can(tmp_path):
    p=tmp_path/"params.csv";p.write_text("Time,Engine_RPM,Vehicle_Speed\n0.0,800,0\n")
    r=detect_log_format(p)
    assert r.classification=="PARAMETER_LOG"
    assert r.parser is None
