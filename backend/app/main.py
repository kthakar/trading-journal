from fastapi import FastAPI
from .api import (
    trades,
    tastytrade,
    brokerage,
    analytics,
    journal_entries,
    tags as tags_api,
    profile,
)

app = FastAPI(title="Trade Blotter API")

app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(tastytrade.router, prefix="/api/tastytrade", tags=["tastytrade"])
app.include_router(brokerage.router, prefix="/api/brokerage", tags=["brokerage"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(journal_entries.router, prefix="/api/journal-entries", tags=["journal-entries"])
app.include_router(tags_api.router, prefix="/api/tags", tags=["tags"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
