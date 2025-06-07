from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def analytics_summary():
    return {"total_trades": 0, "win_rate": 0.0}

@router.get("/time-based")
def analytics_time_based():
    return {"daily": [], "monthly": []}

@router.get("/tags")
def analytics_tags():
    return {"tags": []}

@router.get("/export")
def analytics_export():
    return {"exported_at": datetime.utcnow().isoformat()}
