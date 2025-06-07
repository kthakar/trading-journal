from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/accounts")
def list_accounts():
    return {"accounts": []}

@router.post("/connect")
def connect_brokerage():
    return {"auth_url": "https://example.com/auth", "state": "dummy"}

@router.get("/callback")
def oauth_callback():
    return {"status": "ok"}

@router.post("/disconnect")
def disconnect_brokerage():
    return {"status": "disconnected"}

@router.post("/sync")
def sync_brokerage():
    return {"trades_synced": 0, "last_sync_date": datetime.utcnow()}

@router.get("/positions")
def list_positions():
    return {"positions": []}
