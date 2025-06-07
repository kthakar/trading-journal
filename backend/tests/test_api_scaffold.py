from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_profile_endpoint():
    resp = client.get("/api/profile/")
    assert resp.status_code == 200
    assert "id" in resp.json()

def test_brokerage_sync_endpoint():
    resp = client.post("/api/brokerage/sync")
    assert resp.status_code == 200
    assert resp.json().get("trades_synced") == 0
