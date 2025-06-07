from fastapi import FastAPI
from .api import trades, tastytrade

app = FastAPI(title="Trade Blotter API")

app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(tastytrade.router, prefix="/api/tastytrade", tags=["tastytrade"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
