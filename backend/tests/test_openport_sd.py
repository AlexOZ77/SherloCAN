from app.capture.openport_sd import validate_logcfg,build_obd01_template

def test_generated_obd_template_is_explicitly_active():
    text=build_obd01_template(["rpm","speed"])
    r=validate_logcfg(text)
    assert r.type_name=="obd"
    assert r.protocol_id==6
    assert "ACTIVE_DIAGNOSTIC_REQUESTS" in r.features
    assert any("not passive raw-CAN" in x for x in r.warnings)

def test_filename_is_required():
    r=validate_logcfg("type=obd\nprotocolid=6\n","wrong.txt")
    assert r.filename_ok is False
