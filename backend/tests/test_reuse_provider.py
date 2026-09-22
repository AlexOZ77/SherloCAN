from app.capture.j2534.reuse_provider import status, list_devices

def test_optional_provider_probe_is_safe():
    s=status()
    assert isinstance(s.installed,bool)
    if not s.installed:
        assert list_devices()==[]
