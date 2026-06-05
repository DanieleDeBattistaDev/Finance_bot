from fastapi import FastAPI

from app.api.v1 import analysis, market, predictions, signals
from app.websocket import live

app = FastAPI(title="Finance Bot API", version="1.0.0")

app.include_router(market.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(signals.router, prefix="/api/v1")
app.include_router(live.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
