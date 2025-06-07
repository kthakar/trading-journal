from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

FAKE_PROFILE = {
    "id": "00000000-0000-0000-0000-000000000000",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "display_name": "Trader",
    "timezone": "UTC",
}

@router.get("/")
def get_profile():
    return FAKE_PROFILE

@router.put("/")
def update_profile(display_name: str | None = None, timezone: str | None = None):
    if display_name is not None:
        FAKE_PROFILE["display_name"] = display_name
    if timezone is not None:
        FAKE_PROFILE["timezone"] = timezone
    FAKE_PROFILE["updated_at"] = datetime.utcnow()
    return FAKE_PROFILE
