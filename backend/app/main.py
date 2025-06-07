from fastapi import FastAPI
from .api import trades

app = FastAPI(title="Trade Blotter API")

app.include_router(trades.router, prefix="/api/trades", tags=["trades"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
