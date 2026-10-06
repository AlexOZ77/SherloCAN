from app.capture.openport_profiles import list_profiles, render_profile, validate_custom_profile


def test_profile_catalog_has_ready_raw_and_custom_modes():
    profiles={x["id"]:x for x in list_profiles()}
    assert profiles["obd-basic"]["status"]=="READY"
    assert profiles["raw-can"]["status"]=="REQUIRES_VERIFIED_CONFIG"
    assert profiles["custom"]["status"]=="CUSTOM"
    assert profiles["custom"]["editable"] is True


def test_ready_profile_renders_valid_logcfg():
    result=render_profile("obd-start")
    assert result["content"]
    assert "type=obd" in result["content"]
    assert "paramid=0x0C" in result["content"]


def test_raw_can_profile_does_not_invent_config():
    result=render_profile("raw-can")
    assert result["content"]==""
    assert result["status"]=="REQUIRES_VERIFIED_CONFIG"


def test_custom_profile_is_structurally_validated_but_not_vehicle_verified():
    result=validate_custom_profile("type=obd\nprotocolid=6\n")
    assert result["valid"] is True
    assert result["status"]=="CUSTOM_VALIDATED"
    assert result["vehicle_protocol_verified"] is False
