"""Helper functions for interacting with the Tastytrade API via OAuth2."""

from typing import List

import httpx
from fastapi import HTTPException

from ..config import get_settings


def _obtain_access_token() -> str:
    """Authenticate with Tastytrade using OAuth2 refresh token."""
    settings = get_settings()
    if not all(
        [settings.tasty_refresh_token, settings.tasty_client_secret]
    ):
        raise HTTPException(status_code=400, detail="Tastytrade credentials not configured")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": settings.tasty_refresh_token,
        "client_secret": settings.tasty_client_secret,
    }

    resp = httpx.post(f"{settings.tasty_base_url}/oauth/token", data=data, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Failed to authenticate with Tastytrade")

    token = resp.json().get("access_token")
    if not token:
        raise HTTPException(status_code=500, detail="Malformed authentication response")
    return token


def list_accounts() -> List[str]:
    """Return a list of account numbers for the authenticated user."""
    token = _obtain_access_token()
    settings = get_settings()
    headers = {"Authorization": f"Bearer {token}"}
    resp = httpx.get(f"{settings.tasty_base_url}/customers/me/accounts", headers=headers, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch accounts")

    json_data = resp.json()
    accounts = [acct.get("account-number") for acct in json_data.get("data", [])]
    return accounts
