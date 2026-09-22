from app.capture.j2534.discovery import discover_j2534_devices

def test_discovery_is_safe_on_ci():
    result=discover_j2534_devices()
    assert isinstance(result,list)
