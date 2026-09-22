import pytest
from app.capture.j2534 import open_test

def test_open_test_rejects_missing_devices(monkeypatch):
    pytest.importorskip("J2534")
    import J2534
    monkeypatch.setattr(J2534,"get_list_j2534_devices",lambda:[])
    with pytest.raises(RuntimeError,match="No J2534 devices"):
        open_test.run_open_test()
