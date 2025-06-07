from fastapi.testclient import TestClient
import httpx

from backend.app.main import app
from backend.app.config import get_settings

client = TestClient(app)


def test_accounts_no_credentials(monkeypatch):
    monkeypatch.delenv("TASTY_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("TASTY_CLIENT_SECRET", raising=False)
    get_settings.cache_clear()
    resp = client.get("/api/tastytrade/accounts")
    assert resp.status_code == 400


def test_accounts_success(monkeypatch):
    monkeypatch.setenv("TASTY_REFRESH_TOKEN", "RTOKEN")
    monkeypatch.setenv("TASTY_CLIENT_SECRET", "SECRET")
    monkeypatch.setenv("TASTY_CLIENT_ID", "CLIENT")
    monkeypatch.setenv("TASTY_BASE_URL", "https://api.tastytrade.com")
    get_settings.cache_clear()

    class FakeResp:
        def __init__(self, data):
            self.status_code = 200
            self._data = data
        def json(self):
            return self._data

    def fake_post(url, data, timeout):
        assert data["grant_type"] == "refresh_token"
        assert data["refresh_token"] == "RTOKEN"
        assert data["client_secret"] == "SECRET"
        return FakeResp({"access_token": "abc"})

    def fake_get(url, headers, timeout):
        assert headers["Authorization"] == "Bearer abc"
        return FakeResp({"data": [{"account-number": "1234"}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    resp = client.get("/api/tastytrade/accounts")
    assert resp.status_code == 200
    assert resp.json() == {"accounts": ["1234"]}
