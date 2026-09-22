from app.capture.j2534.device_test import run_device_tests

def test_preflight_is_noninvasive_and_safe_on_ci():
    results=run_device_tests()
    assert isinstance(results,list)
    for r in results:
        assert r.device_opened is False
        assert r.channel_connected is False
        assert r.capture_validated is False
