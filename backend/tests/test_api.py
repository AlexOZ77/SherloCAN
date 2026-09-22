from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_demo_analysis_vertical_slice():
    response = client.get("/api/capture/demo-analysis")
    assert response.status_code == 200
    body = response.json()
    assert body["synthetic"] is True
    assert body["baseline"]["0x351"]["median_period_ms"] == 20.0
    assert body["anomalies"][0]["kind"] == "LONG_GAP"
    assert body["anomalies"][0]["can_id"] == "0x351"
